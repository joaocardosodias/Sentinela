---
sidebar_position: 4
title: ROI, Payback e VPL
---

# Retorno sobre Investimento (ROI, Payback e VPL)

&emsp;Esta seção consolida os benefícios esperados da solução, modela o retorno financeiro ao longo de 5 anos e calcula os principais indicadores de viabilidade: ROI, Payback e VPL.

---

## 1. Situação Atual da Pier

&emsp;Segundo dados fornecidos pelo parceiro, a Pier registra atualmente **aproximadamente 70 casos de roubo ou furto por mês**, dos quais apenas **5 a 7 veículos são recuperados**, resultando em uma taxa de recuperação de aproximadamente **8,6%**.

&emsp;Isso significa que, dos 70 veículos roubados ou furtados por mês, em torno de **63–65 geram indenização integral** pela Tabela FIPE, representando o principal vetor de custo da sinistralidade nessa categoria.

| Indicador | Valor Atual |
|---|---|
| Veículos roubados/furtados por mês | ~70 |
| Veículos recuperados por mês | 5–7 (média: ~6) |
| Taxa de recuperação atual | ~8,6% |
| Veículos indenizados integralmente por mês | ~63–65 |

---

## 2. Lógica do Benefício

&emsp;No setor de seguros, a cobertura de roubo/furto indeniza o segurado em até 100% da Tabela FIPE quando o veículo não é recuperado. Portanto, cada veículo adicional recuperado representa uma economia direta para a seguradora equivalente ao valor FIPE do veículo.

$$\text{Benefício Bruto} = \text{Veículos adicionais recuperados/mês} \times \text{Indenização média evitada}$$

&emsp;A indenização média é estimada em **R$ 50.000**, com referência na Tabela FIPE para carteiras típicas de seguradoras de médio porte. Esta é a principal premissa de sensibilidade da análise (carteiras com veículos de maior valor elevam proporcionalmente o retorno).

---

## 3. Cenários de Recuperação com a Solução

&emsp;Os três cenários abaixo projetam diferentes níveis de melhoria na taxa de recuperação a partir da implantação da solução. A base de comparação é sempre a situação atual: ~6 veículos recuperados por mês.

| Cenário         | Recuperados/mês com solução | Taxa resultante | Ganho incremental | Benefício bruto/mês |
| --------------- | --------------------------- | --------------- | ----------------- | ------------------- |
| **Conservador** | 10                          | ~14,3%          | +4 veículos       | **R$ 200.000** |
| **Referência** | 14                          | ~20,0%          | +8 veículos       | **R$ 400.000** |
| **Otimista** | 18                          | ~25,7%          | +12 veículos      | **R$ 600.000** |

> **Contexto:** Os cenários apresentados representam projeções exploratórias baseadas nos dados fornecidos pelo parceiro e têm caráter ilustrativo para análise de viabilidade econômica.

> **Importante:** Esses valores representam a economia gerada para a Pier, não a receita direta do sistema. O modelo de negócio (equipe interna, SaaS, outsourcing) define como esse benefício se converte em retorno para quem investir.

---

## 4. Custo Total da Solução (5 anos)

&emsp;O custo total considera o CAPEX inicial mais o OPEX acumulado ao longo dos 5 anos, incluindo as devidas provisões para reposição de equipamentos para garantir a continuidade operacional.

### Cenário Base (DJI Mavic 3 Enterprise)

| Componente                |         Mínimo |           Máximo | Referência (médio) |
| ------------------------- | -------------: | ---------------: | -----------------: |
| CAPEX inicial             |     R$ 131.900 |       R$ 246.300 |         R$ 189.100 |
| OPEX acumulado (5 anos)   |     R$ 826.200 |     R$ 1.075.200 |     R$ 950.700 |
| Reposição de equipamentos |           R$ 0 |        R$ 66.000 |          R$ 33.000 |
| **Custo Total**           | **R$ 958.100** | **R$ 1.387.500** |   **R$ 1.172.800** |


