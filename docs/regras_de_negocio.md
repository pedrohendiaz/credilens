# Regras de Negócio Aplicadas

Documento técnico que descreve cada regra de negócio aplicada nas camadas Silver e Gold do pipeline. Serve como referência tanto pra mim (autor do projeto) quanto pra qualquer pessoa que queira entender o que cada coluna do dashboard significa.

As regras foram desenhadas a partir do dicionário de dados fornecido pela Núclea e do que entendi como práticas comuns do mercado de FIDC (consultei material acadêmico e regulamentação CVM 175).

## Camada Silver

### 1. Dias de atraso

```
dias_atraso = dt_pagamento - dt_vencimento
```

Negativo ou zero = pago em dia (ou adiantado). Positivo = atraso. Nulo = boleto ainda não pago.

### 2. Status do boleto

- Se `dt_pagamento` é nula → `em_aberto`
- Se `dias_atraso <= 0` → `pago_em_dia`
- Se `dias_atraso > 0` → `pago_em_atraso`

### 3. Faixa de aging

Buckets de atraso usados em gestão de carteira:

- 0 - Em dia
- 1 - Atraso 1 a 5 dias
- 2 - Atraso 6 a 15 dias
- 3 - Atraso 16 a 30 dias
- 4 - Atraso 31 a 60 dias
- 5 - Atraso 60+ dias

Escolhi essas faixas porque uma das colunas que a Núclea já nos entregou (`share_vl_inad_pag_bol_6_a_15d`) usa essa segmentação, o que sugere que é uma padronização interna deles.

### 4. Conciliação

```
boleto_conciliado = (vlr_baixa == vlr_nominal)
```

Quando o valor pago é igual ao valor nominal, o boleto está conciliado. Quando difere, indica pagamento parcial ou divergência - algo que precisa de atenção em auditoria.

### 5. Mês de referência

Extraio o mês e ano de `dt_emissao` e `dt_vencimento` para permitir análises temporais agregadas.

### 6. Setor econômico

Mapeio os 2 primeiros dígitos do CNAE pra grandes setores, seguindo classificação do IBGE:

- 01-03: Agropecuária
- 05-09: Indústria Extrativa
- 10-33: Indústria
- 35: Eletricidade e Gás
- 36-39: Utilidades
- 41-43: Construção
- 45-47: Comércio
- 49-53: Transporte
- 55-56: Alojamento/Alimentação
- 58-63: Informação/Comunicação
- 64-66: Financeiro
- Demais: Serviços/Outros

### 7. Região do Brasil

Mapeamento UF → região (Norte, Nordeste, Centro-Oeste, Sudeste, Sul) seguindo divisão regional do IBGE.

### 8. Classificação de risco

Baseada no `score_materialidade_evolucao` (que vai de 0 a 1000):

- score < 300 → Alto Risco
- 300 ≤ score < 700 → Médio Risco
- score ≥ 700 → Baixo Risco
- score nulo → Sem Classificação

Escolhi esses cortes (300 e 700) por dois motivos: dividem a escala em três faixas semanticamente claras e me dão uma distribuição razoavelmente equilibrada na base.

## Camada Gold

### 9. % de inadimplência

```
% inad = (boletos em atraso + boletos em aberto) / total × 100
```

Calculado em diferentes granularidades: geral, por setor, por UF, por mês, por cedente.

### 10. Aging médio

Média de `dias_atraso` apenas para boletos com `dias_atraso > 0`. Responde "quando atrasam, em média quanto tempo demoram a pagar".

### 11. Score médio da carteira

Média do `score_materialidade_evolucao` ponderada pela presença dos cedentes nos boletos. Cedentes que aparecem em muitos boletos pesam mais na média. Faz mais sentido pra gestão de risco do que uma média simples dos CNPJs únicos.

### 12. Concentração de cedentes

```
% concentração = valor cedido por cedente / valor total × 100
```

Métrica crítica em gestão de FIDC. Cedente com alta concentração e baixo score é o pior cenário pro fundo, porque o impacto de uma inadimplência dele é grande.

### 13. Cruzamento boletos × auxiliar

`boletos.id_beneficiario = auxiliar.id_cnpj`, com `LEFT JOIN` (mantém o boleto mesmo se o beneficiário não estiver na base auxiliar). No nosso caso, a cobertura foi de 100% - todos os 7.118 boletos tinham seus beneficiários na base auxiliar.

## Aderência à CVM 175

As regras acima atendem aos seguintes princípios da Resolução CVM 175/2023:

- **Transparência**: KPIs padronizados e auditáveis
- **Rastreabilidade**: camadas Bronze/Silver/Gold preservam o dado original e o histórico de transformações
- **Padronização**: taxonomias unificadas (faixas de aging, setores, faixas de risco)
- **Avaliação de risco**: classificação e análise de concentração
- **Conciliação**: identificação de divergências entre cedido e pago
