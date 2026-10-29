"""Estado operacional SQLite, separado da persistência estruturada Oracle."""
import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from .config import state_dir


@contextmanager
def connect():
    db = sqlite3.connect(state_dir() / "operacao.sqlite3", timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY, source TEXT NOT NULL, plot TEXT NOT NULL,
            observed_at TEXT NOT NULL, payload TEXT NOT NULL,
            created REAL NOT NULL, processed INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS outbox (
            id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES events(id),
            plot TEXT NOT NULL, rules TEXT NOT NULL, body TEXT NOT NULL,
            status TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0, next_attempt REAL NOT NULL DEFAULT 0,
            message_id TEXT, error TEXT);
        CREATE TABLE IF NOT EXISTS executions (
            id TEXT PRIMARY KEY, service TEXT NOT NULL, created REAL NOT NULL,
            result TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_events_pending ON events(processed, created);
        CREATE INDEX IF NOT EXISTS idx_outbox_due ON outbox(status, next_attempt);
    """)
    # Migração compatível com o histórico já criado nas versões anteriores.
    if "error" not in {row[1] for row in db.execute("PRAGMA table_info(events)")}:
        try:
            db.execute("ALTER TABLE events ADD COLUMN error TEXT")
            db.commit()
        except sqlite3.OperationalError:
            # Outro processo pode ter aplicado a mesma migração neste instante.
            if "error" not in {row[1] for row in db.execute("PRAGMA table_info(events)")}:
                db.close()
                raise
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def add_event(source, plot, observed_at, payload, event_id=None):
    if source not in {"sensores", "visao"}:
        raise ValueError("Origem de evento inválida")
    if not str(plot).strip():
        raise ValueError("Talhão é obrigatório")
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False)
    event_id = event_id or hashlib.sha256(
        f"{source}|{plot}|{observed_at}|{serialized}".encode()).hexdigest()
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO events(id,source,plot,observed_at,payload,created) "
                   "VALUES (?,?,?,?,?,?)", (event_id, source, plot, observed_at, serialized, time.time()))
    return event_id


def history(table="outbox", limit=100, *, plot=None, source=None):
    if table not in {"outbox", "events", "executions"}:
        raise ValueError("Tabela inválida")
    limit = int(limit)
    if not 1 <= limit <= 10000:
        raise ValueError("Limite do histórico entre 1 e 10000")
    if source is not None and table != "events":
        raise ValueError("Filtro de origem disponível somente para eventos")
    if plot is not None and table == "executions":
        raise ValueError("Execuções não possuem filtro por talhão")
    filters, parameters = [], []
    for column, value in (("plot", plot), ("source", source)):
        if value is not None:
            filters.append(f"{column}=?")
            parameters.append(value)
    where = " WHERE " + " AND ".join(filters) if filters else ""
    with connect() as db:
        return [dict(row) for row in db.execute(
            f"SELECT * FROM {table}{where} ORDER BY created DESC,id DESC LIMIT ?", (*parameters, limit))]