### Cenário Simplificado (Drone Intermediário)

| Componente                |         Mínimo |           Máximo | Referência (médio) |
| ------------------------- | -------------: | ---------------: | -----------------: |
| CAPEX inicial             |      R$ 77.900 |       R$ 197.300 |         R$ 137.600 |
| OPEX acumulado (5 anos)   |     R$ 778.200 |     R$ 1.003.200 |     **R$ 890.700** |
| Reposição de equipamentos |      R$ 16.000 |        R$ 24.000 |          R$ 20.000 |
| **Custo Total**           | **R$ 872.100** | **R$ 1.224.500** |   **R$ 1.048.300** |

---

## 5. Projeção de Fluxo de Caixa (5 anos)

&emsp;Fluxo de caixa incremental anual para o **Cenário Referência** (+8 veículos/mês × R$ 50.000 = R$ 400.000/mês de benefício bruto, totalizando R$ 4.800.000/ano), utilizando o **Cenário Base** de equipamento (custo médio).

| Ano   | Benefício Anual | OPEX Anual   | CAPEX       | Fluxo Líquido    | Fluxo Acumulado   |
| ----- | --------------- | ------------ | ----------- | ---------------- | ----------------- |
| Ano 0 | —               | —            | -R$ 189.100 | -R$ 189.100      | -R$ 189.100       |
| Ano 1 | R$ 4.800.000    | -R$ 190.140  | —           | **R$ 4.609.860** | **R$ 4.420.760**  |
| Ano 2 | R$ 4.800.000    | -R$ 190.140  | —           | **R$ 4.609.860** | **R$ 9.030.620**  |
| Ano 3 | R$ 4.800.000    | -R$ 190.140  | —           | **R$ 4.609.860** | **R$ 13.640.480** |
| Ano 4 | R$ 4.800.000    | -R$ 190.140  | —           | **R$ 4.609.860** | **R$ 18.250.340** |
| Ano 5 | R$ 4.800.000    | -R$ 223.140* | —           | **R$ 4.576.860** | **R$ 22.827.200** |

> \* O OPEX do Ano 5 é acrescido do custo de reposição de equipamentos previsto em média (R$ 33.000) para encerramento ou renovação tecnológica do ciclo planejado. O OPEX regular anual é calculado a partir do OPEX médio mensal do Cenário Base (R$ 15.845 × 12 = R$ 190.140).

---

## 6. Indicadores de Viabilidade

### 6.1 ROI (Retorno sobre Investimento)

$$\text{ROI} = \frac{\text{Benefício Total (5 anos)} - \text{Custo Total (5 anos)}}{\text{Custo Total (5 anos)}} \times 100$$

| Cenário                       | Benefício 5 anos | Custo Total 5 anos |           ROI |
| ----------------------------- | ---------------: | -----------------: | ------------: |
| Conservador (+4 veículos/mês) |    R$ 12.000.000 |       R$ 1.172.800 |   **+923,3%** |
| Referência (+8 veículos/mês)  |    R$ 24.000.000 |       R$ 1.172.800 | **+1.946,6%** |
| Otimista (+12 veículos/mês)   |    R$ 36.000.000 |       R$ 1.172.800 | **+2.969,9%** |


### 6.2 Payback

&emsp;O payback representa o tempo necessário para que os benefícios operacionais líquidos superem o investimento inicial em CAPEX.

| Cenário     | Benefício/mês | OPEX médio/mês | Fluxo líquido/mês |      Payback |
| ----------- | ------------: | -------------: | ----------------: | -----------: |
| Conservador |    R$ 200.000 |      R$ 15.845 |        R$ 184.155 | **1,03 mês** |
| Referência  |    R$ 400.000 |      R$ 15.845 |        R$ 384.155 | **0,49 mês** |
| Otimista    |    R$ 600.000 |      R$ 15.845 |        R$ 584.155 | **0,32 mês** |

