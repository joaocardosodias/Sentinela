---
sidebar_position: 3
title: OPEX
---

# Custos Operacionais (OPEX)

&emsp;O OPEX contempla as despesas recorrentes necessárias para manter a solução em operação. A estrutura de custos é apresentada em base mensal e anual, segmentada por categoria.

&emsp;Assim como no CAPEX, a análise diferencia o **Cenário Base** (drones enterprise, operação mais robusta) do **Cenário Simplificado**, dado que a escolha do equipamento influencia custos de manutenção, seguro e confiabilidade operacional.

---

## 1. Equipe

&emsp;O principal custo recorrente da solução é a operação humana. Para a fase inicial (operação com 2 drones), a equipe mínima necessária é composta por um operador habilitado responsável pela execução das missões e pelo monitoramento da operação.

### 1.1 Operadores de Drone

&emsp;Pilotos remotos habilitados pela ANAC, responsáveis pelas missões de campo.

| Perfil          | Qtd | Salário Bruto/mês | Custo Real CLT (~1,7×) | Total/mês    |
| --------------- | --- | ----------------- | ---------------------- | ------------ |
| Piloto de drone | 1   | R$ 4.500          | R$ 7.650               | **R$ 7.650** |


> Referência salarial: Glassdoor aponta média de R$ 5.650/mês para pilotos com perfil comercial. Adotamos R$ 4.500 como base conservadora para operações de segurança/vigilância. O fator 1,7× sobre o salário bruto reflete encargos (FGTS, INSS patronal, férias, 13°, etc.).

### 1.2 Equipe de Tecnologia (Manutenção e Evolução)

&emsp;Após o desenvolvimento inicial, a solução exige manutenção contínua, ajustes no modelo de visão computacional e evolução incremental.

| Perfil                        | Regime | Dedicação           | Custo/mês         |
| ----------------------------- | ------ | ------------------- | ----------------- |
| Desenvolvedor Full Stack / IA | PJ     | Parcial (~40 h/mês) | R$ 4.000–R$ 6.000 |

> A manutenção pós-implantação demanda apenas suporte pontual, correções e pequenos ajustes evolutivos, justificando a dedicação parcial de aproximadamente 40 horas mensais.

### 1.3 Síntese — Equipe

| Categoria         | Mínimo/mês    | Máximo/mês    |
| ----------------- | ------------- | ------------- |
| Operador de drone | R$ 7.650      | R$ 7.650      |
| Equipe técnica    | R$ 4.000      | R$ 6.000      |
| **Total equipe**  | **R$ 11.650** | **R$ 13.650** |

---

## 2. Infraestrutura Cloud

&emsp;A arquitetura adota upload condicional — apenas evidências de matches positivos são enviadas à nuvem — o que mantém o custo de infraestrutura controlado mesmo em volumes operacionais relevantes.

| Item | Custo/mês | Observações |
|---|---|---|
| Supabase Pro (banco + storage base) | ~R$ 140 | US$ 25/mês convertido; inclui franquia de storage e banco |
| Storage adicional (evidências fotográficas) | R$ 10–R$ 50 | ~10–30 GB/mês além da franquia (upload condicional) |
| Servidor de API remota | R$ 100–R$ 250 | Instância de médio porte para backend cloud |
| CDN e tráfego de saída | R$ 20–R$ 80 | Acesso ao dashboard remoto pela Pier |
| **Total cloud** | **R$ 270–R$ 520/mês** | — |

---

## 3. Conectividade de Campo

&emsp;Cada operador em campo necessita de plano de dados móveis corporativo para comunicação com o backend cloud durante as missões (upload de evidências, consulta à API da Pier).

| Item | Custo/mês | Referência |
|---|---|---|
| Plano de dados 4G corporativo (por operador) | R$ 70–R$ 100 | Vivo Empresas: 40 GB = R$ 69,99; 100 GB = R$ 99,99 |
| Quantidade de operadores | 1 | — |
| **Total conectividade** | **R$ 70–R$ 100/mês** | — |

---

## 4. Manutenção de Equipamentos

&emsp;Os custos de manutenção variam conforme o drone utilizado. Equipamentos enterprise possuem maior valor de peças, mas menor frequência de falhas.

| Item | Cenário Base | Cenário Simplificado |
|---|---|---|
| Reposição de peças (hélices, motores, gimbal) | R$ 600–R$ 1.200/mês | R$ 300–R$ 800/mês |
| Manutenção preventiva e calibração | R$ 400–R$ 800/mês | R$ 200–R$ 500/mês |
| Seguro dos equipamentos | R$ 500–R$ 1.000/mês | R$ 200–R$ 500/mês |
| **Subtotal manutenção** | **R$ 1.500–R$ 3.000/mês** | **R$ 700–R$ 1.800/mês** |

---

## 5. Custos Operacionais Diversos

| Item | Custo/mês | Observações |
|---|---|---|
| Energia elétrica (recarga de baterias, estação de trabalho) | R$ 80–R$ 150 | 1 estação de trabalho + carregadores de bateria |
| Licenças de software (ex.: plataformas de telemetria, mapas) | R$ 200–R$ 500 | Ferramentas de gestão de missão e análise |
| **Total diversos** | **R$ 280–R$ 650/mês** | — |

---

## 6. Síntese do OPEX

### Cenário Base (DJI Mavic 3 Enterprise)

| Categoria | Mínimo/mês | Máximo/mês | Mínimo/ano | Máximo/ano |
|---|---|---|---|---|
| Equipe | R$ 11.650 | R$ 13.650 | R$ 139.800 | R$ 163.800 |
| Infraestrutura cloud | R$ 270 | R$ 520 | R$ 3.240 | R$ 6.240 |
| Conectividade de campo | R$ 70 | R$ 100 | R$ 840 | R$ 1.200 |
| Manutenção de equipamentos | R$ 1.500 | R$ 3.000 | R$ 18.000 | R$ 36.000 |
| Diversos | R$ 280 | R$ 650 | R$ 3.360 | R$ 7.800 |
| **OPEX Total** | **R$ 13.770** | **R$ 17.920** | **R$ 165.240** | **R$ 215.040** |

### Cenário Simplificado (Drone Intermediário)

| Categoria | Mínimo/mês | Máximo/mês | Mínimo/ano | Máximo/ano |
|---|---|---|---|---|
| Equipe | R$ 11.650 | R$ 13.650 | R$ 139.800 | R$ 163.800 |
| Infraestrutura cloud | R$ 270 | R$ 520 | R$ 3.240 | R$ 6.240 |
| Conectividade de campo | R$ 70 | R$ 100 | R$ 840 | R$ 1.200 |
| Manutenção de equipamentos | R$ 700 | R$ 1.800 | R$ 8.400 | R$ 21.600 |
| Diversos | R$ 280 | R$ 650 | R$ 3.360 | R$ 7.800 |
| **OPEX Total** | **R$ 12.970** | **R$ 16.720** | **R$ 155.640** | **R$ 200.640** |

> **Observação:** O OPEX entre os dois cenários permanece relativamente próximo porque a maior parcela do custo operacional está associada à equipe humana, que representa aproximadamente 75% a 85% do OPEX total. A principal diferença entre os cenários está relacionada aos custos de manutenção e reposição dos equipamentos.

---

## Referências

- Salários: Glassdoor, Robert Half (detalhes em [Fontes](./fontes.md))
- Conectividade: Vivo Empresas — planos corporativos 4G
- Infraestrutura: Supabase Pricing (supabase.com/pricing)