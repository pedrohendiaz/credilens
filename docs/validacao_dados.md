# Validação dos Dados

Documento que comprova que os números mostrados no dashboard correspondem aos dados originais da Núclea. Os cálculos abaixo foram refeitos do zero, lendo direto os CSVs originais, sem usar o pipeline próprio.

## Método

Para cada KPI principal, refiz o cálculo manualmente em um script independente lendo `data/bronze/base_boletos_fiap.csv` e `data/bronze/base_auxiliar_fiap.csv`. Comparei com o que aparece no dashboard.

## Resultados

| Métrica | Dashboard | Validação independente | Status |
|---|---|---|---|
| Total de boletos | 7.118 | 7.118 | OK |
| Cedentes únicos (id_beneficiario) | 1.189 | 1.189 | OK |
| Sacados únicos (id_pagador) | 3.525 | 3.525 | OK |
| Valor total cedido (vlr_nominal) | R$ 165.853.488,09 | R$ 165.853.488,09 | OK |
| Valor total pago (vlr_baixa) | R$ 129.555.096,05 | R$ 129.555.096,05 | OK |
| % Inadimplência (atraso + aberto) | 30,30% | 30,30% | OK |
| Pago em dia | 4.961 (69,70%) | 4.961 | OK |
| Pago em atraso | 2.087 (29,32%) | 2.087 | OK |
| Em aberto | 70 (0,98%) | 70 | OK |
| Aging médio (boletos atrasados) | 16,03 dias | 16,03 dias | OK |
| Score médio (ponderado por boleto) | 527,41 | 527,41 | OK |
| Cobertura boletos × auxiliar | 100% | 100% | OK |

Todos os números bateram.

## Confronto com dashboard do grupo na Sprint 3

O dashboard do grupo (`DataViz_Nuclea` no Looker Studio) também usou as mesmas bases. Os números que coincidem nos dois dashboards:

- Beneficiários únicos: **1.189** (deles) vs **1.189 cedentes** (CrediLens)
- Pagadores únicos: **3.525** (deles) vs **3.525 sacados** (CrediLens)

A nomenclatura é diferente (`beneficiario` no deles vs `cedente` no CrediLens) porque o "beneficiário" do boleto original passa a ser tratado como "cedente" no contexto do FIDC após a cessão do crédito.

## Observação sobre o score médio

Existem duas formas válidas de calcular o score médio da carteira:

1. **Média ponderada por boleto:** 527,41 - cada boleto na carteira conta o score do beneficiário dele. Cedentes com muitos boletos pesam mais.
2. **Média simples dos CNPJs únicos:** 756,45 - apenas a média aritmética dos 4.612 CNPJs na base auxiliar.

**O dashboard usa a forma 1 (527).** A justificativa é que ela responde "qual é a qualidade média da carteira efetivamente cedida ao FIDC", que é a pergunta relevante pra gestão de risco. A forma 2 representaria toda a base cadastral da Núclea, não a carteira em si.

## Verificação reproduzível

O código que faz essa validação está em `scripts/validacao_independente.py`. Pode ser rodado a qualquer momento para reproduzir as contas.
