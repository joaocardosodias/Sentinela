---
sidebar_position: 2
title: CAPEX
---

# Investimento Inicial (CAPEX)

&emsp;O CAPEX contempla todos os custos necessários para colocar a solução em operação produtiva, incluindo desenvolvimento do sistema, aquisição de hardware e compliance regulatório.

&emsp;A análise apresenta **dois cenários de equipamento** — Cenário Base (DJI Mavic 3 Enterprise) e Cenário Simplificado (drone intermediário) — para evidenciar o impacto da escolha do hardware no investimento total e na capacidade operacional.

---

## 1. Hardware

### 1.1 Drones

&emsp;O drone é o componente central da operação em campo. A qualidade da câmera, a estabilidade do voo e a presença de GPS integrado impactam diretamente a acurácia do sistema de visão computacional e a confiabilidade das missões.

| Item | Cenário Base (Enterprise) | Cenário Simplificado | Observações |
|---|---|---|---|
| **Modelo de referência** | DJI Mavic 3 Enterprise | Drone intermediário 4K com GPS | — |
| **Custo unitário** | ~R$ 33.000 | ~R$ 8.000–R$ 12.000 | Base: revendas nacionais autorizadas |
| **Quantidade inicial** | 2 unidades | 2 unidades | Cobertura de turnos e manutenção rotativa |
| **Subtotal drones** | **R$ 66.000** | **R$ 16.000 – R$ 24.000** | — |

> **Por que 2 drones?** A operação inicial considera um drone principal em missão e um drone reserva para contingência, manutenção preventiva ou troca de baterias. Essa configuração garante continuidade operacional sem exigir investimento excessivo em redundância.

### 1.2 Acessórios e Periféricos

| Item                           | Custo Estimado         | Observações                                                   |
| ------------------------------ | ---------------------- | ------------------------------------------------------------- |
| Baterias extras (3 por drone)  | R$ 3.600–R$ 6.000     | Cada bateria enterprise ~R$ 600–R$ 800; 3 baterias × 2 drones |
| Cases e proteção de transporte | R$ 1.500–R$ 3.000      | Proteção para operação em campo                               |
| Carregadores e hubs de recarga | R$ 1.000–R$ 2.000      | Recarga paralela de baterias                                  |
| Modem/roteador portátil        | R$ 300–R$ 600          | 1 unidade para operação em campo                              |
| **Subtotal acessórios**        | **R$ 6.400–R$ 11.600** | —                                                             |

### 1.3 Estação de Trabalho (Edge Computing)

&emsp;O processamento de visão computacional pode ser centralizado em uma única estação de trabalho equipada com GPU dedicada, reduzindo custos de infraestrutura sem comprometer a operação do sistema.

| Item | Custo Estimado | Observações |
|---|---|---|
| Notebook com GPU dedicada | R$ 8.000–R$ 14.000 | GPU Nvidia série RTX, mínimo 8GB VRAM |
| Quantidade | 1 unidade | Estação compartilhada para processamento da operação |
| **Subtotal edge** | **R$ 8.000–R$ 14.000** | — |

---

## 2. Desenvolvimento do Sistema

&emsp;O custo de desenvolvimento considera a construção da solução completa para produção, partindo da PoC desenvolvida na graduação. Inclui hardening do sistema, integração com sistemas reais da Pier, pipeline de visão computacional otimizado, frontend operacional e backend cloud.

### 2.1 Perfis e Estimativas de Esforço

| Perfil | Horas Estimadas | Custo/hora (PJ) | Custo Total |
|---|---|---|---|
| Engenheiro de IA / Visão Computacional | 200–350 h | R$ 100–R$ 220/h | R$ 20.000–R$ 77.000 |
| Desenvolvedor Python sênior (backend) | 150–250 h | R$ 80–R$ 120/h | R$ 12.000–R$ 30.000 |
| Desenvolvedor React sênior (frontend) | 100–180 h | R$ 75–R$ 115/h | R$ 7.500–R$ 20.700 |
| **Total desenvolvimento** | **450–780 h** | — | **R$ 39.500–R$ 127.700** |

> **Nota:** O intervalo amplo reflete incertezas sobre o nível de integração exigido com sistemas internos da Pier. O cenário mínimo considera reaproveitamento expressivo da PoC; o máximo, uma refatoração mais profunda para produção.

### 2.2 Síntese do Desenvolvimento

| Cenário | Custo de Desenvolvimento |
|---|---|
| **Otimista** | R$ 39.500 |
| **Referência** | ~R$ 80.000 |
| **Conservador** | R$ 127.700 |

