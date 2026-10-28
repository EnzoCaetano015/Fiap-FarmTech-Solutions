from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from ml.recomendador import sugerir_manejo  # noqa: E402

FEATURES = ["umidade", "temperatura", "ph", "n", "p", "k", "nivel_chuva", "irrigacao_ligada"]
TARGETS = ["umidade_prevista", "ph_previsto", "produtividade_estimada"]


def carregar_dados_fase3() -> pd.DataFrame:
    caminho_csv = BASE_DIR / "data" / "sensores_fase2.csv"
    df = pd.read_csv(caminho_csv)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    df["irrigacao_ligada"] = (df["status_irrigacao"].str.upper() == "LIGADA").astype(int)
    return df


def carregar_dados_ml() -> pd.DataFrame | None:
    caminho_csv = BASE_DIR / "data" / "sensores_fase4_ml.csv"
    if not caminho_csv.exists():
        return None
    df = pd.read_csv(caminho_csv)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    return df


def carregar_metricas() -> pd.DataFrame | None:
    caminho = BASE_DIR / "relatorios" / "fase4" / "metricas_modelos.csv"
    if not caminho.exists():
        return None
    return pd.read_csv(caminho)


@st.cache_resource
def carregar_modelos() -> dict:
    modelos = {}
    for target in TARGETS:
        caminho = BASE_DIR / "models" / f"modelo_{target}.joblib"
        if caminho.exists():
            modelos[target] = joblib.load(caminho)
    return modelos


def render_monitoramento(df: pd.DataFrame) -> None:
    st.subheader("Monitoramento de sensores - Fase 3")
    opcoes_status = ["Todos", "LIGADA", "DESLIGADA"]
    status_selecionado = st.selectbox("Filtrar por status da irrigação", opcoes_status)

    if status_selecionado != "Todos":
        df_filtrado = df[df["status_irrigacao"] == status_selecionado]
    else:
        df_filtrado = df

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Média umidade", f"{df_filtrado['umidade'].mean():.2f}%")
    col2.metric("Média temperatura", f"{df_filtrado['temperatura'].mean():.2f}°C")
    col3.metric("Média pH", f"{df_filtrado['ph'].mean():.2f}")
    col4.metric("Total leituras", f"{len(df_filtrado)}")
    col5.metric("Irrigação ligada", f"{(df_filtrado['status_irrigacao'] == 'LIGADA').sum()}")

    st.write("Umidade ao longo do tempo")
    st.line_chart(df_filtrado.set_index("data_hora")[["umidade"]])

    st.write("pH ao longo do tempo")
    st.line_chart(df_filtrado.set_index("data_hora")[["ph"]])

    st.write("Presença de P e K")
    pk = pd.DataFrame({"sensor": ["P", "K"], "total": [df_filtrado["p"].sum(), df_filtrado["k"].sum()]})
    st.bar_chart(pk.set_index("sensor"))

    st.write("Sugestões registradas")
    st.dataframe(df_filtrado[["data_hora", "umidade", "ph", "status_irrigacao", "sugestao"]])


def render_analise_ml(df_ml: pd.DataFrame | None, metricas: pd.DataFrame | None) -> None:
    st.subheader("Pipeline de Machine Learning - Fase 4")
    st.write(
        "Os modelos de regressão usam dados de sensores para prever umidade futura, pH futuro "
        "e produtividade estimada. As métricas usadas são MAE, MSE, RMSE e R²."
    )

    if df_ml is None or metricas is None:
        st.warning("Modelos ainda não treinados. Execute: python ml/treinar_modelos.py")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Amostras ML", len(df_ml))
    col2.metric("Média produtividade", f"{df_ml['produtividade_estimada'].mean():.2f}")
    col3.metric("Média umidade prevista", f"{df_ml['umidade_prevista'].mean():.2f}%")

    st.write("Métricas dos modelos")
    st.dataframe(metricas)

    st.write("Correlação entre variáveis agrícolas")
    colunas_corr = ["umidade", "temperatura", "ph", "n", "p", "k", "nivel_chuva"] + TARGETS
    corr = df_ml[colunas_corr].corr(numeric_only=True)
    st.dataframe(corr.style.format("{:.2f}"))

    st.write("Tendência de produtividade estimada")
    st.line_chart(df_ml.reset_index()[["index", "produtividade_estimada"]].set_index("index"))

    st.write("Relação entre umidade prevista e produtividade estimada")
    st.scatter_chart(df_ml[["umidade_prevista", "produtividade_estimada"]])


