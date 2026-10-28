from ...config import ROOT


def train():
    from .training import treinar
    metrics = treinar()
    return {"dados": {"metricas": metrics.to_dict(orient="records"), "dados_sinteticos": True},
            "arquivos": [str(ROOT / "data/sensores_fase4_ml.csv"),
                         str(ROOT / "relatorios/fase4/metricas_modelos.csv"),
                         *[str(p) for p in (ROOT / "models").glob("modelo_*")]]}
