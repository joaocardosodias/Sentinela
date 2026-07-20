---
sidebar_position: 1
title: Premissas
---

# Premissas da Análise Financeira

&emsp;Esta análise financeira tem como objetivo estimar a viabilidade econômica da **implementação em produção** da solução de recuperação de veículos roubados e furtados utilizando drones e visão computacional desenvolvida para a Pier.

&emsp;Como o projeto atual consiste em uma prova de conceito (PoC), algumas informações operacionais não estão disponíveis. Dessa forma, foram utilizadas premissas baseadas em pesquisas de mercado, documentação pública e estimativas da equipe, devidamente referenciadas na seção de [Fontes](./fontes.md).


## Escopo Considerado

&emsp;A análise considera um cenário de implantação operacional da solução, incluindo:

- Aquisição de drones para monitoramento em campo
- Infraestrutura computacional local (edge) e em nuvem
- Equipe técnica para desenvolvimento, manutenção e evolução da solução
- Operadores de drone para execução das missões
- Integração com sistemas internos da Pier
- Operação contínua do sistema ao longo de 5 anos

&emsp;**Não são considerados** nesta análise:

- Custos de desenvolvimento da prova de conceito acadêmica (absorvidos pelo projeto)
- Custos jurídicos específicos e eventuais processos administrativos não recorrentes.
- Expansão nacional da operação
- Integração com sistemas policiais ou base de dados governamentais

---

## Horizonte de Análise

&emsp;Será considerado um horizonte de operação de **5 anos**. Justificativas:

- Drones comerciais de nível profissional (ex.: DJI Mavic 3 Enterprise) possuem vida útil estimada entre 3 e 5 anos, dependendo da intensidade de uso e manutenção
- O período permite avaliar o retorno sobre investimento de médio prazo e capturar o ponto de equilíbrio (payback)
- É um horizonte usual em análises de viabilidade para projetos de tecnologia aplicada em seguradoras

---

## Cenários de Drone Avaliados

&emsp;A análise contempla **dois cenários de equipamento**, dado que o projeto foi desenvolvido com um drone de baixo custo (DJI Tello) e a solução produtiva exigiria equipamentos mais robustos:

| Cenário | Drone | Perfil |
|---|---|---|
| **Cenário Base** | DJI Mavic 3 Enterprise | Câmera 4K estabilizada, GPS integrado, alcance operacional real, adequado para operação profissional urbana |
| **Cenário Simplificado** | Drone intermediário (câmera 4K, GPS, sem certificação enterprise) | Equipamento mais acessível, menor alcance, maior limitação operacional |

> A diferença entre os cenários não é apenas de custo de aquisição — drones enterprise oferecem maior confiabilidade operacional, menor downtime e facilitam o processo de certificação junto à ANAC.

---

## Premissas Operacionais

| Premissa | Valor | Justificativa |
|---|---|---|
| Número de drones na operação inicial | 2 unidades | Drone principal em operação e drone reserva para contingência,
manutenção preventiva ou troca de baterias. |
| Missões por drone por mês | ~20 missões | Operação em dias úteis, média de 1 missão por dia útil por equipamento |
| Veículos identificados por missão | ~50 placas | Estimativa conservadora para varredura em área periférica |
| Ganho incremental de recuperação | +4 a +12 veículos/mês | Faixa utilizada nos cenários conservador, referência e otimista da análise financeira. |
| Indenização média evitada por veículo | R$ 50.000 | Referência à Tabela FIPE para carteira de veículos segurados pela Pier |
| Veículos roubados/furtados na carteira por mês | ~70 casos/mês | Dado fornecido pelo parceiro |

---

## Premissas de Equipe

| Perfil | Regime | Referência Salarial |
|---|---|---|
| Desenvolvedor Python sênior (backend + IA) | CLT ou PJ | R$ 12.000–R$ 15.000/mês (Robert Half, Glassdoor) |
| Desenvolvedor React sênior (frontend) | CLT ou PJ | R$ 12.000–R$ 18.000/mês (Robert Half) |
| Engenheiro de visão computacional / IA | PJ | R$ 15.000–R$ 35.000/mês (estimativa de mercado) |
| Piloto de drone (operador de campo) | CLT | R$ 3.500–R$ 5.650/mês (Glassdoor) |

&emsp;Para o custo real de contratação CLT, aplica-se um multiplicador de **~1,7× sobre o salário bruto**, considerando encargos, benefícios e overhead. Para PJ, considera-se contratação por hora/projeto com margem de overhead reduzida.

---

## Premissas de Infraestrutura

| Item | Referência |
|---|---|
| Banco de dados (Supabase Pro) | ~US$ 25/mês (plano base), mais US$ 0,021/GB acima da franquia |
| Storage (imagens e vídeos de evidência) | ~US$ 0,021/GB/mês após franquia |
| Volume estimado de storage/mês | 10–30 GB (upload condicional apenas de matches positivos) |
| Dados móveis corporativos (por operador) | R$ 70–R$ 100/mês — referência Vivo Empresas (40 GB = R$ 69,99; 100 GB = R$ 99,99) |

---

## Premissas Regulatórias

&emsp;A operação comercial com drones acima de 400 pés AGL exige licença específica (RBAC-E94, ANAC). Os custos de certificação, seguros operacionais, consultoria regulatória e treinamento dos pilotos são tratados como um **bloco de compliance** estimado separadamente, e não como taxa unitária fixa, dado que variam conforme o perfil de operação.

---

## Taxa de Desconto

&emsp;Para o cálculo do VPL (Valor Presente Líquido), adota-se uma taxa de desconto de **15% ao ano**, compatível com o custo de capital de empresas de tecnologia e insurtechs no Brasil em horizonte de médio prazo.

---

## Fonte das Premissas

&emsp;Todas as fontes que fundamentam estas premissas estão detalhadas na seção [Fontes](./fontes.md).