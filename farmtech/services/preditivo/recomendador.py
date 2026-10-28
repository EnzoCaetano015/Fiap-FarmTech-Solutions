from __future__ import annotations


def classificar_faixa(valor: float, minimo: float, maximo: float) -> str:
    if valor < minimo:
        return "baixo"
    if valor > maximo:
        return "alto"
    return "adequado"


def sugerir_manejo(
    umidade_prevista: float,
    ph_previsto: float,
    produtividade_estimada: float,
    n: int,
    p: int,
    k: int,
    nivel_chuva: int,
) -> dict:
    """Gera recomendações agrícolas a partir das previsões do modelo.

    Regras usadas:
    - umidade ideal simulada: 35% a 55%; abaixo disso recomenda irrigação;
    - pH ideal: 5.8 a 7.0; fora disso recomenda correção;
    - NPK ausente recomenda fertilização específica;
    - chuva forte reduz/adia irrigação.
    """
    acoes = []
    volume_irrigacao_mm = 0.0

    faixa_umidade = classificar_faixa(umidade_prevista, 35.0, 55.0)
    faixa_ph = classificar_faixa(ph_previsto, 5.8, 7.0)

    if faixa_umidade == "baixo":
        volume_irrigacao_mm = round((35.0 - umidade_prevista) * 1.8, 2)
        if nivel_chuva == 2:
            acoes.append("Adiar irrigação: chuva forte prevista, mesmo com umidade baixa.")
            volume_irrigacao_mm = 0.0
        elif nivel_chuva == 1:
            acoes.append("Irrigar com volume reduzido, pois há chuva fraca/moderada prevista.")
            volume_irrigacao_mm = round(volume_irrigacao_mm * 0.5, 2)
        else:
            acoes.append("Irrigar o talhão para elevar a umidade do solo.")
    elif faixa_umidade == "alto":
        acoes.append("Manter irrigação desligada: umidade prevista acima da faixa ideal.")
    else:
        acoes.append("Manter monitoramento: umidade prevista em faixa adequada.")

    if faixa_ph == "baixo":
        acoes.append("Corrigir acidez do solo: pH previsto abaixo do ideal.")
    elif faixa_ph == "alto":
        acoes.append("Avaliar manejo para reduzir alcalinidade: pH previsto acima do ideal.")
    else:
        acoes.append("pH previsto dentro da faixa adequada.")

    nutrientes_faltantes = []
    if int(n) == 0:
        nutrientes_faltantes.append("N")
    if int(p) == 0:
        nutrientes_faltantes.append("P")
    if int(k) == 0:
        nutrientes_faltantes.append("K")

    if nutrientes_faltantes:
        acoes.append(
            "Fertilização recomendada para nutriente(s): "
            + ", ".join(nutrientes_faltantes)
            + "."
        )
    else:
        acoes.append("NPK adequado na leitura informada.")

    if produtividade_estimada < 55:
        risco = "alto"
        acoes.append("Risco produtivo alto: priorizar correção de solo e irrigação.")
    elif produtividade_estimada < 70:
        risco = "médio"
        acoes.append("Risco produtivo médio: acompanhar tendência e ajustar manejo.")
    else:
        risco = "baixo"
        acoes.append("Produtividade estimada favorável.")

    return {
        "volume_irrigacao_mm": volume_irrigacao_mm,
        "risco_produtivo": risco,
        "acoes": acoes,
    }
