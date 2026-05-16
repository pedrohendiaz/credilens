"""
Camada silver - aqui a gente limpa os dados crus e cria as colunas
derivadas que vão alimentar o dashboard.

As regras de negócio estão documentadas em docs/regras_de_negocio.md
"""
import pandas as pd
from pathlib import Path

BRONZE = Path(__file__).parent.parent / "data" / "bronze"
SILVER = Path(__file__).parent.parent / "data" / "silver"
SILVER.mkdir(parents=True, exist_ok=True)


# mapeamentos auxiliares
SETORES_CNAE = {
    range(1, 4): "Agropecuária",
    range(5, 10): "Indústria Extrativa",
    range(10, 34): "Indústria",
    range(35, 36): "Eletricidade e Gás",
    range(36, 40): "Utilidades",
    range(41, 44): "Construção",
    range(45, 48): "Comércio",
    range(49, 54): "Transporte",
    range(55, 57): "Alojamento/Alimentação",
    range(58, 64): "Informação/Comunicação",
    range(64, 67): "Financeiro",
}

REGIOES = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte",
    "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}


def faixa_aging(dias):
    if pd.isna(dias) or dias <= 0:
        return "0 - Em dia"
    if dias <= 5:
        return "1 - Atraso 1-5 dias"
    if dias <= 15:
        return "2 - Atraso 6-15 dias"
    if dias <= 30:
        return "3 - Atraso 16-30 dias"
    if dias <= 60:
        return "4 - Atraso 31-60 dias"
    return "5 - Atraso 60+ dias"


def classifica_risco(score):
    # baseado no score de materialidade evolução (produto Núclea, escala 0-1000)
    if pd.isna(score):
        return "Sem Classificação"
    if score < 300:
        return "Alto Risco"
    if score < 700:
        return "Médio Risco"
    return "Baixo Risco"


def mapeia_setor(cnae):
    if pd.isna(cnae):
        return "Não Informado"
    prefixo = int(str(int(cnae)).zfill(7)[:2])
    for faixa, setor in SETORES_CNAE.items():
        if prefixo in faixa:
            return setor
    return "Serviços/Outros"


def processa_boletos():
    print("Processando boletos...")
    df = pd.read_csv(BRONZE / "base_boletos_fiap.csv")

    # converte datas
    for col in ["dt_emissao", "dt_vencimento", "dt_pagamento"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # converte valores
    df["vlr_nominal"] = pd.to_numeric(df["vlr_nominal"], errors="coerce")
    df["vlr_baixa"] = pd.to_numeric(df["vlr_baixa"], errors="coerce")

    # dias de atraso
    df["dias_atraso"] = (df["dt_pagamento"] - df["dt_vencimento"]).dt.days

    # status do boleto
    df["status_boleto"] = "em_aberto"
    df.loc[df["dt_pagamento"].notna() & (df["dias_atraso"] <= 0), "status_boleto"] = "pago_em_dia"
    df.loc[df["dt_pagamento"].notna() & (df["dias_atraso"] > 0), "status_boleto"] = "pago_em_atraso"

    # faixa de aging (buckets)
    df["faixa_aging"] = df["dias_atraso"].apply(faixa_aging)

    # conciliação: boleto está conciliado quando vlr_baixa = vlr_nominal
    df["boleto_conciliado"] = (df["vlr_baixa"] == df["vlr_nominal"]).astype("object")
    df.loc[df["vlr_baixa"].isna(), "boleto_conciliado"] = None

    # mês de referência pra análises temporais
    df["mes_emissao"] = df["dt_emissao"].dt.to_period("M").astype(str)
    df["mes_vencimento"] = df["dt_vencimento"].dt.to_period("M").astype(str)

    df.to_parquet(SILVER / "boletos_silver.parquet", index=False)
    print(f"  ok - {len(df):,} boletos salvos")
    print(f"  status: {df['status_boleto'].value_counts().to_dict()}")


def processa_auxiliar():
    print("Processando base auxiliar...")
    df = pd.read_csv(BRONZE / "base_auxiliar_fiap.csv")

    # converte colunas numéricas
    cols_num = [
        "score_materialidade_evolucao", "score_quantidade_v2", "score_materialidade_v2",
        "sacado_indice_liquidez_1m", "cedente_indice_liquidez_1m",
        "indicador_liquidez_quantitativo_3m", "share_vl_inad_pag_bol_6_a_15d",
        "media_atraso_dias",
    ]
    for c in cols_num:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # enrichment
    df["setor_economico"] = df["cd_cnae_prin"].apply(mapeia_setor)
    df["regiao"] = df["uf"].map(REGIOES).fillna("Não Informado")
    df["faixa_risco"] = df["score_materialidade_evolucao"].apply(classifica_risco)

    df.to_parquet(SILVER / "auxiliar_silver.parquet", index=False)
    print(f"  ok - {len(df):,} CNPJs salvos")
    print(f"  risco: {df['faixa_risco'].value_counts().to_dict()}")


if __name__ == "__main__":
    processa_boletos()
    processa_auxiliar()
    print("\nSilver pronto.")
