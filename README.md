# CrediLens

Plataforma analítica para o mercado de FIDCs (Fundos de Investimento em Direitos Creditórios), desenvolvida como entrega final do Enterprise Challenge da FIAP em parceria com a Núclea.

**Dashboard online:** https://credilens.streamlit.app

## O problema

O mercado de FIDCs movimenta mais de R$ 400 bilhões no Brasil (ANBIMA, 2024), mas ainda opera com gargalos sérios:

- Conciliação manual de boletos entre múltiplas fontes
- Assimetria de informações entre gestores, investidores e reguladores
- Falta de benchmarks setoriais padronizados

A Resolução CVM 175/2023 trouxe exigências de transparência, mas faltam ferramentas analíticas que ajudem os participantes a cumprir essas exigências e ao mesmo tempo tomar decisões melhores.

## A proposta

O CrediLens consome dados anonimizados da Núclea (boletos cedidos a FIDCs + scores de risco) e entrega 4 visões:

1. **Visão Executiva** - KPIs consolidados da carteira (valor cedido, inadimplência, aging, score médio)
2. **Risco de Cedentes** - análise de concentração e exposição por cedente
3. **Setorial e Geográfica** - comparação entre setores e regiões
4. **Evolução Temporal** - série histórica mensal

## Resultados sobre as bases fornecidas

A análise das ~7.118 cessões e 4.612 CNPJs fornecidos pela Núclea revelou:

- **R$ 165,8 milhões** em valor total cedido
- **1.189 cedentes** únicos analisados
- **30,3%** de boletos inadimplentes
- **16 dias** de aging médio
- **Score médio 527** (faixa de médio risco)

## Arquitetura

Pipeline em modelo Medalhão:

```
Bronze (CSVs crus)  ->  Silver (Parquet limpo)  ->  Gold (Agregados)  ->  Dashboard
```

- **Bronze:** dados originais intactos (auditoria/rastreabilidade exigida pela CVM 175)
- **Silver:** dados limpos, tipados, com regras de negócio aplicadas
- **Gold:** tabelas agregadas prontas pro consumo do dashboard

## Stack

- Python (Pandas, PyArrow)
- Parquet para armazenamento
- Streamlit + Plotly para a interface
- GitHub para versionamento
- Streamlit Cloud para o deploy

## Como rodar local

```bash
git clone https://github.com/pedrohendiaz/credilens.git
cd credilens
pip install -r requirements.txt

# roda o pipeline de dados
python scripts/01_bronze_layer.py
python scripts/02_silver_layer.py
python scripts/03_gold_layer.py

# sobe o dashboard
streamlit run app.py
```

## Estrutura

```
credilens/
├── app.py                    # dashboard streamlit
├── requirements.txt
├── data/
│   ├── bronze/               # CSVs originais
│   ├── silver/               # parquets limpos
│   └── gold/                 # parquets agregados
├── scripts/
│   ├── 01_bronze_layer.py
│   ├── 02_silver_layer.py
│   └── 03_gold_layer.py
└── docs/
    ├── regras_de_negocio.md
    └── validacao_dados.md
```

## Documentação

- [Regras de negócio aplicadas](docs/regras_de_negocio.md)
- [Validação dos números](docs/validacao_dados.md)

## Sobre o uso de IA no projeto

Esse projeto foi construído usando IA generativa como ferramenta de apoio em algumas etapas (geração de código boilerplate, formatação de visualizações, escrita de documentação). Trabalho na área comercial há 4 anos com SQL, Excel e Power BI, então o desenho analítico (que métricas, que cruzamentos, que cortes fazem sentido pra FIDC) foi todo decidido por mim com base nos dados que recebi e no feedback do tutor na Sprint 3. Validei todos os números do dashboard contra cálculo manual - validação documentada em `docs/validacao_dados.md`.

## Autor

Pedro Dias · RM 567031 · 1TSCO · FIAP 2025
