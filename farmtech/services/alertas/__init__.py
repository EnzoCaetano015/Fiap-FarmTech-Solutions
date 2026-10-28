"""Regras demonstrativas, outbox persistente e publicação SNS."""
import json
import logging
import math
import os
import time
import uuid
from ...storage import connect, history

LOG = logging.getLogger(__name__)


def evaluate(source, payload):
    if not isinstance(payload, dict):
        raise ValueError("Dados de evento inválidos")
    rules = []
    if source == "sensores":
        from ..iot import validate
        data = validate(payload)
        if data["umidade"] < 35:
            action = ("Verificar o talhão e adiar irrigação: chuva forte prevista."
                      if data["nivel_chuva"] == 2 else "Verificar o talhão e avaliar irrigação para elevar a umidade.")
            rules.append(("umidade_baixa", action))
        elif data["umidade"] > 55:
            rules.append(("umidade_alta", "Manter irrigação desligada e verificar drenagem do talhão."))
        if data["ph"] < 5.8 or data["ph"] > 7:
            rules.append(("ph_fora_faixa", "Conferir medição e avaliar correção do solo com responsável técnico."))
        for nutrient in ("n", "p", "k"):
            if data[nutrient] == 0:
                rules.append((f"ausencia_{nutrient}", f"Verificar disponibilidade de {nutrient.upper()} e avaliar manejo nutricional."))
    elif source == "visao":
        detections = payload.get("deteccoes")
        if not isinstance(detections, list):
            raise ValueError("Lista de detecções inválida")
        for detection in detections:
            if not isinstance(detection, dict) or detection.get("classe") not in {
                    "folha_saudavel", "folha_com_sinais_de_doenca"}:
                raise ValueError("Classe visual inválida")
            try:
                confidence = float(detection["confianca"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("Confiança visual inválida") from exc
            if not math.isfinite(confidence) or not 0 <= confidence <= 1:
                raise ValueError("Confiança visual inválida")
            if detection["classe"] == "folha_com_sinais_de_doenca" and confidence >= .5:
                rules.append(("sinais_doenca", "Registrar a imagem e inspecionar as plantas do talhão com responsável técnico."))
                # Validar todas as detecções, mesmo depois de encontrar a condição.
        rules = list(dict(rules).items())
    else:
        raise ValueError("Origem de evento inválida")
    return rules


def enqueue(now=None):
    now = time.time() if now is None else now
    queued = suppressed = invalid = 0
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        events = db.execute("SELECT * FROM events WHERE processed=0 ORDER BY created,id LIMIT 100").fetchall()
        for event in events:
            try:
                payload = json.loads(event["payload"])
                rules = evaluate(event["source"], payload)
            except (ValueError, TypeError, KeyError, OverflowError) as exc:
                # Um registro inválido não pode impedir o processamento dos demais.
                # Conservar o registro para inspeção no histórico da dashboard.
                db.execute("UPDATE events SET processed=-1,error=? WHERE id=?",
                           (f"{type(exc).__name__}: evento inválido; revise os dados observados", event["id"]))
                LOG.warning("Evento inválido isolado: %s (%s)", event["id"], type(exc).__name__)
                invalid += 1
                continue
            active = set()
            for previous in db.execute("SELECT rules FROM outbox WHERE plot=? AND "
                                       "((status='published' AND updated>?) OR status IN ('pending','publishing'))",
                                       (event["plot"], now - 1800)):
                active.update(json.loads(previous["rules"]))
            fresh = [(code, action) for code, action in rules if code not in active]
            suppressed += len(rules) - len(fresh)
            if fresh:
                label = "SIMULAÇÃO" if payload.get("simulado") else "MONITORAMENTO"
                body = (f"FarmTech Solutions — {label}\nTalhão: {event['plot']}\n"
                        f"Origem: {event['source']}\nHorário observado: {event['observed_at']}\n"
                        f"Evento: {event['id']}\nDados: {json.dumps(payload, ensure_ascii=False)}\n\n"
                        + "\n".join(f"{code}: {action}" for code, action in fresh))
                db.execute("INSERT INTO outbox(id,event_id,plot,rules,body,status,created,updated) "
                           "VALUES (?,?,?,?,?,'pending',?,?)", (uuid.uuid4().hex, event["id"], event["plot"],
                           json.dumps([code for code, _ in fresh]), body, now, now))
                queued += 1
            db.execute("UPDATE events SET processed=1 WHERE id=?", (event["id"],))
    return {"enfileirados": queued, "condicoes_suprimidas": suppressed, "eventos_invalidos": invalid}


def publish_sns(body):
    topic = os.getenv("FARMTECH_SNS_TOPIC_ARN", "")
    if not topic.startswith("arn:aws:sns:") or topic.endswith(".fifo"):
        raise RuntimeError("Configure FARMTECH_SNS_TOPIC_ARN com um tópico Standard")
    import boto3
    from botocore.config import Config
    region = topic.split(":")[3]
    client = boto3.client("sns", region_name=region,
                          config=Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 2}))
    result = client.publish(TopicArn=topic, Subject="FarmTech: alerta e ação corretiva", Message=body)
    return result["MessageId"]


def drain(publisher=None, now=None):
    publisher = publisher or publish_sns
    published = failed = 0
    # Um lease permite recuperar publicações interrompidas por reinício.
    # SNS Standard é at-least-once: falha entre publish e commit pode duplicar e-mail.
    for _ in range(100):
        current = time.time() if now is None else now
        with connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE outbox SET status='pending' WHERE status='publishing' AND updated<?", (current-120,))
            row = db.execute("SELECT * FROM outbox WHERE status='pending' AND next_attempt<=? "
                             "ORDER BY created,id LIMIT 1", (current,)).fetchone()
            if row is None:
                break
            db.execute("UPDATE outbox SET status='publishing',updated=?,attempts=attempts+1 WHERE id=?", (current, row["id"]))
        try:
            message_id = publisher(row["body"])
            if not message_id:
                raise RuntimeError("Publicação sem MessageId")
        except Exception as exc:
            failed += 1
            attempt = row["attempts"] + 1
            delay = min(3600, 10 * 2 ** min(attempt - 1, 9))
            code = getattr(exc, "response", {}).get("Error", {}).get("Code", type(exc).__name__)
            with connect() as db:
                db.execute("UPDATE outbox SET status='pending',updated=?,next_attempt=?,error=? WHERE id=?",
                           (current, current + delay, str(code)[:200], row["id"]))
            LOG.warning("Publicação pendente %s: %s", row["id"], code)
        else:
            published += 1
            with connect() as db:
                db.execute("UPDATE outbox SET status='published',updated=?,message_id=?,error=NULL WHERE id=?",
                           (current, str(message_id), row["id"]))
    return {"publicados_sns": published, "falhas_pendentes": failed}


def monitor_once():
    return {"dados": {**enqueue(), **drain()}}


def monitor(interval=10):
    from ...config import initialize_environment
    initialize_environment()
    interval = float(interval)
    if not math.isfinite(interval) or interval < 1:
        raise ValueError("Intervalo do monitor deve ser de pelo menos 1 segundo")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    while True:
        try:
            LOG.info("Ciclo: %s", monitor_once()["dados"])
        except Exception:
            LOG.exception("Falha no ciclo; o monitor tentará novamente")
        time.sleep(interval)


def get_history():
    return {"dados": history()}
