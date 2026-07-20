---
sidebar_position: 1
title: Resultados dos Testes de Usuário
---

# Resultados dos Testes de Usuário

&emsp;Esta página reúne os resultados das sessões de teste com usuários realizadas na Sprint 5. Cada sessão tem duração máxima de 20 minutos. Um integrante da equipe observa e preenche as tabelas abaixo durante ou imediatamente após cada sessão. Os participantes externos são identificados de forma anonima.

---

## Fase 1 — Equipe de Desenvolvimento

&emsp;A equipe realizou os três roteiros em conjunto, numa única sessão, com o sistema rodando em ambiente local. O objetivo foi mapear pontos de atrito evidentes antes de expor o produto a participantes externos. Durante a sessão, os membros revezaram quem interagia com a interface enquanto os demais observavam e anotavam. As discussões que surgiram durante a execução estão registradas nas observações de cada roteiro.

---

### TV-01 — Qualidade das Imagens

**Sessão:** grupo completo | **Imagens avaliadas:** 20 | **Aprovadas:** 17 (85%)

**Desenvolvimento da sessão:**

&emsp;A equipe avaliou as imagens em conjunto, discutindo cada caso antes de classificar. As 12 imagens com boa iluminação e captura frontal foram classificadas unanimemente como _"adequada para evidência"_ os caracteres estavam legíveis, o veículo identificável e o enquadramento adequado.

&emsp;As 5 imagens em condições intermediárias (iluminação levemente reduzida ou ângulo leve de 10°) geraram debate interno. A equipe decidiu classificá-las como _"aceitável com ressalvas"_, documentando que seriam suficientes para uso operacional mas não para laudo formal sem complementação de outra imagem do mesmo veículo.

&emsp;As 3 imagens reprovadas compartilhavam dois problemas combinados: baixa iluminação (capturada em área coberta) e ângulo lateral acentuado (~25–30°), fazendo com que parte da placa ficasse parcialmente ocluída pelo paralama do veículo.

&emsp;**Achado:** a equipe identificou a ausência de um indicador de qualidade de imagem na interface — o operador não tem como saber, ao receber o alerta, se a imagem de evidência armazenada é nítida ou não sem abri-la manualmente. Sugestão: exibir um ícone de aviso no card do alerta quando a nitidez estiver abaixo do limiar calculado pelo pipeline.

**Resultado: Aprovado** (critério: >= 80% — obtido 85%).

---

### TV-02 — Fluxo da Central de Alertas

**Sessão:** grupo completo | **Concluiu sem ajuda?** Sim | **Tempo total:** 2 min 14 s

**Desenvolvimento da sessão:**

&emsp;Um integrante assumiu o papel de operador e executou o fluxo enquanto os demais observavam em silêncio. O login foi realizado sem dificuldade (18 s). A navegação até a Central de Alertas levou cerca de 35 s — o integrante foi primeiro para o dashboard de operações antes de localizar o item correto no menu lateral.

&emsp;A listagem de alertas pendentes foi encontrada corretamente. O integrante abriu os detalhes do primeiro alerta e leu em voz alta os campos: placa, zona, data/hora e imagem.

&emsp;A ação de aprovação foi executada em 11 s. O grupo notou que podia ter um feedback visual ou sonoro confirmando a ação ,o alerta simplesmente desapareceu da lista. A rejeição do segundo alerta foi executada em 9 s, com a mesma ausência de feedback.

&emsp;**Achados:**
- Caminho até a Central de Alertas não é intuitivo para quem não conhece o sistema. (Tutorial vai servir para isso)
- Ausência de feedback visual/sonoro ao confirmar aprovação ou rejeição.
- O botão "Rejeitar" tem cor cinza neutra, o que pode passar a impressão de estar desabilitado.

**Resultado: Aprovado** (critério: &lt;= 3 min — obtido 2 min 14 s, sem assistência).

---

### TV-03 — Monitoramento de Conectividade dos Drones

**Sessão:** grupo completo | **Identificou problema de conectividade?** Parcialmente

**Desenvolvimento da sessão:**

&emsp;Durante a sessão, a equipe observou o comportamento da interface em dois estados distintos de conectividade. Quando o drone está operando normalmente, a tela exibe os dados de telemetria atualizados corretamente. Quando a conexão cai por completo o drone para de enviar qualquer dado o sistema eventualmente reflete o estado `offline` e a equipe consegue identificar o problema na interface.

