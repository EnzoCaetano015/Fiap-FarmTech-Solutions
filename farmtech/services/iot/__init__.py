import csv
import math
import time
from datetime import datetime, timezone
from ...config import ROOT
from ...storage import add_event


def validate(row):
    data = dict(row)
    for key, low, high in [("umidade", 0, 100), ("temperatura", -80, 100), ("ph", 0, 14),
                           ("n", 0, 1), ("p", 0, 1), ("k", 0, 1), ("nivel_chuva", 0, 2)]:
        v = float(data[key])
        if not math.isfinite(v) or not low <= v <= high:
            raise ValueError(f"Leitura inválida: {key}")
        if key in {"n", "p", "k", "nivel_chuva"}:
            if not v.is_integer():
                raise ValueError(f"Leitura discreta inválida: {key}")
            v = int(v)
        data[key] = v
    stamp = str(data["data_hora"])
    parsed = datetime.fromisoformat(stamp)
    if parsed.tzinfo is None:
        # CSV histórico foi produzido no horário de São Paulo (UTC-03).
        stamp += "-03:00"
    data["data_hora"] = stamp
    if data.get("status_irrigacao") not in {"LIGADA", "DESLIGADA"}:
        raise ValueError("Status de irrigação inválido")
    return data


def read_rows(csv_path=None):
    with open(csv_path or ROOT / "data/sensores_fase2.csv", encoding="utf-8-sig", newline="") as f:
        rows = [validate(row) for row in csv.DictReader(f)]
    if not rows:
        raise ValueError("CSV sem leituras")
    return rows


def replay(csv_path=None, plot="talhao-demo", interval=1, live_time=False):
    interval = float(interval)
    if not math.isfinite(interval) or interval < 0 or interval > 60:
        raise ValueError("Intervalo deve estar entre 0 e 60 segundos")
    rows = read_rows(csv_path)  # Validar tudo antes de inserir parcialmente.
    ids = []
    for i, row in enumerate(rows):
        payload = {**row, "simulado": True}
        stamp = datetime.now(timezone.utc).isoformat() if live_time else row["data_hora"]
        if live_time:
            payload["data_hora_original"] = row["data_hora"]
            payload["data_hora"] = stamp
        ids.append(add_event("sensores", plot, stamp, payload))
        if interval and i < len(rows) - 1:
            time.sleep(interval)
    return {"dados": {"eventos": ids, "leituras": len(ids), "simulado": True,
                       "horario": "atual" if live_time else "histórico"}}
