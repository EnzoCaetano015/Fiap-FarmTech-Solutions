"""Regressões de aceite: entradas inválidas, concorrência e reruns da interface."""
import concurrent.futures
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from farmtech.storage import add_event, connect, history
from farmtech.services.alertas import enqueue, drain, evaluate, publish_sns
from farmtech.operations import execute
from test_services import sensor


class AcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"FARMTECH_STATE_DIR": self.temp.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def test_invalid_event_does_not_block_valid_event(self):
        add_event("sensores", "A", sensor()["data_hora"], sensor(ph=99), "bad")
        add_event("sensores", "B", sensor()["data_hora"], sensor(umidade=20), "good")
        result = enqueue(now=100)
        self.assertEqual(result["enfileirados"], 1)
        self.assertEqual(result["eventos_invalidos"], 1)
        rows = {r["id"]: r for r in history("events")}
        self.assertEqual(rows["bad"]["processed"], -1)
        self.assertTrue(rows["bad"]["error"])
        self.assertEqual(rows["good"]["processed"], 1)
        self.assertEqual(enqueue(now=101)["eventos_invalidos"], 0)

    def test_invalid_visual_payload_rejected(self):
        for payload in ({}, {"deteccoes": None}, {"deteccoes": [{"classe": "outra", "confianca": .9}]},
                        {"deteccoes": [{"classe": "folha_saudavel", "confianca": float("nan")}]},
                        {"deteccoes": [{"classe": "folha_saudavel"}]}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                evaluate("visao", payload)
        with self.assertRaises(ValueError):
            evaluate("origem-invalida", {})

    def test_all_sensor_rules_and_strong_rain(self):
        rules = dict(evaluate("sensores", sensor(umidade=34.99, ph=5.79, n=0, p=0, k=0, nivel_chuva=2)))
        self.assertEqual(set(rules), {"umidade_baixa", "ph_fora_faixa", "ausencia_n", "ausencia_p", "ausencia_k"})
        self.assertIn("adiar", rules["umidade_baixa"])
        self.assertEqual(set(dict(evaluate("sensores", sensor(umidade=55.01, ph=7.01)))), {"umidade_alta", "ph_fora_faixa"})

    def test_suppression_exact_expiration(self):
        for identity, now, expected in (("one", 100, 1), ("two", 1899.99, 0), ("three", 1900, 1)):
            add_event("sensores", "A", sensor()["data_hora"], sensor(umidade=20), identity)
            self.assertEqual(enqueue(now=now)["enfileirados"], expected)
            drain(lambda _: "test-only-id", now=now)

    def test_concurrent_workers_publish_once(self):
        for index in range(8):
            add_event("sensores", str(index), sensor()["data_hora"], sensor(umidade=20), str(index))
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda _: enqueue(), range(2)))
        self.assertEqual(len(history()), 8)
        sent = []
        def publish(body):
            sent.append(body)
            return f"test-{len(sent)}"
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda _: drain(publish), range(2)))
        self.assertEqual(len(sent), 8)
        self.assertTrue(all(r["status"] == "published" for r in history()))

    def test_sns_sdk_contract_without_external_publish(self):
        import boto3
        from botocore.stub import Stubber
        client = boto3.client("sns", region_name="us-east-1", aws_access_key_id="testing", aws_secret_access_key="testing")
        topic = "arn:aws:sns:us-east-1:123456789012:farmtech-test"
        with Stubber(client) as stub, patch("boto3.client", return_value=client), patch.dict(os.environ, {"FARMTECH_SNS_TOPIC_ARN": topic}):
            stub.add_response("publish", {"MessageId": "stub-only-message-id"}, {
                "TopicArn": topic, "Subject": "FarmTech: alerta e ação corretiva", "Message": "Somente teste local"})
            self.assertEqual(publish_sns("Somente teste local"), "stub-only-message-id")
            stub.assert_no_pending_responses()

    def test_large_history_plot_not_hidden(self):
        from dashboard.src.integrada import monitoring_frame
        add_event("sensores", "antigo", sensor()["data_hora"], sensor(), "first")
        with connect() as db:
            db.executemany("INSERT INTO events(id,source,plot,observed_at,payload,created) VALUES (?,?,?,?,?,?)",
                [(f"other-{n}", "sensores", "outro", sensor()["data_hora"], json.dumps(sensor()), 9999999999+n) for n in range(1001)])
        frame, source = monitoring_frame("antigo")
        self.assertEqual(len(frame), 1)
        self.assertIn("Histórico operacional", source)

    def test_empty_plot_fails_before_inference(self):
        result = execute("visao", image="missing.png", plot=" ")
        self.assertFalse(result["sucesso"])
        self.assertIn("Talhão", result["erro"])

    def test_corrupt_image_fails_before_loading_model(self):
        import hashlib
        from farmtech.services.visao import CLASSES
        path = Path(self.temp.name) / "corrupt.png"
        path.write_bytes(b"not an image")
        bundle = Path(self.temp.name) / "bundle"
        bundle.mkdir()
        weights = b"placeholder used only to exercise image validation"
        (bundle / "best.pt").write_bytes(weights)
        (bundle / "manifest.json").write_text(json.dumps({"classes": CLASSES, "yolo_version": "v7.0",
            "weights_sha256": hashlib.sha256(weights).hexdigest()}), encoding="utf-8")
        result = execute("visao", image=str(path), bundle=str(bundle))
        self.assertFalse(result["sucesso"])
        self.assertIn("Imagem", result["erro"])

    def test_dashboard_vision_result_survives_rerun(self):
        from farmtech.config import ROOT
        from streamlit.testing.v1 import AppTest
        from PIL import Image
        class Upload(io.BytesIO):
            name = "leaf.png"
            @property
            def size(self): return len(self.getvalue())
        buffer = io.BytesIO()
        Image.new("RGB", (16, 16), "green").save(buffer, format="PNG")
        upload = Upload(buffer.getvalue())
        annotated = Path(self.temp.name) / "anotada.jpg"
        Image.new("RGB", (16, 16), "green").save(annotated)
        record = {"id": "ui-test", "servico": "visao", "sucesso": True, "duracao_s": .01,
                  "dados": {"resultado": "Inconclusivo: nenhuma detecção", "deteccoes": []},
                  "arquivos": [str(annotated)], "erro": None}
        with patch("streamlit.file_uploader", return_value=upload), patch("dashboard.src.integrada.execute", return_value=record):
            app = AppTest.from_file(str(ROOT / "dashboard/src/dashboard.py"), default_timeout=30).run()
            app.button(key="action_visao").click().run()
            self.assertEqual(app.session_state["result_visao"], record)
            app.run()
            self.assertTrue(any("Inconclusivo" in item.value for item in app.json))
            self.assertEqual(len(app.exception), 0)

    def test_sns_rejection_remains_pending_without_leaking_error(self):
        from botocore.exceptions import ClientError
        add_event("sensores", "A", sensor()["data_hora"], sensor(umidade=20), "retry")
        enqueue(now=100)
        def rejected(_):
            raise ClientError({"Error": {"Code": "Throttled", "Message": "sensitive-detail"}}, "Publish")
        drain(rejected, now=100)
        drain(rejected, now=110)
        row = history()[0]
        self.assertEqual(row["attempts"], 2)
        self.assertEqual(row["next_attempt"], 130)
        self.assertEqual(row["error"], "Throttled")
        self.assertEqual(row["status"], "pending")

    def test_invalid_json_and_missing_sensor_field_are_isolated(self):
        add_event("sensores", "A", sensor()["data_hora"], {}, "missing")
        add_event("sensores", "A", sensor()["data_hora"], sensor(), "json")
        with connect() as db:
            db.execute("UPDATE events SET payload='not-json' WHERE id='json'")
        self.assertEqual(enqueue()["eventos_invalidos"], 2)
        self.assertTrue(all(row["processed"]==-1 for row in history("events")))

    def test_dashboard_remains_available_without_predictive_models(self):
        from farmtech.config import ROOT
        from streamlit.testing.v1 import AppTest
        with patch("dashboard.src.fase4.carregar_modelos", return_value={}):
            app = AppTest.from_file(str(ROOT / "dashboard/src/dashboard.py"), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertTrue(any("Modelos não encontrados" in w.value for w in app.warning))
            app.button(key="action_area").click().run()
            self.assertTrue(app.session_state["result_area"]["sucesso"])

    def test_database_migration_preserves_existing_events(self):
        from contextlib import closing
        import sqlite3
        path = Path(self.temp.name) / "operacao.sqlite3"
        with closing(sqlite3.connect(path)) as db:
            db.execute("CREATE TABLE events (id TEXT PRIMARY KEY,source TEXT NOT NULL,plot TEXT NOT NULL,"
                       "observed_at TEXT NOT NULL,payload TEXT NOT NULL,created REAL NOT NULL,processed INTEGER NOT NULL DEFAULT 0)")
            db.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)", ("legacy", "sensores", "A",
                       sensor()["data_hora"], json.dumps(sensor()), 100, 0))
            db.commit()
        rows = history("events")
        self.assertEqual(rows[0]["id"], "legacy")
        self.assertIsNone(rows[0]["error"])

    def test_empty_detection_output_is_inconclusive_without_alert(self):
        import contextlib
        import hashlib
        from unittest.mock import Mock
        import numpy as np
        from PIL import Image
        from farmtech.services.visao import CLASSES
        folder = Path(self.temp.name)
        bundle, runtime = folder/"bundle", folder/"runtime"
        bundle.mkdir()
        runtime.mkdir()
        (runtime/"hubconf.py").write_text("# fixture")
        weights = b"test model output is explicitly controlled"
        (bundle/"best.pt").write_bytes(weights)
        (bundle/"manifest.json").write_text(json.dumps({"classes": CLASSES, "yolo_version": "v7.0",
            "yolo_commit": "fixture", "weights_sha256": hashlib.sha256(weights).hexdigest()}))
        image = folder/"entrada.png"
        Image.new("RGB", (16,16), "green").save(image)
        results = Mock()
        results.xyxy = [Mock()]
        results.xyxy[0].cpu.return_value.tolist.return_value = []
        results.render.return_value = [np.zeros((16,16,3), dtype=np.uint8)]
        model = Mock(return_value=results)
        model.names = CLASSES
        torch = Mock()
        torch.hub.load.return_value = model
        torch.inference_mode.side_effect = contextlib.nullcontext
        with patch.dict("sys.modules", {"torch": torch}), patch.dict(os.environ, {"FARMTECH_YOLO_RUNTIME": str(runtime)}), \
                patch("subprocess.check_output", return_value="fixture"):
            record = execute("visao", image=str(image), bundle=str(bundle))
        self.assertTrue(record["sucesso"], record["erro"])
        self.assertEqual(record["dados"]["deteccoes"], [])
        self.assertIn("Inconclusivo", record["dados"]["resultado"])
        self.assertEqual(enqueue()["enfileirados"], 0)

    def test_legacy_entrypoints_accept_help_without_side_effects(self):
        import subprocess
        import sys
        from farmtech.config import ROOT
        for relative in ("database/ingestao_iot_sqlite.py", "dashboard/src/importar_csv_oracle.py",
                         "api-clima/clima.py", "ml/treinar_modelos.py"):
            with self.subTest(entrypoint=relative):
                process = subprocess.run([sys.executable, str(ROOT/relative), "--help"],
                    cwd=self.temp.name, capture_output=True, encoding="utf-8", timeout=20)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertIn("usage:", process.stdout)
        self.assertEqual(history("events"), [])


if __name__ == "__main__":
    unittest.main()