&emsp;O ponto crítico identificado foi o estado intermediário: **quando a conectividade está fraca, mas ainda presente, a interface não dá nenhuma indicação disso**. O sinal de Wi-Fi do drone pode estar degradado, os pacotes de telemetria chegando com atraso ou de forma intermitente, e a tela continua exibindo tudo como normal. A equipe só consegue saber que havia um problema depois que a conexão cai de vez. Não existe, na interface atual, nenhum indicador de qualidade de sinal, latência de telemetria ou instabilidade de conexão.

&emsp;**Achados:**
- Conectividade fraca é completamente invisível na interface o operador não recebe nenhum sinal de alerta prévio.
- A detecção de problema só ocorre após queda total da conexão.
- Não há indicador de qualidade de sinal, instabilidade ou latência de telemetria.
- O card do drone deveria sinalizar degradação progressiva antes da queda, não apenas o estado final.

**Evidências da sessão:**

![Painel de informações do drone mostrando conectividade Wi-Fi ativa e bateria em 81%](/img/sprint-5/testes/imagem_info_drone.jpg)

*Painel de informações do drone durante a sessão: conectividade exibida como "Wi-Fi" com indicador verde e bateria em 81%. Nenhum sinal visual de degradação, mesmo com o drone próximo ao limite de alcance.*

![Tela do Gestor da Operação com feed de vídeo ao vivo](/img/sprint-5/testes/image_camera_drone.jpg)

*Tela principal do Gestor da Operação durante o teste: feed de vídeo ativo com indicador "AO VIVO". O erro HTTP 401 visível no topo foi identificado durante a sessão como resultado de uma tentativa de operação com sessão expirada.*

**Resultado: Reprovado** (critério: problema de conectividade identificável em &lt;= 30 s — não detectável no estado intermediário de sinal fraco).

---

## Fase 2 — Alunos do Inteli

&emsp;Sessões realizadas com 5 alunos do campus do Inteli sem envolvimento no projeto. Um integrante da equipe atuou como observador silencioso, registrando tempos sem interferir nas tarefas. Os participantes receberam apenas a instrução: _"Você é um operador de segurança. Use o sistema como achar necessário."_

### TV-01 — Qualidade das Imagens

| Participante | Imagens avaliadas | Aprovadas (%) |
|---|---|---|
| 1 | 20 | 90% |
| 2 | 20 | 80% |
| 3 | 20 | 85% |
| 4 | 20 | 85% |
| 5 | 20 | 80% |

**Resultado TV-01 (Fase 2): Aprovado** — todos os 5 participantes atingiram >= 80% de aprovação. Média: 84%.

---

### TV-02 — Fluxo da Central de Alertas

| Participante | Concluiu sem ajuda? | Tempo total |
|---|---|---|
| 1 | Sim | 2 min 31 s |
| 2 | Sim | 1 min 58 s |
| 3 | Sim | 2 min 47 s |
| 4 | Sim | 1 min 44 s |
| 5 | Não | 3 min 52 s |

**Resultado TV-02 (Fase 2): Aprovado com ressalva** — 4 de 5 participantes concluíram dentro do critério. O participante 5 ultrapassou o tempo e precisou de assistência.

---

### TV-03 — Monitoramento de Conectividade dos Drones

| Participante | Identificou problema de conectividade? | Tempo |
|---|---|---|
| 1 | Não | — |
| 2 | Não | — |
| 3 | Não | — |
| 4 | Não | — |
| 5 | Não | — |

**Resultado TV-03 (Fase 2): Reprovado** — nenhum participante identificou o estado de conectividade fraca. Confirmação externa do achado da Fase 1.

---

## Resumo Final

| Roteiro | Critério de aceite | Resultado Fase 1 | Resultado Fase 2 | Veredicto |
|---|---|---|---|---|
| TV-01 | >= 80% das imagens aprovadas | 85% | 84% médio (5/5) | Aprovado |
| TV-02 | Fluxo completo em &lt;= 3 min sem assistência | 2 min 14 s | 4/5 dentro do critério | Aprovado com ressalva |
| TV-03 | Problema de conectividade identificável em &lt;= 30 s | Não detectável (sinal fraco) | Não detectável (5/5) | Reprovado |

&emsp;O TV-03 permanece reprovado de forma consistente entre a equipe e os participantes externos. O problema central não é apenas a queda total de conexão, mas a ausência de qualquer indicador de degradação progressiva de sinal o operador só descobre o problema depois que a conexão já morreu. O TV-02, aprovado com ressalva, aponta ajustes pontuais de interface: clareza na nomenclatura de alertas pendentes vs. aprovados, feedback visual ao confirmar ações e conversão do timestamp para horário local.
