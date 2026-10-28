"""Importação incremental, serializada e atômica na tabela existente."""
import os
from ...config import initialize_environment
from ..iot import read_rows
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP


def open_connection():
    initialize_environment()
    import oracledb
    values = [os.getenv(k) for k in ("ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN")]
    if not all(values):
        raise RuntimeError("Configure ORACLE_USER, ORACLE_PASSWORD e ORACLE_DSN no .env")
    return oracledb.connect(user=values[0], password=values[1], dsn=values[2], tcp_connect_timeout=10)


def import_csv(csv_path=None, connection_factory=None):
    rows = read_rows(csv_path)
    connection = (connection_factory or open_connection)()
    inserted = 0
    try:
        with connection.cursor() as cursor:
            # A tabela antiga não tem sequence/identity. O lock protege MAX+1 e a deduplicação.
            cursor.execute("LOCK TABLE FARMTECH_SENSOR_LEITURA IN EXCLUSIVE MODE WAIT 10")
            for row in rows:
                stamp = datetime.fromisoformat(row["data_hora"]).astimezone(timezone(timedelta(hours=-3))).replace(tzinfo=None)
                numeric = [Decimal(str(row[key])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                           for key in ("umidade", "temperatura", "ph")]
                values = (stamp, *numeric,
                          row["n"], row["p"], row["k"], row["nivel_chuva"], row["status_irrigacao"])
                cursor.execute("""SELECT COUNT(*) FROM FARMTECH_SENSOR_LEITURA
                    WHERE DATA_HORA=:1 AND UMIDADE=:2 AND TEMPERATURA=:3 AND PH=:4
                    AND N=:5 AND P=:6 AND K=:7 AND NIVEL_CHUVA=:8 AND STATUS_IRRIGACAO=:9""", values)
                if cursor.fetchone()[0]:
                    continue
                cursor.execute("SELECT NVL(MAX(ID_LEITURA),0)+1 FROM FARMTECH_SENSOR_LEITURA")
                identifier = cursor.fetchone()[0]
                cursor.execute("""INSERT INTO FARMTECH_SENSOR_LEITURA
                    (ID_LEITURA,DATA_HORA,UMIDADE,TEMPERATURA,PH,N,P,K,NIVEL_CHUVA,STATUS_IRRIGACAO,SUGESTAO)
                    VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)""",
                    (identifier, *values, row.get("sugestao", "")))
                inserted += 1
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {"dados": {"inseridos": inserted, "existentes": len(rows) - inserted}}


def query(limit=100):
    limit = int(limit)
    if not 1 <= limit <= 1000:
        raise ValueError("Limite entre 1 e 1000")
    connection = open_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM (SELECT * FROM FARMTECH_SENSOR_LEITURA "
                           "ORDER BY DATA_HORA DESC) WHERE ROWNUM <= :1", (limit,))
            columns = [c[0].lower() for c in cursor.description]
            records = [dict(zip(columns, [v.isoformat() if isinstance(v, datetime) else v for v in row]))
                       for row in cursor.fetchall()]
    finally:
        connection.close()
    return {"dados": records}
