---
sidebar_position: 1
title: Sprint 5
---

# Sprint 5

&emsp;A Sprint 5 consolidou a versão final do MVP do projeto. O trabalho concentrou-se em transformar os componentes desenvolvidos nas sprints anteriores em uma experiência mais utilizável em campo: controle do drone pelo dashboard, onboarding para os perfis de gestão, validação com usuários, investigação de deploy e reorganização técnica do pipeline.

&emsp;O foco da sprint não foi criar uma nova arquitetura do zero, mas fechar lacunas práticas encontradas durante os testes: pilotar o DJI Tello sem controle FPV dedicado, orientar usuários no primeiro acesso, evidenciar problemas de conectividade antes da falha total e separar melhor as responsabilidades do código para facilitar operação e manutenção.

## Objetivos

| Objetivo | Resultado esperado |
| --- | --- |
| Viabilizar o teste operacional com drone real | Permitir controle de voo do DJI Tello pelo dashboard, junto ao vídeo e à telemetria. |
| Reduzir fricção no primeiro acesso | Criar fluxos de onboarding para gestor remoto e gestor local. |
| Validar a solução com usuários | Executar roteiros de teste e registrar achados, métricas e pontos de melhoria. |
| Avaliar caminhos de publicação | Investigar o que deve ir para deploy e o que deve continuar como operação local de borda. |
| Melhorar manutenibilidade | Modularizar responsabilidades do pipeline de drone, banco local e sincronização. |

## Entregas

### Controle de voo pelo dashboard

&emsp;Foi implementado o controle do DJI Tello diretamente na tela de operação. O dashboard passou a oferecer comandos de decolagem, pouso, parada, deslocamento, altitude e rotação, integrados ao servidor WebRTC local. A decisão técnica foi manter o browser afastado do UDP do drone: o frontend envia ações de alto nível e o servidor local traduz para comandos do SDK por meio de uma allowlist.

&emsp;A entrega evoluiu durante os testes de campo. O controle discreto por botões foi complementado por modo contínuo via WebSocket, com comportamento de "segurar para mover e soltar para pairar", watchdog no servidor e parada ao perder conexão. Isso tornou a pilotagem mais próxima de um joystick/arcade e mais adequada para enquadrar placas em movimento.

**Artefato:** [Controle de Voo pelo Dashboard](./controle-voo-dashboard.md)

### Onboarding de primeiro acesso

&emsp;Foram criados dois fluxos guiados de onboarding no frontend React + Vite. O primeiro atende o gestor remoto, conduzindo a jornada de Central de Alertas, verificação, veículos confirmados e veículos recusados. O segundo atende o gestor local, explicando a tela de operação com vídeo ao vivo, telemetria e mapa.

&emsp;Os tours usam elementos reais da interface marcados com `data-tour`, persistem conclusão no `localStorage` e evitam simular telas críticas. A solução preserva componentes dinâmicos como vídeo, cards de telemetria e mapa, usando imagens apenas como prévias dentro dos popups.

**Artefato:** [Onboarding de Primeiro Acesso](./onboarding-primeiro-acesso.mdx)

### Testes com usuários

&emsp;A sprint registrou testes em duas fases: uma validação interna com a equipe de desenvolvimento e uma rodada com cinco alunos do Inteli sem envolvimento no projeto. Os roteiros avaliaram qualidade das imagens, fluxo da Central de Alertas e monitoramento de conectividade dos drones.

&emsp;Os resultados indicaram que a qualidade das imagens foi aprovada e que o fluxo da Central de Alertas funciona, mas ainda exige melhorias de clareza e feedback visual. O principal ponto reprovado foi o monitoramento de conectividade: usuários não conseguiram identificar estado de sinal fraco antes da queda total da conexão.

**Artefato:** [Resultados dos Testes de Usuário](./Testes/resultados-testes-usuario.md)

### Investigação de deploy

&emsp;Foi analisado como o projeto deve ser publicado considerando sua arquitetura híbrida. A conclusão foi que documentação, frontend, backend e banco se beneficiam de deploy estruturado, enquanto a camada de drone, WebRTC, YOLO/OCR e scripts de rede deve ser tratada como operação local de borda.

&emsp;A recomendação final é adotar um deploy seletivo: GitLab Pages para documentação, build/publicação para frontend e backend em ambiente apropriado de produção, mantendo scripts e validações locais para o computador conectado ao Tello.

**Artefato:** [Investigação de Deploy](./investigacao_deploy.md)

### Refatoração e organização técnica

&emsp;A sprint também documentou a remoção do antigo `drone_pipeline.py` como monólito e a redistribuição de suas responsabilidades entre módulos mais específicos. O servidor WebRTC passou a concentrar o runtime de vídeo/controle, enquanto a fila local, sincronização e reconhecimento de placas ficaram separados em módulos próprios.

&emsp;No fechamento do período, também houve reorganização estrutural de pastas e arquivos, separando dados, CLI, banco, drone, visão computacional e testes. Essa organização reduz acoplamento e torna mais claro onde cada parte do sistema deve evoluir.

**Artefato:** [Modularização e remoção do drone_pipeline.py](./Refatoração/drone-pipeline-modularizacao.md)

## Artefatos

| Área | Documento |
| --- | --- |
| Operação com drone | [Controle de Voo pelo Dashboard](./controle-voo-dashboard.md) |
| Experiência do usuário | [Onboarding de Primeiro Acesso](./onboarding-primeiro-acesso.mdx) |
| Testes | [Resultados dos Testes de Usuário](./Testes/resultados-testes-usuario.md) |
| Deploy | [Investigação de Deploy](./investigacao_deploy.md) |
| Refatoração | [Modularização e remoção do drone_pipeline.py](./Refatoração/drone-pipeline-modularizacao.md) |

## Principais decisões

| Decisão | Justificativa |
| --- | --- |
| Manter o controle do Tello no servidor local | O browser não deve enviar comandos UDP diretamente ao drone; o servidor aplica allowlist e limites. |
| Tornar o modo contínuo padrão no controle de voo | A pilotagem por passos discretos era menos natural para enquadrar placas durante o voo. |
| Criar onboardings separados por perfil | Gestor remoto e gestor local têm jornadas diferentes e precisam de instruções específicas. |
| Tratar deploy como arquitetura híbrida | Nem tudo deve ir para nuvem; a borda depende de hardware, Wi-Fi do Tello e baixa latência. |
| Remover o monólito gradualmente | A fila local de detecções precisava continuar sendo alimentada antes de apagar `drone_pipeline.py`. |

## Resultados e aprendizados

&emsp;A Sprint 5 deixou o MVP é a versão final do projeto entregue para a Pier: o drone pode ser pilotado pela própria interface, os gestores recebem orientação contextual e os principais fluxos foram testados.