### 2.3 Prazo Estimado de Desenvolvimento e Implantação

&emsp;Considerando o volume de horas estimado e uma equipe pequena trabalhando em paralelo, o prazo até o início da operação é de aproximadamente:

| Etapa | Duração Estimada |
|---|---|
| Desenvolvimento (refatoração da PoC para produção) | 2–3 meses |
| Certificação ANAC do operador responsável | 1–2 meses |
| Testes de campo e ajustes finais | 2–4 semanas |
| **Total até início da operação** | **~3–4 meses** |

> Esse período concentra o "tempo morto" do investimento: a equipe já gera custo (parte do CAPEX de desenvolvimento), mas a operação ainda não gera o benefício de recuperação de veículos. Esse intervalo é considerado no cálculo de payback em [ROI, Payback e VPL](./roi-payback-vpl.md).

---

## 3. Compliance Regulatório (ANAC / RBAC-E94)

&emsp;A operação comercial de drones acima de 400 pés AGL exige habilitação específica do piloto responsável pela operação, seguros operacionais e conformidade com o RBAC-E94. Esses custos são tratados como bloco único de compliance inicial.

| Item                                                             | Custo Estimado          |
| ---------------------------------------------------------------- | ----------------------- |
| Cursos de habilitação (por piloto, 1 piloto)                     | R$ 1.000–R$ 2.000       |
| Seguros operacionais (responsabilidade civil, danos a terceiros) | R$ 6.000–R$ 15.000/ano  |
| Consultoria regulatória e documentação                           | R$ 5.000–R$ 10.000      |
| **Subtotal compliance**                                          | **R$ 12.000–R$ 27.000** |

---

## 4. Síntese do CAPEX

### Cenário Base (DJI Mavic 3 Enterprise)

| Categoria       | Mínimo         | Máximo         |
| --------------- | -------------- | -------------- |
| Drones          | R$ 66.000      | R$ 66.000      |
| Acessórios      | R$ 6.400       | R$ 11.600      |
| Edge computing  | R$ 8.000       | R$ 14.000      |
| Desenvolvimento | R$ 39.500      | R$ 127.700     |
| Compliance      | R$ 12.000      | R$ 27.000      |
| **CAPEX Total** | **R$ 131.900** | **R$ 246.300** |

### Cenário Simplificado (Drone Intermediário)

| Categoria       | Mínimo         | Máximo         |
| --------------- | -------------- | -------------- |
| Drones          | R$ 16.000      | R$ 24.000      |
| Acessórios      | R$ 6.400       | R$ 11.600      |
| Edge computing  | R$ 8.000       | R$ 14.000      |
| Desenvolvimento | R$ 39.500      | R$ 127.700     |
| Compliance      | R$ 12.000       | R$ 27.000      |
| **CAPEX Total** | **R$ 77.900**  | **R$ 197.300** |

---

## 5. Depreciação dos Ativos

&emsp;Os equipamentos são depreciados linearmente ao longo de sua vida útil estimada, conforme tabela abaixo. A depreciação compõe a análise de custo total ao longo dos 5 anos.

| Ativo | Vida Útil | Método | Depreciação Anual (Cenário Base) |
|---|---|---|---|
| Drones (enterprise) | 4 anos | Linear | R$ 16.500/ano |
| Notebooks com GPU | 4 anos | Linear | R$ 2.000–R$ 3.500/ano |
| Acessórios e periféricos | 3 anos | Linear | R$ 2.133–R$ 3.867/ano |

> No Cenário Simplificado, a vida útil dos drones intermediários é estimada em 3 anos, com depreciação mais acelerada e necessidade de reposição antes do fim do horizonte de análise.

---

## 6. Reposição de Drones ao Longo dos 5 Anos

&emsp;Dado o horizonte de análise de 5 anos e a vida útil dos equipamentos, o custo de reposição deve ser considerado:

| Cenário | Reposição esperada | Custo de reposição estimado |
|---|---|---|
| **Base (Enterprise)** | Início do Ano 5 | R$ 66.000 |
| **Simplificado** | Ano 4 | R$ 16.000–R$ 24.000 |

---

## Referências

- Preço DJI Mavic 3 Enterprise: revendas nacionais autorizadas (~R$ 33.000/un.)
- Salários e custo-hora de desenvolvimento: Glassdoor, Robert Half (detalhes em [Fontes](./fontes.md))
- Regulamentação: ANAC RBAC-E94, habilitação de pilotos remotos