\* Cálculo baseado no CAPEX médio do Cenário Base (R$ 189.100) a partir do início efetivo da operação comercial.

> **Interpretação:** O benefício mensal gerado supera com ampla margem o OPEX mensal em todos os cenários. O investimento inicial (CAPEX) é integralmente recuperado logo nas primeiras semanas de operação. Considerando o prazo de desenvolvimento e implantação estimado em **~3–4 meses**, o payback total do projeto (contando o período pré-operacional) é de aproximadamente **4 meses** desde o marco zero.

### 6.3 VPL (Valor Presente Líquido)

&emsp;O VPL desconta os fluxos de caixa futuros a uma taxa de **15% ao ano**, refletindo o custo de capital (WACC) e o prêmio de risco típicos para insurtechs no mercado brasileiro.

| Cenário | VPL (5 anos, 15% a.a.) |
|---|---|
| Conservador (+4 veículos/mês) | **R$ 6.673.962,83** |
| Referência (+8 veículos/mês) | **R$ 14.719.135,07** |
| Otimista (+12 veículos/mês) | **R$ 22.764.307,30** |

> Um VPL multimilionário e altamente positivo em todos os cenários comprova a excelente resiliência financeira da iniciativa, mitigando riscos mesmo diante de taxas de desconto severas.

---

## 7. Análise de Sensibilidade

&emsp;A tabela abaixo cruza o ganho incremental de veículos mensalmente recuperados com diferentes valores médios de indenização da Tabela FIPE evitada. O indicador apresentado é o **ROI resultante em 5 anos**, calculado contra o custo médio total de longo prazo (Cenário Base: R$ 1.172.800).

| Ganho incremental/mês | FIPE média R$ 30k | FIPE média R$ 50k (Base) | FIPE média R$ 80k |
|---|---|---|---|
| **+4 veículos** (Conservador) | +513,9%% | **+923,3%** | +1537,3% |
| **+8 veículos** (Referência) | +1127,8% | **+1946,6%** | +3174,8% |
| **+12 veículos** (Otimista) | +1741,8% | **+2969,9%** | +4812,2% |

> A coluna central em negrito reflete a premissa de R$ 50.000 adotada no corpo desta modelagem. Nota-se que o modelo é extremamente elástico em relação ao ticket médio da carteira de seguros: carteiras focadas em veículos Premium aumentam o ROI de forma geométrica sem demandar acréscimos na infraestrutura operacional de drones.

---

## 8. Limitações da Análise

- O dado de 70 roubados/mês e 6 recuperados foi fornecido pelo parceiro e não pôde ser validado externamente por auditoria independente.
- A estimativa de R$ 50.000 de indenização média é uma referência paramétrica de mercado (o valor real flutuará dependendo do mix de apólices ativo da Pier).
- A taxa de recuperação incremental esperada está balizada em premissas técnicas; resultados reais dependem da eficiência das equipes em solo, qualidade dos algoritmos de visão computacional e meteorologia nas zonas de varredura.
- Benefícios intangíveis ou secundários não foram monetizados, tais como: melhora no índice de sinistralidade global, efeito reputacional de marca, inibição de novas tentativas de fraude e otimização em tabelas de precificação de apólices futuras.
- O modelo assume sinistro integral evitado a cada recuperação, desconsiderando custos marginais com reparos em veículos que venham a ser recuperados com avarias parciais.

---

## Referências

- Dados operacionais da Pier: material fornecido pelo parceiro (70 roubados/mês, 5–7 recuperados).
- Indenização por roubo/furto — cobertura 100% Tabela FIPE: referências de mercado de insurtechs nacionais.
- Taxa de desconto de 15% a.a.: prêmio de risco setorial padrão aplicado para valuations e projetos de tecnologia de seguros no Brasil.