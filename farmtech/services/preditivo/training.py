from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "sensores"
MODELS_DIR = BASE_DIR / "models" / "preditivo"
RELATORIOS_DIR = BASE_DIR / "relatorios" / "preditivo"

FEATURES = ["umidade", "temperatura", "ph", "n", "p", "k", "nivel_chuva", "irrigacao_ligada"]
TARGETS = ["umidade_prevista", "ph_previsto", "produtividade_estimada"]


def carregar_base_sensores() -> pd.DataFrame:
    caminho = DATA_DIR / "leituras.csv"
    if not caminho.exists():
        raise FileNotFoundError(f"Base de sensores não encontrada: {caminho}")
    df = pd.read_csv(caminho)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    df["irrigacao_ligada"] = (df["status_irrigacao"].str.upper() == "LIGADA").astype(int)
    return df


def gerar_dataset_ml(df_base: pd.DataFrame, amostras_por_linha: int = 25) -> pd.DataFrame:
    """
    Como a base original de sensores é curta para ML, este método simula leituras
    adicionais preservando a lógica agrícola: umidade, temperatura, pH, NPK,
    chuva e irrigação influenciam as variáveis-alvo.
    """
    rng = np.random.default_rng(42)
    registros = []

    for _, linha in df_base.iterrows():
        for _ in range(amostras_por_linha):
            umidade = float(np.clip(linha["umidade"] + rng.normal(0, 4), 15, 80))
            temperatura = float(np.clip(linha["temperatura"] + rng.normal(0, 2), 15, 40))
            ph = float(np.clip(linha["ph"] + rng.normal(0, 0.35), 4.5, 8.5))
            n = int(linha["n"] if rng.random() > 0.10 else 1 - int(linha["n"]))
            p = int(linha["p"] if rng.random() > 0.10 else 1 - int(linha["p"]))
            k = int(linha["k"] if rng.random() > 0.10 else 1 - int(linha["k"]))
            nivel_chuva = int(np.clip(linha["nivel_chuva"] + rng.integers(-1, 2), 0, 2))
            irrigacao_ligada = int(linha["irrigacao_ligada"])

            umidade_prevista = (
                umidade
                + 8.0 * irrigacao_ligada
                + 5.0 * nivel_chuva
                - 0.35 * max(0, temperatura - 26)
                + rng.normal(0, 2)
            )
            umidade_prevista = float(np.clip(umidade_prevista, 10, 90))

            ph_previsto = (
                ph
                + 0.08 * n
                + 0.05 * p
                + 0.04 * k
                - 0.03 * nivel_chuva
                + rng.normal(0, 0.12)
            )
            ph_previsto = float(np.clip(ph_previsto, 4.0, 9.0))

            penalidade_umidade = abs(umidade_prevista - 45) * 0.85
            penalidade_ph = abs(ph_previsto - 6.5) * 9.0
            bonus_npk = (n + p + k) * 4.0
            produtividade_estimada = 70 + bonus_npk - penalidade_umidade - penalidade_ph - abs(temperatura - 26) * 0.7
            produtividade_estimada += rng.normal(0, 4)
            produtividade_estimada = float(np.clip(produtividade_estimada, 20, 100))

            registros.append(
                {
                    "data_hora": linha["data_hora"],
                    "umidade": round(umidade, 2),
                    "temperatura": round(temperatura, 2),
                    "ph": round(ph, 2),
                    "n": n,
                    "p": p,
                    "k": k,
                    "nivel_chuva": nivel_chuva,
                    "status_irrigacao": "LIGADA" if irrigacao_ligada else "DESLIGADA",
                    "irrigacao_ligada": irrigacao_ligada,
                    "umidade_prevista": round(umidade_prevista, 2),
                    "ph_previsto": round(ph_previsto, 2),
                    "produtividade_estimada": round(produtividade_estimada, 2),
                }
            )

    df_ml = pd.DataFrame(registros)
    caminho_ml = DATA_DIR / "treino_sintetico.csv"
    df_ml.to_csv(caminho_ml, index=False)
    return df_ml


def avaliar_modelo(nome: str, modelo, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    pred = modelo.predict(X_test)
    mse = mean_squared_error(y_test, pred)
    return {
        "modelo": nome,
        "MAE": round(mean_absolute_error(y_test, pred), 4),
        "MSE": round(mse, 4),
        "RMSE": round(float(np.sqrt(mse)), 4),
        "R2": round(r2_score(y_test, pred), 4),
    }


def treinar() -> pd.DataFrame:
    MODELS_DIR.mkdir(exist_ok=True)
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

    df_base = carregar_base_sensores()
    df_ml = gerar_dataset_ml(df_base)

    X = df_ml[FEATURES]
    metricas = []

    for target in TARGETS:
        y = df_ml[target]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )

        modelos = {
            "regressao_linear": Pipeline(
                steps=[("scaler", StandardScaler()), ("model", LinearRegression())]
            ),
            "random_forest": RandomForestRegressor(
                n_estimators=200, random_state=42, max_depth=8
            ),
        }

        melhor_nome = None
        melhor_modelo = None
        melhor_r2 = -999.0

        for nome, modelo in modelos.items():
            modelo.fit(X_train, y_train)
            resultado = avaliar_modelo(nome, modelo, X_test, y_test)
            resultado["alvo"] = target
            metricas.append(resultado)

            if resultado["R2"] > melhor_r2:
                melhor_r2 = resultado["R2"]
                melhor_nome = nome
                melhor_modelo = modelo

        joblib.dump(melhor_modelo, MODELS_DIR / f"modelo_{target}.joblib")
        (MODELS_DIR / f"modelo_{target}_meta.json").write_text(
            json.dumps({"alvo": target, "modelo": melhor_nome, "features": FEATURES}, indent=2),
            encoding="utf-8",
        )

    df_metricas = pd.DataFrame(metricas)
    df_metricas = df_metricas[["alvo", "modelo", "MAE", "MSE", "RMSE", "R2"]]
    df_metricas.to_csv(RELATORIOS_DIR / "metricas_modelos.csv", index=False)
    print("Treinamento concluído.")
    print(f"Dataset ML salvo em: {DATA_DIR / 'treino_sintetico.csv'}")
    print(f"Métricas salvas em: {RELATORIOS_DIR / 'metricas_modelos.csv'}")
    print(df_metricas)
    return df_metricas


if __name__ == "__main__":
    treinar()
