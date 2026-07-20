---
sidebar_position: 5
title: Comparação com Sprint 1
---

# Comparação com a Análise Financeira da Sprint 1

&emsp;Esta seção compara a estimativa de custos produzida na Sprint 1 com a análise financeira mais detalhada desenvolvida na Sprint 4, evidenciando as diferenças de escopo, premissas e valores.

---

## 1. Diferença de Escopo

&emsp;A análise da Sprint 1 foi elaborada no início do projeto, com informações limitadas e foco em estimar o custo de um **piloto/MVP** — não de uma solução em produção. A análise da Sprint 4 parte de um entendimento mais maduro do sistema e projeta o custo de uma **implantação operacional real**, com equipe dedicada, equipamentos profissionais e horizonte de 5 anos.

| Dimensão | Sprint 1 | Sprint 4 |
|---|---|---|
| **Objetivo** | Estimar custo do MVP/piloto | Estimar viabilidade da solução em produção |
| **Drone considerado** | R$ 800–R$ 9.000 (entrada a 4K) | R$ 8.000–R$ 33.000 (intermediário a enterprise) |
| **Equipe de campo** | R$ 1.500–R$ 3.000/mês (operador genérico) | R$ 7.650/mês (1 piloto CLT) |
| **Equipe de tecnologia** | Custo por hora de desenvolvimento (one-shot) | Custo de manutenção contínua (PJ, parcial) |
| **Compliance regulatório** | Não considerado | Considerado (ANAC, seguro operacional) |
| **Horizonte de análise** | 12 meses | 60 meses (5 anos) |
| **Indicadores calculados** | Custo total apenas | ROI, Payback, VPL, análise de sensibilidade |

---

## 2. Comparação de Valores — CAPEX

| Categoria | Sprint 1 (mínimo–máximo) | Sprint 4 — Cenário Base | Sprint 4 — Cenário Simplificado |
|---|---|---|---|
| Hardware (drone + periféricos) | R$ 7.100–R$ 22.100 | R$ 81.400–R$ 88.800 (2 drones enterprise + acessórios) | R$ 31.000–R$ 50.000 |
| Desenvolvimento | R$ 15.000–R$ 35.000 | R$ 39.500–R$ 127.700 | R$ 39.500–R$ 127.700 |
| Compliance | Não considerado | R$ 14.000–R$ 31.000 | R$ 12.000–R$ 27.000 |
| **CAPEX Total** | **R$ 22.100–R$ 57.100** | **R$ 131.900–R$ 246.300** | **R$ 104.500–R$ 241.700** |

**Principal diferença:** A Sprint 1 considerava 1 drone de baixo custo; a Sprint 4 projeta 2 drones profissionais para operação contínua, além de incluir compliance regulatório e edge computing adequado.

---

## 3. Comparação de Valores — OPEX

| Categoria | Sprint 1 (mínimo–máximo/mês) | Sprint 4 — Cenário Base (mínimo–máximo/mês) |
|---|---|---|
| Equipe (operação) | R$ 1.500–R$ 3.000 | R$ 7.650 |
| Equipe (tecnologia) | Não separado (one-shot no CAPEX) | R$ 4.000–6.000 |
| Infraestrutura cloud | R$ 60–R$ 280 | R$ 270–R$ 520 |
| Conectividade | R$ 80–R$ 150 | R$ 70–100 |
| Manutenção de equipamentos | R$ 100–R$ 300 | R$ 1.500–R$ 3.000 |
| Energia | R$ 20–R$ 50 | R$ 150–R$ 300 |
| **OPEX Total** | **R$ 1.760–R$ 3.780** | **R$ 13.770–R$ 17.920** |

**Principal diferença:** A Sprint 1 subestimou significativamente o custo da equipe. O OPEX real de uma operação com 1 piloto CLT habilitado e uma equipe de tecnologia em manutenção contínua é ~10× maior do que o estimado inicialmente.

---

## 4. Projeção de 12 meses

&emsp;Para facilitar a comparação direta, a tabela abaixo projeta os custos totais em 12 meses (mesmo horizonte usado na Sprint 1).

| Cenário | Sprint 1 (estimativa original) | Sprint 4 — Cenário Base | Sprint 4 — Cenário Simplificado |
|---|---|---|---|
| **Mínimo** | R$ 43.220 | R$ 297.140 | R$ 233.540 |
| **Máximo** | R$ 102.460 | R$ 461.340 | R$ 407.940 |

> A diferença expressiva reflete principalmente a mudança de escopo: a Sprint 1 estimava um piloto com 1 drone e 1 operador sem vínculo CLT; a Sprint 4 projeta uma operação real com 2 drones profissionais, equipe dedicada e conformidade regulatória.

---

## 5. O que Mudou e Por Quê

### Equipe foi subestimada
&emsp;A Sprint 1 usou uma faixa genérica de "operador de drone" sem considerar a exigência de habilitação ANAC, regime CLT e encargos. A Sprint 4 corrige isso com base em salários de mercado e custo real de contratação.

### Hardware foi subestimado
&emsp;Drones de entrada (R$ 800–R$ 1.500, como o DJI Tello usado na PoC) não são adequados para operação comercial real: ausência de GPS integrado, câmera de baixa qualidade, vida útil curta e nenhuma conformidade regulatória. A solução em produção exige equipamentos de nível profissional.

### Compliance não foi considerado
&emsp;Operar drones comercialmente acima de 400 pés exige licença, seguro e documentação. Esse custo foi ignorado na Sprint 1 por ainda não estar dentro do escopo da PoC.

### Benefícios não foram quantificados na Sprint 1
&emsp;A Sprint 1 calculou apenas custos, sem modelar o retorno. A Sprint 4 completa a análise com ROI, Payback e VPL, mostrando que — apesar do custo real ser muito maior que o estimado — o retorno potencial torna a solução amplamente viável.

---

## 6. Conclusão da Comparação

&emsp;A evolução entre as duas análises não representa um erro da Sprint 1, mas sim o amadurecimento natural do entendimento do projeto. A Sprint 1 cumpriu seu papel de estimar rapidamente a ordem de grandeza do investimento para um piloto. A Sprint 4 responde à pergunta correta: **quanto custaria e quanto valeria implantar isso de verdade?**

&emsp;A conclusão é que o custo real é significativamente maior do que o estimado inicialmente — mas o retorno potencial, quando modelado adequadamente, justifica o investimento com folga, mesmo em cenários conservadores.