from ...config import ROOT


def train():
    from .training import treinar
    metrics = treinar()
    return {"dados": {"metricas": metrics.to_dict(orient="records"), "dados_sinteticos": True},
            "arquivos": [str(ROOT / "data/sensores/treino_sintetico.csv"),
                         str(ROOT / "relatorios/preditivo/metricas_modelos.csv"),
                         *[str(p) for p in (ROOT / "models/preditivo").glob("modelo_*")]]}
