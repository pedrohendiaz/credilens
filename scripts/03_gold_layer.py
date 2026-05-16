"""
Camada gold - tabelas agregadas prontas pro dashboard.
Cada arquivo aqui responde uma pergunta de negócio diferente.
"""
import pandas as pd
from pathlib import Path

SILVER = Path(__file__).parent.parent / "data" / "silver"
GOLD = Path(__file__).parent.parent / "data" / "gold"
GOLD.mkdir(parents=True, exist_ok=True)


def pct_inadimplencia(serie):
    return serie.isin(["em_aberto", "pago_em_atraso"]).mean() * 100


def main():
    boletos = pd.read_parquet(SILVER / "boletos_silver.parquet")
    auxiliar = pd.read_parquet(SILVER / "auxiliar_silver.parquet")

    # cruzamento principal: boleto.id_beneficiario -> auxiliar.id_cnpj
    fato = boletos.merge(
        auxiliar,
        left_on="id_beneficiario",
        right_on="id_cnpj",
        how="left",
    )
    fato.to_parquet(GOLD / "fato_boletos.parquet", index=False)
    print(f"fato_boletos: {len(fato):,}")

    # KPIs executivos (linha única)
    kpis = pd.DataFrame([{
        "total_boletos": len(fato),
        "total_cedentes_unicos": fato["id_beneficiario"].nunique(),
        "total_sacados_unicos": fato["id_pagador"].nunique(),
        "valor_total_cedido": fato["vlr_nominal"].sum(),
        "valor_total_pago": fato["vlr_baixa"].sum(),
        "pct_inadimplencia": pct_inadimplencia(fato["status_boleto"]),
        "pct_em_aberto": (fato["status_boleto"] == "em_aberto").mean() * 100,
        "aging_medio_dias": fato.loc[fato["dias_atraso"] > 0, "dias_atraso"].mean(),
        "score_medio_carteira": fato["score_materialidade_evolucao"].mean(),
    }])
    kpis.to_parquet(GOLD / "kpis_executivos.parquet", index=False)
    print(f"kpis: valor_cedido={kpis['valor_total_cedido'][0]:,.0f}, "
          f"inad={kpis['pct_inadimplencia'][0]:.1f}%, "
          f"aging={kpis['aging_medio_dias'][0]:.0f}d")

    # visão por setor
    setor = fato.groupby("setor_economico").agg(
        qtd_boletos=("id_boleto", "count"),
        valor_total=("vlr_nominal", "sum"),
        valor_pago=("vlr_baixa", "sum"),
        aging_medio=("dias_atraso", lambda x: x[x > 0].mean()),
        score_medio=("score_materialidade_evolucao", "mean"),
        qtd_cedentes=("id_beneficiario", "nunique"),
    ).reset_index()
    setor["pct_inadimplencia"] = fato.groupby("setor_economico")["status_boleto"].apply(pct_inadimplencia).values
    setor = setor.sort_values("valor_total", ascending=False)
    setor.to_parquet(GOLD / "visao_setor.parquet", index=False)
    print(f"visao_setor: {len(setor)} setores")

    # visão geográfica
    geo = fato.groupby(["regiao", "uf"]).agg(
        qtd_boletos=("id_boleto", "count"),
        valor_total=("vlr_nominal", "sum"),
        score_medio=("score_materialidade_evolucao", "mean"),
        qtd_cedentes=("id_beneficiario", "nunique"),
    ).reset_index()
    geo["pct_inadimplencia"] = fato.groupby(["regiao", "uf"])["status_boleto"].apply(pct_inadimplencia).values
    geo.to_parquet(GOLD / "visao_geografica.parquet", index=False)
    print(f"visao_geografica: {len(geo)} UFs")

    # top cedentes (análise de concentração)
    cedentes = fato.groupby("id_beneficiario").agg(
        qtd_boletos=("id_boleto", "count"),
        valor_total=("vlr_nominal", "sum"),
        aging_medio=("dias_atraso", lambda x: x[x > 0].mean()),
        score=("score_materialidade_evolucao", "first"),
        setor=("setor_economico", "first"),
        uf=("uf", "first"),
        faixa_risco=("faixa_risco", "first"),
    ).reset_index()
    cedentes["pct_inadimplencia"] = fato.groupby("id_beneficiario")["status_boleto"].apply(pct_inadimplencia).values
    cedentes["pct_concentracao"] = cedentes["valor_total"] / cedentes["valor_total"].sum() * 100
    cedentes = cedentes.sort_values("valor_total", ascending=False)
    cedentes.to_parquet(GOLD / "top_cedentes.parquet", index=False)
    print(f"top_cedentes: {len(cedentes):,} cedentes")

    # evolução temporal
    evolucao = fato.groupby("mes_emissao").agg(
        qtd_boletos=("id_boleto", "count"),
        valor_emitido=("vlr_nominal", "sum"),
        valor_pago=("vlr_baixa", "sum"),
    ).reset_index()
    evolucao["pct_inadimplencia"] = fato.groupby("mes_emissao")["status_boleto"].apply(pct_inadimplencia).values
    evolucao = evolucao.sort_values("mes_emissao")
    evolucao.to_parquet(GOLD / "evolucao_mensal.parquet", index=False)
    print(f"evolucao_mensal: {len(evolucao)} meses")

    # distribuição de aging
    aging = fato.groupby("faixa_aging").agg(
        qtd_boletos=("id_boleto", "count"),
        valor_total=("vlr_nominal", "sum"),
    ).reset_index().sort_values("faixa_aging")
    aging.to_parquet(GOLD / "aging_distribuicao.parquet", index=False)
    print(f"aging_distribuicao: {len(aging)} faixas")

    # distribuição de risco
    risco = fato.groupby("faixa_risco").agg(
        qtd_boletos=("id_boleto", "count"),
        qtd_cedentes=("id_beneficiario", "nunique"),
        valor_total=("vlr_nominal", "sum"),
    ).reset_index()
    risco.to_parquet(GOLD / "risco_distribuicao.parquet", index=False)
    print(f"risco_distribuicao: {len(risco)} faixas")

    # tipos de baixa
    baixa = fato.groupby("tipo_baixa").agg(
        qtd_boletos=("id_boleto", "count"),
        valor_total=("vlr_nominal", "sum"),
    ).reset_index().sort_values("qtd_boletos", ascending=False)
    baixa.to_parquet(GOLD / "tipos_baixa.parquet", index=False)
    print(f"tipos_baixa: {len(baixa)} tipos")

    print("\nGold pronto.")


if __name__ == "__main__":
    main()
