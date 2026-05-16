"""
CrediLens - Dashboard de inteligência analítica para FIDCs.
Le os arquivos parquet da camada Gold e monta as visões interativas.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


st.set_page_config(
    page_title="CrediLens | Inteligência para FIDCs",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# paleta CrediLens — alinhada com o PPT
BG_PRIMARY = "#0A0E1A"
BG_SECONDARY = "#111827"
BG_CARD = "#1A2233"
PRIMARY = "#00D9FF"
SECONDARY = "#7C3AED"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER = "#EF4444"
TEXT = "#F1F5F9"
TEXT_MUTED = "#94A3B8"
TEXT_DIM = "#64748B"


st.markdown(f"""
<style>
    .stApp {{
        background-color: {BG_PRIMARY};
    }}

    #MainMenu, footer, header {{visibility: hidden;}}

    h1, h2, h3 {{
        color: {TEXT} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    h1 {{
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}

    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}

    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, {BG_SECONDARY} 0%, {BG_CARD} 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(0, 217, 255, 0.15);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }}

    [data-testid="stMetric"]:hover {{
        border-color: rgba(0, 217, 255, 0.4);
        box-shadow: 0 8px 32px rgba(0, 217, 255, 0.1);
        transform: translateY(-2px);
    }}

    [data-testid="stMetricLabel"] {{
        color: {TEXT_MUTED} !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}

    [data-testid="stMetricValue"] {{
        color: {TEXT} !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: #060912 !important;
        border-right: 1px solid rgba(0, 217, 255, 0.1);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem;
    }}

    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label {{
        background-color: transparent;
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        transition: all 0.2s ease;
        color: {TEXT};
    }}

    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {{
        background-color: rgba(0, 217, 255, 0.08);
    }}

    [data-testid="stDataFrame"] {{
        background-color: {BG_SECONDARY};
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    hr {{
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 2rem 0 !important;
    }}

    .stMultiSelect [data-baseweb="tag"] {{
        background-color: rgba(0, 217, 255, 0.15) !important;
        color: {PRIMARY} !important;
        border: 1px solid rgba(0, 217, 255, 0.3);
    }}

    .tag-ciano {{
        display: inline-block;
        background: rgba(0, 217, 255, 0.12);
        color: {PRIMARY};
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        border: 1px solid rgba(0, 217, 255, 0.3);
    }}

    .credilens-caption {{
        color: {TEXT_MUTED};
        font-size: 0.95rem;
        font-style: italic;
        margin-bottom: 1.5rem;
    }}

    .accent-line {{
        height: 4px;
        width: 60px;
        background: linear-gradient(90deg, {PRIMARY} 0%, {SECONDARY} 100%);
        border-radius: 2px;
        margin: 0.5rem 0 1.5rem 0;
    }}

    .info-box {{
        background-color: {BG_SECONDARY};
        border-left: 3px solid {PRIMARY};
        padding: 1rem 1.2rem;
        border-radius: 6px;
        margin: 1rem 0;
        color: {TEXT_MUTED};
    }}

    .info-box strong {{
        color: {TEXT};
    }}
</style>
""", unsafe_allow_html=True)


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


def aplicar_tema_plotly(fig, height=400):
    """Aplica tema dark unificado em qualquer figura plotly."""
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="-apple-system, Segoe UI, sans-serif", color=TEXT, size=12),
        title_font=dict(size=14, color=TEXT),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(color=TEXT_MUTED),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(color=TEXT_MUTED),
        ),
        legend=dict(
            bgcolor="rgba(17,24,39,0.8)",
            bordercolor="rgba(0,217,255,0.2)",
            borderwidth=1,
            font=dict(color=TEXT, size=11),
        ),
        margin=dict(t=50, b=40, l=40, r=20),
    )
    return fig


# sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 0 0 1rem 0;">
        <div style="font-size: 1.8rem; font-weight: 800; color: {TEXT}; letter-spacing: -0.02em;">
            🔍 CrediLens
        </div>
        <div style="color: {TEXT_MUTED}; font-size: 0.85rem; margin-top: 0.2rem;">
            Inteligência para FIDCs
        </div>
        <div style="height: 3px; width: 40px; background: linear-gradient(90deg, {PRIMARY}, {SECONDARY}); margin-top: 0.8rem; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='tag-ciano' style='margin: 1rem 0 0.5rem 0;'>NAVEGAÇÃO</div>", unsafe_allow_html=True)

    pagina = st.radio(
        " ",
        [
            "Visão Executiva",
            "Risco de Cedentes",
            "Setorial e Geográfica",
            "Evolução Temporal",
            "Sobre o Projeto",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown(f"""
    <div style="color: {TEXT_MUTED}; font-size: 0.8rem; line-height: 1.6;">
        <div style="color: {PRIMARY}; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.7rem; letter-spacing: 0.1em;">SOBRE</div>
        Plataforma analítica que consome dados da Núclea (PCR de boletos + scores)
        e entrega visões executivas para gestores, investidores e reguladores
        do mercado de FIDCs.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f"""
    <div style="color: {TEXT_DIM}; font-size: 0.75rem; line-height: 1.5;">
        <div style="color: {TEXT}; font-weight: 600;">Pedro Dias</div>
        RM 567031 · Turma 1TSCO<br>
        Challenge FIAP + Núclea<br>
        <a href="https://github.com/pedrohendiaz/credilens" style="color: {PRIMARY}; text-decoration: none;">↗ GitHub</a>
    </div>
    """, unsafe_allow_html=True)


# VISÃO EXECUTIVA
if pagina == "Visão Executiva":
    st.markdown(f"<div class='tag-ciano'>01 · EXECUTIVA</div>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top: 0.3rem;'>Visão Executiva da Carteira</h1>", unsafe_allow_html=True)
    st.markdown("<div class='accent-line'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='credilens-caption'>Indicadores consolidados dos boletos cedidos a FIDCs · Atualizado a partir da camada Gold do Data Lake</div>", unsafe_allow_html=True)

    k = dados["kpis"].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Valor Total Cedido", f"R$ {k['valor_total_cedido']/1e6:.1f}M")
    c2.metric("📄 Total de Boletos", f"{int(k['total_boletos']):,}".replace(",", "."))
    c3.metric("⚠️ Inadimplência", f"{k['pct_inadimplencia']:.1f}%")
    c4.metric("🎯 Score Médio", f"{k['score_medio_carteira']:.0f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("🏢 Cedentes Únicos", f"{int(k['total_cedentes_unicos']):,}".replace(",", "."))
    c6.metric("👥 Sacados Únicos", f"{int(k['total_sacados_unicos']):,}".replace(",", "."))
    c7.metric("⏱️ Aging Médio", f"{k['aging_medio_dias']:.0f} dias")
    c8.metric("📭 Em Aberto", f"{k['pct_em_aberto']:.1f}%")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<h3 style='font-size: 1.1rem; color: {TEXT};'>📊 Status dos Boletos</h3>", unsafe_allow_html=True)
        status = dados["fato"]["status_boleto"].value_counts().reset_index()
        status.columns = ["status", "qtd"]
        cores_status = {"pago_em_dia": SUCCESS, "pago_em_atraso": WARNING, "em_aberto": DANGER}
        fig = px.pie(status, values="qtd", names="status", color="status",
                     color_discrete_map=cores_status, hole=0.6)
        fig.update_traces(textposition="outside", textinfo="label+percent",
                          marker=dict(line=dict(color=BG_PRIMARY, width=2)),
                          textfont=dict(color=TEXT, size=12))
        fig = aplicar_tema_plotly(fig, height=380)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown(f"<h3 style='font-size: 1.1rem; color: {TEXT};'>📐 Distribuição por Faixa de Aging</h3>", unsafe_allow_html=True)
        aging = dados["aging"].copy()
        cores_aging = [SUCCESS, "#84CC16", WARNING, "#F97316", DANGER, "#991B1B"]
        fig = px.bar(aging, x="faixa_aging", y="qtd_boletos",
                     color="faixa_aging", color_discrete_sequence=cores_aging,
                     text="qtd_boletos")
        fig.update_traces(textposition="outside",
                          textfont=dict(color=TEXT, size=11),
                          marker=dict(line=dict(width=0)))
        fig = aplicar_tema_plotly(fig, height=380)
        fig.update_layout(xaxis_title="", yaxis_title="Quantidade",
                          showlegend=False, xaxis={"tickangle": -25})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown(f"<h3 style='font-size: 1.1rem; color: {TEXT};'>🎯 Cedentes por Faixa de Risco</h3>", unsafe_allow_html=True)
    cores_risco = {"Baixo Risco": SUCCESS, "Médio Risco": WARNING,
                   "Alto Risco": DANGER, "Sem Classificação": TEXT_DIM}
    c3, c4 = st.columns([2, 1])
    with c3:
        fig = px.bar(dados["risco"], x="faixa_risco", y="qtd_cedentes",
                     color="faixa_risco", color_discrete_map=cores_risco,
                     text="qtd_cedentes")
        fig.update_traces(textposition="outside", textfont=dict(color=TEXT, size=12))
        fig = aplicar_tema_plotly(fig, height=350)
        fig.update_layout(xaxis_title="", yaxis_title="Cedentes", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown(f"""
        <div class='info-box'>
            <strong style='color: {PRIMARY};'>Como classifico o risco</strong><br><br>
            Score de materialidade evolução da Núclea (0-1000):<br><br>
            🟢 <strong>Baixo:</strong> score ≥ 700<br>
            🟡 <strong>Médio:</strong> 300 ≤ score &lt; 700<br>
            🔴 <strong>Alto:</strong> score &lt; 300
        </div>
        """, unsafe_allow_html=True)


# RISCO DE CEDENTES
elif pagina == "Risco de Cedentes":
    st.markdown(f"<div class='tag-ciano'>02 · RISCO</div>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top: 0.3rem;'>Análise de Risco de Cedentes</h1>", unsafe_allow_html=True)
    st.markdown("<div class='accent-line'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='credilens-caption'>Identifica os cedentes mais expostos e os mais arriscados da carteira</div>", unsafe_allow_html=True)

    ced = dados["cedentes"].copy()

    f1, f2, f3 = st.columns(3)
    with f1:
        filtro_risco = st.multiselect("Faixa de Risco",
            ced["faixa_risco"].dropna().unique(),
            default=ced["faixa_risco"].dropna().unique())
    with f2:
        filtro_setor = st.multiselect("Setor",
            sorted(ced["setor"].dropna().unique()),
            default=sorted(ced["setor"].dropna().unique()))
    with f3:
        topn = st.slider("Top N cedentes", 5, 50, 20)

    ced_filt = ced[
        ced["faixa_risco"].isin(filtro_risco) & ced["setor"].isin(filtro_setor)
    ].head(topn)

    st.markdown(f"<h3 style='font-size: 1.1rem; color: {TEXT};'>🏆 Top {topn} Cedentes por Valor Cedido</h3>", unsafe_allow_html=True)
    ced_filt["id_curto"] = ced_filt["id_beneficiario"].str[:8] + "..."
    fig = px.bar(ced_filt, x="valor_total", y="id_curto",
                 color="faixa_risco", orientation="h",
                 color_discrete_map={
                     "Baixo Risco": SUCCESS, "Médio Risco": WARNING,
                     "Alto Risco": DANGER, "Sem Classificação": TEXT_DIM,
                 },
                 hover_data=["setor", "uf", "score", "pct_inadimplencia"])
    fig = aplicar_tema_plotly(fig, height=600)
    fig.update_layout(xaxis_title="Valor Cedido (R$)", yaxis_title="",
                      yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown(f"<h3 style='font-size: 1.1rem; color: {TEXT};'>🎯 Mapa de Risco: Score × Concentração</h3>", unsafe_allow_html=True)
    st.markdown(f"<div class='credilens-caption'>Cedentes na parte superior esquerda (alta concentração + baixo score) merecem atenção crítica</div>", unsafe_allow_html=True)

    fig = px.scatter(ced.head(100), x="score", y="pct_concentracao",
                     size="qtd_boletos", color="faixa_risco",
                     color_discrete_map={
                         "Baixo Risco": SUCCESS, "Médio Risco": WARNING,
                         "Alto Risco": DANGER, "Sem Classificação": TEXT_DIM,
                     },
                     hover_data=["setor", "uf", "valor_total"])
    fig = aplicar_tema_plotly(fig, height=500)
    fig.update_layout(xaxis_title="Score (0-1000, maior = melhor)",
                      yaxis_title="% Concentração na Carteira")
    fig.update_traces(marker=dict(line=dict(width=1, color=BG_PRIMARY)))
    fig.add_vline(x=300, line_dash="dash", line_color=DANGER, opacity=0.6)
    fig.add_vline(x=700, line_dash="dash", line_color=SUCCESS, opacity=0.6)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown(f"<h3 style='font-size: 1.1rem; color: {TEXT};'>📋 Tabela Detalhada</h3>", unsafe_allow_html=True)
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


# SETORIAL E GEOGRÁFICA
elif pagina == "Setorial e Geográfica":
    st.markdown(f"<div class='tag-ciano'>03 · SETORIAL · GEOGRÁFICA</div>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top: 0.3rem;'>Visão Setorial e Geográfica</h1>", unsafe_allow_html=True)
    st.markdown("<div class='accent-line'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='credilens-caption'>Como o volume e o risco se distribuem entre setores econômicos e regiões do Brasil</div>", unsafe_allow_html=True)

    st.markdown(f"<h3 style='font-size: 1.1rem; color: {TEXT};'>🏭 Análise Setorial</h3>", unsafe_allow_html=True)
    setor = dados["setor"].copy()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(setor, x="setor_economico", y="valor_total",
                     color="pct_inadimplencia",
                     color_continuous_scale=[[0, SUCCESS], [0.5, WARNING], [1, DANGER]],
                     labels={"pct_inadimplencia": "% Inad."})
        fig = aplicar_tema_plotly(fig, height=450)
        fig.update_layout(title="Valor Cedido por Setor (cor = inadimplência)",
                          xaxis_title="", yaxis_title="Valor (R$)",
                          xaxis={"tickangle": -35})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(setor, x="aging_medio", y="pct_inadimplencia",
                         size="valor_total", color="setor_economico",
                         text="setor_economico", size_max=70,
                         color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(textposition="top center",
                          textfont=dict(color=TEXT, size=10),
                          marker=dict(line=dict(width=1, color=BG_PRIMARY)))
        fig = aplicar_tema_plotly(fig, height=450)
        fig.update_layout(title="Risco Setorial: Aging × Inadimplência (tam = volume)",
                          xaxis_title="Aging Médio (dias)",
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

    st.markdown(f"<h3 style='font-size: 1.1rem; color: {TEXT};'>🗺️ Geografia (UF e Região)</h3>", unsafe_allow_html=True)
    geo = dados["geo"].copy()

    c3, c4 = st.columns(2)
    with c3:
        reg = geo.groupby("regiao").agg(
            valor_total=("valor_total", "sum"),
            qtd_boletos=("qtd_boletos", "sum"),
        ).reset_index().sort_values("valor_total", ascending=False)
        fig = px.pie(reg, values="valor_total", names="regiao", hole=0.6,
                     color_discrete_sequence=[PRIMARY, SECONDARY, SUCCESS, WARNING, DANGER, TEXT_DIM])
        fig.update_traces(textposition="outside", textinfo="label+percent",
                          marker=dict(line=dict(color=BG_PRIMARY, width=2)),
                          textfont=dict(color=TEXT, size=11))
        fig = aplicar_tema_plotly(fig, height=420)
        fig.update_layout(title="Volume Cedido por Região", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.bar(geo.sort_values("valor_total", ascending=True),
                     x="valor_total", y="uf",
                     color="pct_inadimplencia",
                     color_continuous_scale=[[0, SUCCESS], [0.5, WARNING], [1, DANGER]],
                     orientation="h")
        fig = aplicar_tema_plotly(fig, height=500)
        fig.update_layout(title="Valor por UF (cor = inadimplência)",
                          xaxis_title="Valor (R$)", yaxis_title="UF")
        st.plotly_chart(fig, use_container_width=True)


# EVOLUÇÃO TEMPORAL
elif pagina == "Evolução Temporal":
    st.markdown(f"<div class='tag-ciano'>04 · TEMPORAL</div>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top: 0.3rem;'>Evolução Temporal</h1>", unsafe_allow_html=True)
    st.markdown("<div class='accent-line'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='credilens-caption'>Como a carteira se comporta ao longo do tempo · Análise mensal de 34 períodos</div>", unsafe_allow_html=True)

    evo = dados["evolucao"].copy()
    evo = evo[evo["mes_emissao"].notna() & (evo["mes_emissao"] != "NaT")]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=evo["mes_emissao"], y=evo["valor_emitido"],
                         name="Emitido", marker_color=PRIMARY,
                         marker_line_width=0))
    fig.add_trace(go.Bar(x=evo["mes_emissao"], y=evo["valor_pago"],
                         name="Pago", marker_color=SUCCESS,
                         marker_line_width=0))
    fig = aplicar_tema_plotly(fig, height=450)
    fig.update_layout(title="Volume Emitido vs Pago por Mês",
                      barmode="group",
                      xaxis_title="Mês de Emissão", yaxis_title="Valor (R$)")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(evo, x="mes_emissao", y="pct_inadimplencia", markers=True)
    fig.update_traces(line_color=DANGER, line_width=3,
                      marker=dict(size=8, line=dict(width=2, color=BG_PRIMARY)))
    fig = aplicar_tema_plotly(fig, height=400)
    fig.update_layout(title="Evolução da Inadimplência (%)",
                      xaxis_title="Mês de Emissão", yaxis_title="% Inadimplência")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(evo, x="mes_emissao", y="qtd_boletos",
                 color="qtd_boletos",
                 color_continuous_scale=[[0, BG_CARD], [1, PRIMARY]])
    fig.update_traces(marker=dict(line=dict(width=0)))
    fig = aplicar_tema_plotly(fig, height=400)
    fig.update_layout(title="Boletos Emitidos por Mês",
                      xaxis_title="Mês de Emissão", yaxis_title="Quantidade")
    st.plotly_chart(fig, use_container_width=True)


# SOBRE O PROJETO
elif pagina == "Sobre o Projeto":
    st.markdown(f"<div class='tag-ciano'>SOBRE</div>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top: 0.3rem;'>Sobre o CrediLens</h1>", unsafe_allow_html=True)
    st.markdown("<div class='accent-line'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='info-box' style='border-left-color: {PRIMARY};'>
        <strong style='color: {PRIMARY}; font-size: 1.1rem;'>O Problema</strong><br><br>
        O mercado de FIDCs (Fundos de Investimento em Direitos Creditórios) movimenta
        mais de <strong>R$ 400 bilhões</strong> no Brasil (ANBIMA, 2024). Apesar do volume,
        ainda opera com <strong>conciliação manual de boletos</strong>, <strong>assimetria
        informacional</strong> entre players e <strong>ausência de benchmarks padronizados</strong>.<br><br>
        A <strong>Resolução CVM 175/2023</strong> trouxe exigências de transparência e
        rastreabilidade, mas o setor carece de ferramentas analíticas que padronizem
        indicadores e automatizem análise de risco.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='info-box' style='border-left-color: {SECONDARY};'>
        <strong style='color: {SECONDARY}; font-size: 1.1rem;'>A Solução</strong><br><br>
        CrediLens consome os dados anonimizados da Núclea (PCR de boletos + scores de risco)
        e entrega <strong>4 visões analíticas</strong>:<br><br>
        🏠 <strong>Visão Executiva</strong> · KPIs consolidados da carteira<br>
        ⚠️ <strong>Risco de Cedentes</strong> · análise de concentração e exposição<br>
        🌎 <strong>Setorial e Geográfica</strong> · comparativo entre setores e regiões<br>
        📈 <strong>Evolução Temporal</strong> · série histórica mensal
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f"<h2 style='font-size: 1.4rem;'>🏗️ Arquitetura</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='credilens-caption'>Pipeline em modelo Medalhão, 100% Python, pronto pra escalar</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display: flex; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px; background: {BG_SECONDARY}; padding: 1.2rem; border-radius: 10px; border-left: 4px solid #CD7F32;">
            <div style="color: #CD7F32; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.15em;">BRONZE</div>
            <div style="color: {TEXT}; font-size: 1.1rem; font-weight: 700; margin: 0.4rem 0;">Dados crus</div>
            <div style="color: {TEXT_MUTED}; font-size: 0.85rem;">CSVs originais da Núclea, intactos. Fonte da verdade auditável.</div>
        </div>
        <div style="flex: 1; min-width: 200px; background: {BG_SECONDARY}; padding: 1.2rem; border-radius: 10px; border-left: 4px solid #C0C0C0;">
            <div style="color: #C0C0C0; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.15em;">SILVER</div>
            <div style="color: {TEXT}; font-size: 1.1rem; font-weight: 700; margin: 0.4rem 0;">Dados limpos</div>
            <div style="color: {TEXT_MUTED}; font-size: 0.85rem;">Tipagem correta, regras de negócio aplicadas, formato Parquet.</div>
        </div>
        <div style="flex: 1; min-width: 200px; background: {BG_SECONDARY}; padding: 1.2rem; border-radius: 10px; border-left: 4px solid #FFD700;">
            <div style="color: #FFD700; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.15em;">GOLD</div>
            <div style="color: {TEXT}; font-size: 1.1rem; font-weight: 700; margin: 0.4rem 0;">Agregados</div>
            <div style="color: {TEXT_MUTED}; font-size: 0.85rem;">Tabelas analíticas otimizadas, prontas para consumo no dashboard.</div>
        </div>
        <div style="flex: 1; min-width: 200px; background: {BG_SECONDARY}; padding: 1.2rem; border-radius: 10px; border-left: 4px solid {PRIMARY};">
            <div style="color: {PRIMARY}; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.15em;">DASHBOARD</div>
            <div style="color: {TEXT}; font-size: 1.1rem; font-weight: 700; margin: 0.4rem 0;">Interface</div>
            <div style="color: {TEXT_MUTED}; font-size: 0.85rem;">App Streamlit interativo, hospedado em nuvem.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h2 style='font-size: 1.4rem; margin-top: 2rem;'>⚙️ Stack Tecnológico</h2>", unsafe_allow_html=True)

    stack = [
        ("INGESTÃO & PROCESSAMENTO", "Python · Pandas · PyArrow", PRIMARY),
        ("ARMAZENAMENTO", "Parquet (Data Lake)", SECONDARY),
        ("VISUALIZAÇÃO", "Streamlit · Plotly", SUCCESS),
        ("VERSIONAMENTO", "Git · GitHub", WARNING),
        ("DEPLOY", "Streamlit Community Cloud", DANGER),
    ]

    for tag, desc, cor in stack:
        st.markdown(f"""
        <div style='background: {BG_SECONDARY}; padding: 0.9rem 1.2rem; border-radius: 8px; border-left: 3px solid {cor}; margin: 0.5rem 0;'>
            <div style='color: {cor}; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;'>{tag}</div>
            <div style='color: {TEXT}; font-size: 1rem; font-weight: 600;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<h2 style='font-size: 1.4rem; margin-top: 2rem;'>📐 Regras de Negócio</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='credilens-caption'>Documentação completa em <code>docs/regras_de_negocio.md</code> no GitHub</div>", unsafe_allow_html=True)

    regras = [
        "Cálculo de aging: dt_pagamento - dt_vencimento",
        "Classificação de status: em_dia · atraso · em_aberto",
        "Faixas de aging: 0 / 1-5 / 6-15 / 16-30 / 31-60 / 60+ dias",
        "Conciliação de valores: vlr_baixa = vlr_nominal",
        "Mapeamento CNAE → 12 setores econômicos",
        "Mapeamento UF → 5 regiões do Brasil",
        "Faixas de risco: score < 300 / 300-700 / ≥ 700",
        "Concentração de cedente: % do valor cedido total",
    ]

    for r in regras:
        st.markdown(f"<div style='color: {TEXT_MUTED}; margin: 0.3rem 0;'>▸ {r}</div>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f"""
    <div style='text-align: center; padding: 2rem; background: {BG_SECONDARY}; border-radius: 12px; border: 1px solid rgba(0,217,255,0.2);'>
        <div style='color: {PRIMARY}; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.15em;'>AUTOR</div>
        <div style='color: {TEXT}; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;'>Pedro Dias</div>
        <div style='color: {TEXT_MUTED};'>RM 567031 · Turma 1TSCO · Grupo 75</div>
        <div style='color: {TEXT_DIM}; font-size: 0.85rem; margin-top: 0.8rem;'>Challenge FIAP + Núclea · 2025/2026</div>
    </div>
    """, unsafe_allow_html=True)
