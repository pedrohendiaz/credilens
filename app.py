"""
CrediLens - Dashboard de inteligência analítica pra FIDCs.
Le os arquivos parquet da camada Gold e monta as visões interativas.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


st.set_page_config(
    page_title="CrediLens",
    page_icon="📊",
    layout="wide",
)


# paleta de cores do projeto
COR_PRIMARIA = "#1E88E5"
COR_SUCESSO = "#43A047"
COR_ALERTA = "#FB8C00"
COR_PERIGO = "#E53935"
COR_NEUTRO = "#546E7A"


@st.cache_data
def load_gold():
    gold = Path(__file__).parent / "data" / "gold"
    return {
        "fato": pd.read_parquet(gold / "fato_boletos.parquet"),
        "kpis": pd.read_parquet(gold / "kpis_executivos.parquet"),
        "setor": pd.read_parquet(gold / "visao_setor.parquet"),
        "geo": pd.read_parquet(gold / "visao_geografica.parquet"),
        "cedentes": pd.read_parquet(gold / "top_cedentes.parquet"),
        "evolucao": pd.read_parquet(gold / "evolucao_mensal.parquet"),
        "aging": pd.read_parquet(gold / "aging_distribuicao.parquet"),
        "risco": pd.read_parquet(gold / "risco_distribuicao.parquet"),
        "baixa": pd.read_parquet(gold / "tipos_baixa.parquet"),
    }


dados = load_gold()


# sidebar
st.sidebar.title("CrediLens")
st.sidebar.caption("Inteligência Analítica para FIDCs")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegação",
    [
        "Visão Executiva",
        "Risco de Cedentes",
        "Setorial e Geográfica",
        "Evolução Temporal",
        "Sobre",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Projeto desenvolvido no Enterprise Challenge "
    "FIAP + Núclea, 1º ano Tecnólogo em Data Science."
)
st.sidebar.caption("Pedro Dias · RM 567031")


# ----------------------------------------------------------------------------
# Página: Visão Executiva
# ----------------------------------------------------------------------------
if pagina == "Visão Executiva":
    st.title("Visão Executiva da Carteira")
    st.caption("Indicadores consolidados dos boletos cedidos a FIDCs")

    k = dados["kpis"].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valor Total Cedido", f"R$ {k['valor_total_cedido']/1e6:.1f}M")
    col2.metric("Total de Boletos", f"{int(k['total_boletos']):,}")
    col3.metric("Inadimplência", f"{k['pct_inadimplencia']:.1f}%")
    col4.metric("Score Médio", f"{k['score_medio_carteira']:.0f}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Cedentes Únicos", f"{int(k['total_cedentes_unicos']):,}")
    col6.metric("Sacados Únicos", f"{int(k['total_sacados_unicos']):,}")
    col7.metric("Aging Médio", f"{k['aging_medio_dias']:.0f} dias")
    col8.metric("Em Aberto", f"{k['pct_em_aberto']:.1f}%")

    st.markdown("---")

    # status dos boletos vs aging
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Status dos Boletos")
        status = dados["fato"]["status_boleto"].value_counts().reset_index()
        status.columns = ["status", "qtd"]
        cores = {"pago_em_dia": COR_SUCESSO, "pago_em_atraso": COR_ALERTA, "em_aberto": COR_PERIGO}
        fig = px.pie(status, values="qtd", names="status", color="status",
                     color_discrete_map=cores, hole=0.5)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Distribuição por Faixa de Aging")
        aging = dados["aging"].copy()
        fig = px.bar(aging, x="faixa_aging", y="qtd_boletos",
                     color="faixa_aging",
                     color_discrete_sequence=px.colors.sequential.Reds,
                     text="qtd_boletos")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=400, xaxis_title="", yaxis_title="Boletos",
                          showlegend=False, xaxis={"tickangle": -45})
        st.plotly_chart(fig, use_container_width=True)

    # distribuição de risco
    st.subheader("Cedentes por Faixa de Risco")
    cores_risco = {
        "Baixo Risco": COR_SUCESSO,
        "Médio Risco": COR_ALERTA,
        "Alto Risco": COR_PERIGO,
        "Sem Classificação": COR_NEUTRO,
    }
    c3, c4 = st.columns([2, 1])
    with c3:
        fig = px.bar(dados["risco"], x="faixa_risco", y="qtd_cedentes",
                     color="faixa_risco", color_discrete_map=cores_risco,
                     text="qtd_cedentes")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=350, xaxis_title="", yaxis_title="Cedentes",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.markdown("**Como classifico o risco**")
        st.markdown("""
        Uso o **score de materialidade evolução** da Núclea (escala 0-1000):

        - Baixo Risco: score ≥ 700
        - Médio Risco: 300 ≤ score < 700
        - Alto Risco: score < 300
        """)


# ----------------------------------------------------------------------------
# Página: Risco de Cedentes
# ----------------------------------------------------------------------------
elif pagina == "Risco de Cedentes":
    st.title("Análise de Risco de Cedentes")
    st.caption("Identifica os cedentes mais expostos e os mais arriscados da carteira")

    ced = dados["cedentes"].copy()

    # filtros
    f1, f2, f3 = st.columns(3)
    with f1:
        filtro_risco = st.multiselect(
            "Faixa de Risco",
            ced["faixa_risco"].dropna().unique(),
            default=ced["faixa_risco"].dropna().unique(),
        )
    with f2:
        filtro_setor = st.multiselect(
            "Setor",
            sorted(ced["setor"].dropna().unique()),
            default=sorted(ced["setor"].dropna().unique()),
        )
    with f3:
        topn = st.slider("Top N cedentes", 5, 50, 20)

    ced_filt = ced[
        ced["faixa_risco"].isin(filtro_risco)
        & ced["setor"].isin(filtro_setor)
    ].head(topn)

    # top cedentes
    st.subheader(f"Top {topn} Cedentes por Valor")
    ced_filt["id_curto"] = ced_filt["id_beneficiario"].str[:8] + "..."
    fig = px.bar(
        ced_filt, x="valor_total", y="id_curto",
        color="faixa_risco", orientation="h",
        color_discrete_map={
            "Baixo Risco": COR_SUCESSO,
            "Médio Risco": COR_ALERTA,
            "Alto Risco": COR_PERIGO,
            "Sem Classificação": COR_NEUTRO,
        },
        hover_data=["setor", "uf", "score", "pct_inadimplencia"],
    )
    fig.update_layout(height=600, xaxis_title="Valor Cedido (R$)",
                      yaxis_title="Cedente",
                      yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # scatter score x concentração
    st.subheader("Mapa de Risco: Score x Concentração")
    st.caption("Cedentes na parte superior esquerda merecem atenção (alta concentração + baixo score)")
    fig = px.scatter(
        ced.head(100), x="score", y="pct_concentracao",
        size="qtd_boletos", color="faixa_risco",
        color_discrete_map={
            "Baixo Risco": COR_SUCESSO,
            "Médio Risco": COR_ALERTA,
            "Alto Risco": COR_PERIGO,
            "Sem Classificação": COR_NEUTRO,
        },
        hover_data=["setor", "uf", "valor_total"],
    )
    fig.update_layout(height=500, xaxis_title="Score (0-1000)",
                      yaxis_title="% Concentração na Carteira")
    fig.add_vline(x=300, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_vline(x=700, line_dash="dash", line_color="green", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Tabela Detalhada")
    st.dataframe(
        ced_filt[["id_curto", "setor", "uf", "faixa_risco", "score",
                  "qtd_boletos", "valor_total", "pct_concentracao",
                  "pct_inadimplencia"]].style.format({
            "valor_total": "R$ {:,.2f}",
            "pct_concentracao": "{:.2f}%",
            "pct_inadimplencia": "{:.2f}%",
            "score": "{:.0f}",
        }),
        use_container_width=True, height=400,
    )


# ----------------------------------------------------------------------------
# Página: Setorial e Geográfica
# ----------------------------------------------------------------------------
elif pagina == "Setorial e Geográfica":
    st.title("Visão Setorial e Geográfica")

    st.subheader("Setor Econômico")
    setor = dados["setor"].copy()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(setor, x="setor_economico", y="valor_total",
                     color="pct_inadimplencia",
                     color_continuous_scale="RdYlGn_r",
                     labels={"pct_inadimplencia": "% Inad."})
        fig.update_layout(title="Valor Cedido por Setor (cor = inadimplência)",
                          height=450, xaxis_title="",
                          yaxis_title="Valor (R$)",
                          xaxis={"tickangle": -45})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(setor, x="aging_medio", y="pct_inadimplencia",
                         size="valor_total", color="setor_economico",
                         text="setor_economico", size_max=60)
        fig.update_traces(textposition="top center")
        fig.update_layout(title="Risco Setorial: Aging × Inadimplência (tam = volume)",
                          height=450, xaxis_title="Aging Médio (dias)",
                          yaxis_title="% Inadimplência", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        setor.style.format({
            "valor_total": "R$ {:,.2f}",
            "valor_pago": "R$ {:,.2f}",
            "aging_medio": "{:.1f}",
            "score_medio": "{:.0f}",
            "pct_inadimplencia": "{:.2f}%",
        }),
        use_container_width=True,
    )

    st.markdown("---")

    st.subheader("Geografia (por UF)")
    geo = dados["geo"].copy()

    c3, c4 = st.columns(2)
    with c3:
        reg = geo.groupby("regiao").agg(
            valor_total=("valor_total", "sum"),
            qtd_boletos=("qtd_boletos", "sum"),
        ).reset_index().sort_values("valor_total", ascending=False)
        fig = px.pie(reg, values="valor_total", names="regiao", hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(title="Volume Cedido por Região", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.bar(geo.sort_values("valor_total", ascending=True),
                     x="valor_total", y="uf",
                     color="pct_inadimplencia",
                     color_continuous_scale="RdYlGn_r",
                     orientation="h")
        fig.update_layout(title="Valor por UF (cor = inadimplência)",
                          height=500, xaxis_title="Valor (R$)",
                          yaxis_title="UF")
        st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------------------------------------------
# Página: Evolução Temporal
# ----------------------------------------------------------------------------
elif pagina == "Evolução Temporal":
    st.title("Evolução Temporal")
    st.caption("Comportamento mensal da carteira")

    evo = dados["evolucao"].copy()
    evo = evo[evo["mes_emissao"].notna() & (evo["mes_emissao"] != "NaT")]

    # emitido x pago
    fig = go.Figure()
    fig.add_trace(go.Bar(x=evo["mes_emissao"], y=evo["valor_emitido"],
                         name="Emitido", marker_color=COR_PRIMARIA))
    fig.add_trace(go.Bar(x=evo["mes_emissao"], y=evo["valor_pago"],
                         name="Pago", marker_color=COR_SUCESSO))
    fig.update_layout(title="Volume Emitido vs Pago por Mês",
                      barmode="group", height=450,
                      xaxis_title="Mês de Emissão", yaxis_title="Valor (R$)")
    st.plotly_chart(fig, use_container_width=True)

    # inadimplência ao longo do tempo
    fig = px.line(evo, x="mes_emissao", y="pct_inadimplencia", markers=True)
    fig.update_traces(line_color=COR_PERIGO, line_width=3)
    fig.update_layout(title="Evolução da Inadimplência (%)", height=400,
                      xaxis_title="Mês de Emissão", yaxis_title="% Inadimplência")
    st.plotly_chart(fig, use_container_width=True)

    # qtd boletos
    fig = px.bar(evo, x="mes_emissao", y="qtd_boletos",
                 color="qtd_boletos", color_continuous_scale="Blues")
    fig.update_layout(title="Boletos Emitidos por Mês", height=400,
                      xaxis_title="Mês de Emissão",
                      yaxis_title="Quantidade")
    st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------------------------------------------
# Página: Sobre
# ----------------------------------------------------------------------------
elif pagina == "Sobre":
    st.title("Sobre o CrediLens")

    st.markdown("""
    ## Contexto

    O mercado de FIDCs (Fundos de Investimento em Direitos Creditórios) movimenta
    mais de R$ 400 bilhões no Brasil. Apesar do volume, ainda opera com conciliação
    manual de boletos, assimetria informacional entre players e ausência de
    benchmarks padronizados.

    A Resolução CVM 175/2023 trouxe novas exigências de transparência, mas o
    setor carece de ferramentas que padronizem indicadores e automatizem
    análise de risco.

    ## A solução

    CrediLens consome os dados da Núclea (PCR de boletos + scores de risco) e entrega:

    - Visão executiva consolidada
    - Análise de risco e concentração de cedentes
    - Comparativo setorial e geográfico
    - Evolução temporal

    ## Arquitetura

    Pipeline em modelo Medalhão (Bronze → Silver → Gold), 100% em Python.

    Stack:
    - Pandas para processamento
    - PyArrow/Parquet para armazenamento
    - Streamlit + Plotly para visualização
    - Git/GitHub para versionamento
    - Streamlit Cloud para deploy

    ## Regras de negócio

    Documentação completa em `docs/regras_de_negocio.md` no repositório.

    Principais regras aplicadas:
    1. dias_atraso = dt_pagamento - dt_vencimento
    2. status_boleto: em_dia / pago_em_atraso / em_aberto
    3. Faixas de aging: 0 / 1-5 / 6-15 / 16-30 / 31-60 / 60+ dias
    4. Conciliação: vlr_baixa = vlr_nominal
    5. Faixa de risco baseada no score de materialidade
    6. Concentração por cedente sobre o valor total
    7. Mapeamento CNAE para setor econômico (12 grupos)

    ## Autor

    Pedro Dias · RM 567031 · Turma 1TSCO · FIAP 2025
    """)
