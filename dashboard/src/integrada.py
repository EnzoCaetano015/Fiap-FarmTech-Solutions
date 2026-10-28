from pathlib import Path
import sys
import uuid
import json
import hashlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import streamlit as st
from farmtech.config import state_dir
from farmtech.operations import execute
from farmtech.storage import history
from dashboard.src import fase4


def monitoring_frame(plot):
    from farmtech.services.iot import validate
    records = []
    for event in history("events", limit=1000, plot=plot, source="sensores"):
        try:
            records.append(validate(json.loads(event["payload"])))
        except (ValueError, TypeError, KeyError):
            continue
    if not records:
        return fase4.carregar_dados_fase3(), "CSV histórico simulado da Fase 2"
    frame = fase4.pd.DataFrame(records)
    frame["data_hora"] = fase4.pd.to_datetime(frame["data_hora"], utc=True)
    return frame.sort_values("data_hora"), f"Histórico operacional do talhão {plot}"


def show_vision_result(result):
    if result["sucesso"]:
        st.success(f"Concluído em {result['duracao_s']:.3f}s")
        st.json(result["dados"])
        st.image(next(p for p in result["arquivos"] if p.endswith("anotada.jpg")))
    else:
        st.error(result["erro"])


def action(label, service, **parameters):
    if st.button(label, key=f"action_{service}"):
        with st.spinner("Executando serviço…"):
            result = execute(service, **parameters)
        st.session_state[f"result_{service}"] = result
    result = st.session_state.get(f"result_{service}")
    if result:
        if result["sucesso"]:
            st.success(f"Concluído em {result['duracao_s']:.3f}s")
            st.json(result["dados"])
            for index, filename in enumerate(result["arquivos"]):
                path = Path(filename)
                if path.suffix.lower() in {".png", ".jpg"}:
                    st.image(str(path))
                if path.is_file() and path.stat().st_size < 15_000_000:
                    st.download_button(f"Baixar {path.name}", path.read_bytes(), file_name=path.name,
                                       key=f"download_{service}_{result['id']}_{index}")
        else:
            st.error(result["erro"])


def main():
    st.set_page_config(page_title="FarmTech Solutions — Fase 7", layout="wide")
    st.title("FarmTech Solutions")
    st.caption("Sistema integrado de gestão da fazenda · Fase 7 · Protótipo acadêmico")
    st.sidebar.info("Sensores CSV/ESP32 são simulados. Os alvos e dados ampliados da Fase 4 são sintéticos.")
    plot = st.sidebar.text_input("Talhão", "talhao-demo")
    tabs = st.tabs(["Monitoramento", "ML e métricas", "Previsão interativa", "Serviços", "Visão agrícola", "Alertas"])
    for tab, render in zip(tabs[:3], [fase4.render_monitoramento, None, fase4.render_previsao_interativa]):
        with tab:
            try:
                if render is fase4.render_monitoramento:
                    if st.button("Atualizar leituras"):
                        st.rerun()
                    frame, source = monitoring_frame(plot)
                    st.caption(source)
                    render(frame)
                elif render:
                    render(fase4.carregar_dados_fase3())
                else:
                    st.warning("Experimento com dados e alvos sintéticos; métricas não comprovam produtividade real.")
                    fase4.render_analise_ml(fase4.carregar_dados_ml(), fase4.carregar_metricas())
            except Exception as exc:
                st.warning(f"Painel indisponível ({type(exc).__name__}). Consulte os serviços ou treine os modelos.")
    with tabs[3]:
        st.subheader("Fase 1 · Área e insumos")
        shape = st.selectbox("Formato", ["retangulo", "circulo"])
        a, b, c = st.columns(3)
        length = a.number_input("Comprimento (m)", min_value=.01, value=100.)
        width = b.number_input("Largura (m)", min_value=.01, value=100.)
        radius = c.number_input("Raio (m)", min_value=.01, value=10.)
        dose = st.number_input("Dose informada (kg/ha)", min_value=0., value=10.)
        action("Calcular e exportar CSV", "area", shape=shape, length=length, width=width, radius=radius, dose=dose)
        action("Analisar sensores com R", "analise-r")
        st.subheader("Clima")
        lat = st.number_input("Latitude", min_value=-90., max_value=90., value=-23.55)
        lon = st.number_input("Longitude", min_value=-180., max_value=180., value=-46.63)
        action("Consultar previsão", "clima", latitude=lat, longitude=lon)
        st.subheader("Fase 2 · Simulação IoT")
        interval = st.slider("Intervalo entre leituras (segundos)", 0., 5., 1.)
        st.caption("Reproduz o CSV histórico com horários atuais e identificação de simulação. O monitor independente envia os alertas.")
        action("Reproduzir leituras simuladas", "iot", plot=plot, interval=interval, live_time=True)
        st.subheader("Fase 3 · Oracle")
        action("Importar CSV sem apagar registros", "oracle-importar")
        action("Consultar leituras Oracle", "oracle-consultar")
        st.subheader("Fase 4 · Modelos preditivos")
        action("Treinar modelos sintéticos", "treinar")
        if st.button("Recarregar modelos após treinamento"):
            st.cache_resource.clear()
            st.rerun()
        st.code("python -m farmtech --help", language="bash")
    with tabs[4]:
        st.subheader("Detecção de folhas de tomate")
        st.write("Folha saudável / folha com sinais de doença. O modelo sugere inspeção do talhão. Quando não há detecções, o resultado é inconclusivo.")
        upload = st.file_uploader("Imagem agrícola", type=["jpg", "jpeg", "png"])
        if upload is not None:
            context = (hashlib.sha256(upload.getvalue()).hexdigest(), plot)
            if upload.size > 10_000_000:
                st.error("Envie uma imagem com até 10 MB")
            elif st.button("Analisar imagem", key="action_visao"):
                folder = state_dir() / "uploads"
                folder.mkdir(exist_ok=True)
                path = folder / f"{uuid.uuid4().hex}{Path(upload.name).suffix.lower()}"
                path.write_bytes(upload.getvalue())
                with st.spinner("Inferência em CPU…"):
                    result = execute("visao", image=str(path), plot=plot)
                st.session_state["result_visao"] = result
                st.session_state["vision_context"] = context
            if (st.session_state.get("result_visao") and
                    st.session_state.get("vision_context") == context):
                show_vision_result(st.session_state["result_visao"])
    with tabs[5]:
        st.info("O serviço farmtech-monitor consulta eventos a cada 10s. 'published' indica aceite pelo SNS; confirme o e-mail recebido separadamente.")
        if st.button("Atualizar histórico"):
            st.rerun()
        st.dataframe(history(), width="stretch")
        with st.expander("Eventos e execuções"):
            st.dataframe(history("events"), width="stretch")
            st.dataframe(history("executions"), width="stretch")


if __name__ == "__main__":
    main()
