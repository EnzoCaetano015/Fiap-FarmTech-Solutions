"""Teste funcional dos botões e tolerância a serviço externo ausente."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class DashboardTest(unittest.TestCase):
    def test_monitor_uses_operational_readings_of_selected_plot(self):
        from dashboard.interface import monitoring_frame
        from farmtech.storage import add_event
        from test_services import sensor
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"FARMTECH_STATE_DIR": directory}):
            row = sensor(umidade=23)
            add_event("sensores", "A", row["data_hora"], row, "A1")
            add_event("sensores", "B", row["data_hora"], row, "B1")
            frame, source = monitoring_frame("A")
            self.assertEqual(len(frame), 1)
            self.assertEqual(float(frame.iloc[0]["umidade"]), 23)
            self.assertIn("Histórico operacional", source)
            _, fallback = monitoring_frame("sem-leituras")
            self.assertIn("CSV histórico", fallback)

    def test_actions_share_service_contract(self):
        from streamlit.testing.v1 import AppTest
        from farmtech.config import ROOT
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"FARMTECH_STATE_DIR": directory}):
            app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=30).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.tabs), 6)
            app.button(key="action_area").click().run()
            result = app.session_state["result_area"]
            self.assertTrue(result["sucesso"])
            self.assertAlmostEqual(result["dados"]["area_ha"], 1)
            self.assertTrue(Path(result["arquivos"][0]).exists())
            with patch("farmtech.services.oracle.open_connection", side_effect=RuntimeError("Oracle indisponível")):
                app.button(key="action_oracle-importar").click().run()
            self.assertFalse(app.session_state["result_oracle-importar"]["sucesso"])
            self.assertEqual(len(app.exception), 0)
