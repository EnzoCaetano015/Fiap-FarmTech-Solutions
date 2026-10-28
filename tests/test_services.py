import csv
import json
import math
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

from farmtech.operations import execute
from farmtech.services.inicial import area, weather, analysis_r
from farmtech.services.iot import replay, validate
from farmtech.services.alertas import evaluate, enqueue, drain
from farmtech.storage import add_event, connect, history


def sensor(**changes):
    return {"data_hora": "2026-10-27T12:00:00-03:00", "umidade": 45,
            "temperatura": 25, "ph": 6.5, "n": 1, "p": 1, "k": 1,
            "nivel_chuva": 0, "status_irrigacao": "DESLIGADA", "simulado": True, **changes}


class ServicesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"FARMTECH_STATE_DIR": self.temp.name})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def event(self, identity, **values):
        data = sensor(**values)
        return add_event("sensores", "A", data["data_hora"], data, identity)

    def test_rectangle_and_csv(self):
        result = area(length=100, width=200, dose=12)
        self.assertEqual(result["dados"]["area_ha"], 2)
        self.assertEqual(result["dados"]["insumo_kg"], 24)
        self.assertTrue(Path(result["arquivos"][0]).is_file())

    def test_circle(self):
        self.assertAlmostEqual(area("circulo", radius=10)["dados"]["area_m2"], 100*math.pi)

    def test_cli_success_contract(self):
        result = subprocess.run([sys.executable, "-m", "farmtech", "area", "--length", "100",
                                 "--width", "200", "--dose", "12"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["dados"]["insumo_kg"], 24)

    def test_cli_failure_contract(self):
        result = subprocess.run([sys.executable, "-m", "farmtech", "area", "--length", "-1"],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["sucesso"])

    def test_configuration_fills_initially_blank(self):
        from farmtech.config import initialize_environment
        with patch.dict(os.environ, {"ORACLE_USER": ""}), patch("dotenv.dotenv_values", return_value={"ORACLE_USER": "teste"}):
            initialize_environment()
            self.assertEqual(os.environ["ORACLE_USER"], "teste")

    def test_configuration_preserves_real_environment(self):
        from farmtech.config import initialize_environment
        with patch.dict(os.environ, {"ORACLE_USER": "ambiente"}), patch("dotenv.dotenv_values", return_value={"ORACLE_USER": "arquivo"}):
            initialize_environment()
            self.assertEqual(os.environ["ORACLE_USER"], "ambiente")

    def test_bad_area(self):
        for params in ({"length": -1}, {"dose": float("nan")}, {"radius": 0, "shape": "circulo"}, {"length": float("inf")}):
            with self.assertRaises(ValueError):
                area(**params)

    def test_sensor_validation(self):
        for change in ({"ph": 15}, {"n": .5}, {"umidade": float("nan")},
                       {"data_hora": "ontem"}, {"nivel_chuva": 3}, {"status_irrigacao": "INVALIDO"}):
            with self.assertRaises(ValueError):
                validate(sensor(**change))

    def test_rule_boundaries(self):
        for humidity in (35, 55):
            for ph in (5.8, 7):
                self.assertEqual(evaluate("sensores", sensor(umidade=humidity, ph=ph)), [])

    def test_rain_changes_action(self):
        rules = evaluate("sensores", sensor(umidade=34, nivel_chuva=2))
        self.assertIn("adiar", rules[0][1])

    def test_vision_threshold(self):
        for confidence, count in ((.49, 0), (.5, 1), (.9, 1)):
            self.assertEqual(len(evaluate("visao", {"deteccoes": [{"classe": "folha_com_sinais_de_doenca", "confianca": confidence}]})), count)
        self.assertEqual(evaluate("visao", {"deteccoes": []}), [])

    def test_event_idempotence(self):
        self.event("one", umidade=30)
        self.event("one", umidade=30)
        self.assertEqual(len(history("events")), 1)

    def test_consolidate_suppress_and_restart(self):
        self.event("one", umidade=30, ph=5, n=0)
        self.event("two", umidade=31, ph=5.1, n=0)
        self.assertEqual(enqueue(now=100)["enfileirados"], 1)
        outbox = history()[0]
        self.assertEqual(len(json.loads(outbox["rules"])), 3)
        self.assertEqual(drain(lambda body: "sns-id", now=100)["publicados_sns"], 1)
        self.assertEqual(history()[0]["message_id"], "sns-id")
        self.assertEqual(drain(lambda body: self.fail("Duplicou publicação"), now=101)["publicados_sns"], 0)
        self.event("three", umidade=32)
        self.assertEqual(enqueue(now=101)["enfileirados"], 0)
        self.event("four", umidade=32)
        self.assertEqual(enqueue(now=1901)["enfileirados"], 1)

    def test_new_rule_not_suppressed(self):
        self.event("one", umidade=30)
        enqueue(now=100)
        drain(lambda _: "id", now=100)
        self.event("two", umidade=30, k=0)
        enqueue(now=110)
        rules = [json.loads(row["rules"]) for row in history()]
        self.assertIn(["ausencia_k"], rules)

    def test_transient_failure_backoff(self):
        self.event("one", umidade=30)
        enqueue(now=100)
        def failure(_):
            raise TimeoutError("transient")
        self.assertEqual(drain(failure, now=100)["falhas_pendentes"], 1)
        self.assertEqual(history()[0]["status"], "pending")
        self.assertEqual(drain(lambda _: "id", now=109)["publicados_sns"], 0)
        self.assertEqual(drain(lambda _: "id", now=110)["publicados_sns"], 1)

    def test_interrupted_publish_recovers(self):
        self.event("one", umidade=30)
        enqueue(now=100)
        with connect() as db:
            db.execute("UPDATE outbox SET status='publishing',updated=100")
        self.assertEqual(drain(lambda _: "id", now=221)["publicados_sns"], 1)

    def test_plot_isolation(self):
        self.event("one", umidade=30)
        add_event("sensores", "B", sensor()["data_hora"], sensor(umidade=30), "two")
        self.assertEqual(enqueue(now=100)["enfileirados"], 2)

    def test_replay_repeat_idempotence(self):
        first = replay(interval=0)["dados"]
        replay(interval=0)
        self.assertEqual(len(history("events")), first["leituras"])
        self.assertTrue(first["simulado"])

    def test_service_error_does_not_crash(self):
        record = execute("visao", image="missing.jpg", bundle=self.temp.name)
        self.assertFalse(record["sucesso"])
        self.assertIn("Detector agrícola indisponível", record["erro"])
        self.assertTrue(execute("area", length=10, width=10)["sucesso"])

    def test_weather_unavailable_not_zero(self):
        import requests
        with patch("requests.get", side_effect=requests.Timeout):
            with self.assertRaisesRegex(RuntimeError, "Previsão indisponível"):
                weather()

    def test_weather_levels(self):
        for rain, probability, level in ((0, 20, 0), (1, 40, 1), (6, 80, 2)):
            response = Mock()
            response.json.return_value = {"hourly": {"rain": [rain], "precipitation_probability": [probability]}}
            with patch("requests.get", return_value=response):
                self.assertEqual(weather()["dados"]["nivel_chuva"], level)

    def test_missing_r(self):
        with patch.dict(os.environ, {"FARMTECH_RSCRIPT": ""}), patch("shutil.which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Rscript indisponível"):
                analysis_r()

    def test_oracle_incremental_transaction(self):
        from farmtech.services.oracle import import_csv
        class Cursor:
            def __init__(self):
                self.records = []
                self.last = None
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, sql, params=()):
                if "DELETE" in sql:
                    raise AssertionError("Não apagar tabela")
                if "COUNT" in sql:
                    self.last = (int(params in self.records),)
                elif "MAX" in sql:
                    self.last = (len(self.records)+1,)
                elif "INSERT" in sql:
                    self.records.append(params[1:-1])
            def fetchone(self): return self.last
        cursor = Cursor()
        conn = Mock()
        conn.cursor.return_value = cursor
        first = import_csv(connection_factory=lambda: conn)["dados"]
        second = import_csv(connection_factory=lambda: conn)["dados"]
        self.assertGreater(first["inseridos"], 0)
        self.assertEqual(second["inseridos"], 0)
        conn.rollback.assert_not_called()
        self.assertEqual(conn.commit.call_count, 2)
        with patch("farmtech.services.oracle.read_rows", return_value=[sensor(umidade=32.501), sensor(umidade=32.504)]):
            rounded = import_csv(connection_factory=lambda: conn)["dados"]
        self.assertEqual(rounded, {"inseridos": 1, "existentes": 1})

    def test_oracle_rollback(self):
        from farmtech.services.oracle import import_csv
        conn = Mock()
        conn.cursor.side_effect = RuntimeError("DB indisponível")
        with self.assertRaises(RuntimeError):
            import_csv(connection_factory=lambda: conn)
        conn.rollback.assert_called_once()
        conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
