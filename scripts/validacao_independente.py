"""
Script de validação independente.
Recalcula os principais KPIs do zero a partir dos CSVs originais,
sem usar o pipeline silver/gold, pra confirmar que os números do
dashboard estão corretos.
"""
import pandas as pd
from pathlib import Path

BRONZE = Path(__file__).parent.parent / "data" / "bronze"


def main():
    boletos = pd.read_csv(BRONZE / "base_boletos_fiap.csv")
    auxiliar = pd.read_csv(BRONZE / "base_auxiliar_fiap.csv")

    print("Validação independente dos KPIs do dashboard\n")

    # contagens básicas
    print(f"Total de boletos: {len(boletos):,}")
    print(f"Cedentes únicos: {boletos['id_beneficiario'].nunique():,}")
    print(f"Sacados únicos: {boletos['id_pagador'].nunique():,}")
    print(f"CNPJs na base auxiliar: {auxiliar['id_cnpj'].nunique():,}")

    # valores
    boletos["vlr_nominal"] = pd.to_numeric(boletos["vlr_nominal"], errors="coerce")
    boletos["vlr_baixa"] = pd.to_numeric(boletos["vlr_baixa"], errors="coerce")
    print(f"\nValor total cedido: R$ {boletos['vlr_nominal'].sum():,.2f}")
    print(f"Valor total pago: R$ {boletos['vlr_baixa'].sum():,.2f}")

    # status / inadimplência
    boletos["dt_pagamento"] = pd.to_datetime(boletos["dt_pagamento"], errors="coerce")
    boletos["dt_vencimento"] = pd.to_datetime(boletos["dt_vencimento"], errors="coerce")
    boletos["dias_atraso"] = (boletos["dt_pagamento"] - boletos["dt_vencimento"]).dt.days

    em_aberto = boletos["dt_pagamento"].isna().sum()
    atraso = (boletos["dias_atraso"] > 0).sum()
    em_dia = (boletos["dias_atraso"] <= 0).sum()

    print(f"\nPago em dia: {em_dia:,}")
    print(f"Pago em atraso: {atraso:,}")
    print(f"Em aberto: {em_aberto:,}")
    print(f"% Inadimplência: {(atraso + em_aberto) / len(boletos) * 100:.2f}%")

    # aging
    print(f"\nAging médio (atrasados): {boletos.loc[boletos['dias_atraso'] > 0, 'dias_atraso'].mean():.2f} dias")

    # score médio - duas formas
    cruzado = boletos.merge(
        auxiliar[["id_cnpj", "score_materialidade_evolucao"]],
        left_on="id_beneficiario", right_on="id_cnpj", how="left"
    )
    print(f"\nScore médio (ponderado por boleto): {cruzado['score_materialidade_evolucao'].mean():.2f}")
    print(f"Score médio (CNPJs únicos): {auxiliar['score_materialidade_evolucao'].mean():.2f}")

    print(f"\nCobertura do cruzamento: "
          f"{boletos['id_beneficiario'].isin(auxiliar['id_cnpj']).sum() / len(boletos) * 100:.1f}%")


if __name__ == "__main__":
    main()
