"""Contrato único de execução para terminal e dashboard."""
import contextlib
import importlib
import io
import json
import time
import uuid
from .config import initialize_environment
from .storage import connect

SERVICES = {
    "area": ("agronomia", "area"), "analise-r": ("agronomia", "analysis_r"),
    "clima": ("agronomia", "weather"), "iot": ("iot", "replay"),
    "oracle-importar": ("oracle", "import_csv"), "oracle-consultar": ("oracle", "query"),
    "treinar": ("preditivo", "train"), "visao": ("visao", "infer"),
    "alertas": ("alertas", "get_history"), "monitor-uma-vez": ("alertas", "monitor_once"),
}


def execute(service, **parameters):
    initialize_environment()
    started = time.perf_counter()
    identifier = uuid.uuid4().hex
    output = io.StringIO()
    try:
        module, function = SERVICES[service]
        handler = getattr(importlib.import_module(f"farmtech.services.{module}"), function)
        with contextlib.redirect_stdout(output):
            result = handler(**parameters)
        record = {"id": identifier, "servico": service, "sucesso": True,
                  "dados": result.get("dados"), "arquivos": result.get("arquivos", []), "erro": None}
    except Exception as exc:
        # Evitar serializar exceções de terceiros contendo DSNs, senhas ou credenciais.
        safe = str(exc) if isinstance(exc, (ValueError, RuntimeError, FileNotFoundError)) else (
            f"{type(exc).__name__}: serviço indisponível; confira dependências, conexão e configuração.")
        record = {"id": identifier, "servico": service, "sucesso": False,
                  "dados": None, "arquivos": [], "erro": safe}
    record["duracao_s"] = round(time.perf_counter() - started, 4)
    record["saida"] = output.getvalue()
    with connect() as db:
        db.execute("INSERT INTO executions VALUES (?,?,?,?)", (
            identifier, service, time.time(), json.dumps(record, ensure_ascii=False, default=str)))
    return record
