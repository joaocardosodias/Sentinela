---
sidebar_position: 5
title: Wireframe
---

# Proposta de Interface de Usuário (UI/UX)

A interface de usuário construída para este projeto não é apenas um conjunto de telas, mas a materialização de toda a proposta de solução. O objetivo principal do nosso design é guiar o usuário naturalmente até a solução do seu problema, garantindo a definição clara de uma hierarquia de informação: o que cada usuário precisa ver e em que ordem.

Para chegar à excelência, adotamos um processo iterativo, desenvolvendo uma versão inicial (V1) que foi posteriormente questionada e refinada para uma versão final (V2) baseada em funções.

É possível verificar wireframe na integra no Figma em: [Link](https://www.figma.com/design/upsUjhL9Dt37KqLcbainaG/Wireframe---Low-fid?node-id=0-1&t=QmhVU3l53q808bAN-1)

---

## Primeira Iteração: V1 - Visão Unificada (Descartada)

O objetivo deste primeiro wireframe foi criar um "Super Dashboard". A premissa era unificar todas as pontas do sistema em uma única plataforma gerencial, onde o usuário pudesse acompanhar tanto a saúde do hardware (drones) quanto a entrega de valor do negócio (recuperação de veículos).

### Fluxo de Telas e Navegação (V1)

**1. Tela de Login**
Ponto de entrada seguro do sistema. O usuário insere e-mail/senha e o clique em "Login" redireciona para a Tela Inicial.

<div align="center">Figura 1: Tela Login</div>
<div align="center">![Tela Login](/img/sprint-1/Tela_Login.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

**2. Tela Inicial - Operações**
Fornece uma visão macro de todas as frentes de busca ativas simultaneamente. A tela agrupa os dados por "Operações" (ex: Operação 1, Operação 2). O clique em qualquer card direciona para o detalhamento tático do voo.

<div align="center">Figura 2: Tela Operações</div>
<div align="center">![Tela Operações](/img/sprint-1/tela%20operações.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

**3. Dashboard da Operação: Abas de Scans e Rota**
*   **Scans:** Exibe em tempo real as placas lidas. Definimos uma hierarquia visual onde veículos limpos ficam com fundo neutro, e placas com registro de roubo saltam aos olhos com fundo vermelho ("Alerta"), materializando o requisito de gerar notificações.
*   **Rota:** Um mapa exibe o trajeto do drone, ajudando a garantir que ele cubra a região pré-definida.

<div align="center">Figura 3: Tela Scan Operação</div>
<div align="center">![Tela Scan Operação](/img/sprint-1/tela%20scan%20operação.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

<div align="center">Figura 4: Tela Rota Operação</div>
<div align="center">![Tela Rota Operação](/img/sprint-1/tela%20rota%20operação.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

**4. Visão Global: Alertas e Localização**
Permite que um supervisor veja os "Matches Positivos" de todas as operações ao mesmo tempo no menu lateral ("Global"), sem precisar entrar em cada card individualmente.

<div align="center">Figura 5: Tela Alertas Globais</div>
<div align="center">![Tela Alertas Globais](/img/sprint-1/tela%20alertas%20globais.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

<div align="center">Figura 6: Tela Localização Global</div>
<div align="center">![Tela Localização Global](/img/sprint-1/tela%20localização%20global.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

**5. Health Check e Tratamento de Falhas**
Para responder à exigência de como o sistema comunica suas falhas, criamos modais específicos para notificar problemas como Bateria Baixa ou Perda de Conectividade ao clicar no botão presente no topo superior direito das telas de operações. Você também poderia ver informações de cada drone como localização e scans.

<div align="center">Figura 7: Tela Alertas</div>
<div align="center">![Tela Alertas](/img/sprint-1/tela%20alertas.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

<div align="center">Figura 8: Tela Drone Info</div>
<div align="center">![Tela Drone Info](/img/sprint-1/tela%20drone%20info.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

<div align="center">Figura 9: Tela Drones da Operação</div>
<div align="center">![Tela Drones da Operação](/img/sprint-1/tela%20drones%20da%20operação.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

---

## A Decisão de Pivotar (Avanço para a V2)

Embora a V1 cobrisse os requisitos técnicos, percebemos que ela falhava no principal critério de uma interface excelente: a clareza na hierarquia de informação. 

Ao tentar sanar as necessidades das personas do **Gestor de Frota** (focado no voo e telemetria) e do **Gestor da Pier** (focado apenas no dado do roubo) na mesma estrutura, a interface exigia muitos cliques e causava sobrecarga cognitiva. Demonstrando um processo iterativo e de agilidade real, pivotamos para uma arquitetura segregada por *Roles* (Papéis).

---

## Segunda Iteração: V2 - Foco em Personas (Proposta Final)

O sistema agora possui um ponto de entrada único (Login) que redireciona o usuário para um painel otimizado especificamente para a sua função, eliminando distrações e focando na ação.

### 1. Ponto de Entrada
A autenticação define o roteamento da interface com base no nível de acesso do usuário.

<div align="center">Figura 10: Tela Login</div>
<div align="center">![Tela Login](/img/sprint-1/Tela_Login.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

### 2. Painel do Gestor da Operação (Equipe de Campo)
*   **Persona:** Operador técnico da frota.
*   **Objetivo:** Garantir que o drone siga a rota e que a captura de imagens esteja operante.
*   **Decisões de UI:**
    *   **Health Check Integrado:** Exibe ID, Status, Conectividade e Bateria de forma direta.
    *   **Feed de Câmera Ampliável:** A tela apresenta o feed de vídeo em tempo real. O usuário pode clicar na área do vídeo para amplificar a câmera, facilitando a visualização de obstáculos.
    *   **Mapa de Macro Rota:** Mapa tático exibindo pontos de interesse e altitude.
    *   **Justificativa:** Removemos qualquer dado de sinistro daqui. O operador de voo não aciona a polícia, logo, esses dados apenas poluiriam sua tela.

<div align="center">Figura 11: Tela Gestor Operação</div>
<div align="center">![Tela Gestor Operação](/img/sprint-1/Tela_Gestor_de_Drones.png)</div>
<div align="center">Fonte: Autores, 2026.</div>

### 3. Painel do Gestor Pier (Central de Sinistros / Base)
*   **Persona:** Analista de operações internas da Pier.
*   **Objetivo:** Monitorar alertas e acionar a recuperação.
*   **Decisões de UI:**
    *   **Divisão Binária:** Hierarquia clara entre o que exige atenção imediata (Alertas Críticos em vermelho no topo) e o que é apenas auditoria (Veículos Limpos em branco embaixo).
    *   **Notificação de Match:** Cards vermelhos indicam roubo/furto, contendo Data/Hora, Placa e Localização.
    *   **A Prova Visual (Foto):** Os alertas positivos incluem a foto extraída no exato momento da identificação do carro. O analista usa isso como prova material para evitar falsos positivos antes de acionar o resgate. Veículos "Limpos" não carregam foto para economizar banda.
    *   **Justificativa:** Para a Pier, a solução foca apenas nos dados entregues. A interface entrega exatamente o que o negócio precisa para reduzir a sinistralidade.
    
    Os alertas em vermelho indicam os placas com registro de roubo/furto. Já os indicados como limpo são as leituras de placas sem registro de roubo/furto. 

<div align="center">Figura 12: Tela Gestor Pier</div>
<div align="center">![Tela Gestor Operação](/img/sprint-1/Tela%20Gestor%20Pier.png)</div>
<div align="center">Fonte: Autores, 2026.</div>
