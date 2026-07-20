---
sidebar_position: 6
title: "Frontend: Sistema de Notificações Pop-up"
description: "Implementação de alertas dinâmicos em tempo real para o painel do Analista Pier."
---

# Frontend: Sistema de Notificações Pop-up

## Visão Geral

Durante a Sprint 5, foi implementado um sistema de notificações visuais em tempo real no painel web da Pier Recovery UI, focado na tela da Central de Alertas. O objetivo principal é garantir que o analista de operações receba alertas visuais imediatos sempre que uma nova detecção de veículo roubado chegar ao banco de dados ou quando uma ação de validação for concluída.

---

## Justificativa

Anteriormente, o painel do analista possuía duas limitações críticas de usabilidade e eficiência operacional:

1. **Falta de Alertas em Tempo Real:** O analista precisava atualizar a página manualmente para verificar se o drone havia detectado um novo veículo roubado. Isso gerava atrasos no tempo de resposta a incidentes críticos.
2. **Feedback Estático e Pouco Intuitivo:** As mensagens de aprovação ou recusa de alertas eram exibidas de forma estática no topo da página, consumindo espaço útil da lista de cards e não oferecendo destaque adequado para confirmações operacionais.

Com a adoção de notificações flutuantes dinâmicas, a interface passa a se comportar de maneira reativa e orientada a eventos, melhorando drasticamente a ergonomia e o tempo de reação da equipe.

---

## O que foi feito?

O sistema foi estruturado para atuar em duas frentes principais de comunicação visual com o usuário:

### 1. Detecção Automática de Novos Alertas
Foi configurado um mecanismo de consulta contínua em plano de fundo na Central de Alertas.
* **Frequência:** O sistema realiza verificações periódicas automáticas em busca de novos alertas confirmados pela API externa.
* **Inteligência de Estado:** A interface mantém um histórico em memória dos alertas já exibidos na sessão atual.
* **Disparo da Notificação:** Caso a consulta identifique registros inéditos, um alerta visual flutuante é gerado no canto superior direito da tela.

![Exemplo de notificação de novo alerta de roubo](/img/alertaroubopopup.png)

### 2. Notificações de Validação Operacional
Quando o analista avalia uma ocorrência na interface de verificação e toma uma decisão operacional, o sistema emite uma confirmação visual imediata:

* **Resgate Aprovado:** Exibe uma notificação de sucesso confirmando que o veículo foi transferido para a lista de ocorrências aceitas.

![Exemplo de notificação de resgate aprovado](/img/confirmadopopup.png)

* **Alerta Recusado:** Exibe uma notificação informando que a detecção da placa foi descartada da fila de análise.

![Exemplo de notificação de alerta recusado](/img/recusadopopup.png)
