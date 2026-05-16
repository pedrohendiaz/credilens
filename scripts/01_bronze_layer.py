"""
Camada bronze - valida os arquivos que recebemos da Núclea
antes de mandar pro pipeline.
"""
import pandas as pd
from pathlib import Path

BRONZE = Path(__file__).parent.parent / "data" / "bronze"


def check_arquivos():
    arquivos = ["base_boletos_fiap.csv", "base_auxiliar_fiap.csv"]

    for arq in arquivos:
        caminho = BRONZE / arq
        if not caminho.exists():
            print(f"[ERRO] Arquivo não encontrado: {arq}")
            continue

        df = pd.read_csv(caminho)
        print(f"\n{arq}")
        print(f"  linhas: {len(df):,}")
        print(f"  colunas: {len(df.columns)}")
        print(f"  campos: {', '.join(df.columns[:5])}...")


if __name__ == "__main__":
    print("Validando camada bronze...")
    check_arquivos()
    print("\nOK, prossiga pro silver.")