def render_previsao_interativa(df_base: pd.DataFrame) -> None:
    st.subheader("Previsão interativa e recomendação de manejo")
    modelos = carregar_modelos()
    if len(modelos) < len(TARGETS):
        st.warning("Modelos não encontrados. Execute primeiro: python ml/treinar_modelos.py")
        return

    st.write("Informe uma leitura simulada do campo para gerar previsão em tempo real.")

    c1, c2, c3 = st.columns(3)
    umidade = c1.slider("Umidade atual (%)", 10.0, 90.0, float(df_base["umidade"].mean()))
    temperatura = c2.slider("Temperatura (°C)", 10.0, 45.0, float(df_base["temperatura"].mean()))
    ph = c3.slider("pH do solo", 4.0, 9.0, float(df_base["ph"].mean()))

    c4, c5, c6, c7 = st.columns(4)
    n = c4.selectbox("Nitrogênio (N)", [1, 0], format_func=lambda v: "Presente" if v == 1 else "Ausente")
    p = c5.selectbox("Fósforo (P)", [1, 0], format_func=lambda v: "Presente" if v == 1 else "Ausente")
    k = c6.selectbox("Potássio (K)", [1, 0], format_func=lambda v: "Presente" if v == 1 else "Ausente")
    nivel_chuva = c7.selectbox("Nível de chuva", [0, 1, 2], format_func=lambda v: {0: "Sem chuva", 1: "Chuva fraca/moderada", 2: "Chuva forte"}[v])

    irrigacao_ligada = st.toggle("Irrigação ligada no momento?", value=False)

    entrada = pd.DataFrame(
        [
            {
                "umidade": umidade,
                "temperatura": temperatura,
                "ph": ph,
                "n": int(n),
                "p": int(p),
                "k": int(k),
                "nivel_chuva": int(nivel_chuva),
                "irrigacao_ligada": int(irrigacao_ligada),
            }
        ]
    )

    previsoes = {target: float(modelos[target].predict(entrada[FEATURES])[0]) for target in TARGETS}
    recomendacao = sugerir_manejo(
        previsoes["umidade_prevista"],
        previsoes["ph_previsto"],
        previsoes["produtividade_estimada"],
        int(n),
        int(p),
        int(k),
        int(nivel_chuva),
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Umidade prevista", f"{previsoes['umidade_prevista']:.2f}%")
    col2.metric("pH previsto", f"{previsoes['ph_previsto']:.2f}")
    col3.metric("Produtividade estimada", f"{previsoes['produtividade_estimada']:.2f}")
    col4.metric("Irrigação recomendada", f"{recomendacao['volume_irrigacao_mm']:.2f} mm")

    st.write(f"Risco produtivo: **{recomendacao['risco_produtivo'].upper()}**")
    for acao in recomendacao["acoes"]:
        st.write(f"- {acao}")


def main() -> None:
    st.set_page_config(page_title="FarmTech Solutions - Fase 4", layout="wide")
    st.title("FarmTech Solutions - Assistente Agrícola Inteligente")
    st.write("Evolução da Fase 3 com Machine Learning, previsões e recomendações agrícolas.")

    df_base = carregar_dados_fase3()
    df_ml = carregar_dados_ml()
    metricas = carregar_metricas()

    aba1, aba2, aba3 = st.tabs(["Monitoramento", "ML e métricas", "Previsão interativa"])
    with aba1:
        render_monitoramento(df_base)
    with aba2:
        render_analise_ml(df_ml, metricas)
    with aba3:
        render_previsao_interativa(df_base)


if __name__ == "__main__":
    main()
