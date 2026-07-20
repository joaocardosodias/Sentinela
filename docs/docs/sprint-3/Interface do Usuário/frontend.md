---
sidebar_position: 1
title: Frontend
---

# Frontend 

Documentação do desenvolvimento frontend do sistema de recuperação de veículos da Pier Seguradora. Lembrando que ao final da sprint nós decidimos que não vamos fazer um log com todos os carros limpos, apenas carros limpos que foram inicialmente colocados como roubados iram aparecer na parte de baixo como limpos, os que inicialmente são escaneados e foram para o limpo, são descartados.

---

## Visão Geral

O frontend é uma aplicação web estática construída em **React 18 + Vite 5**, com navegação baseada em estado (sem React Router) e estilização via inline styles. Não há dependência de biblioteca de UI externa — o design foi implementado do zero com as cores do site da marca da Pier.

**Paleta de cores:**
- `#FF3366` — rosa Pier (cor primária, alertas, ações)
- `#1A1F36` — azul escuro (sidebar, fundos)
- `#0D1025` — fundo principal das telas

---

## Evolução do Design

### Wireframes (Low-Fidelity)

Os wireframes iniciais definiram o layout e o fluxo entre as telas, servindo de referência para as decisões estruturais do sistema. Tivemos apenas uma pequena modificação na tela do gestor da Pier onde adicionamos como queriamos a Tela de aceitar ou não se o carro realmente é um carro roubado ou caso foi um erro do modelo.

**Tela de Login:**

![Wireframe Login](/img/sprint-3/interface/Tela_Login.png)

**Tela do Gestor de Operação (Drone):**

![Wireframe Gestor de Drones](/img/sprint-3/interface/Tela_Gestor_de_Drones.png)

**Tela do Gestor da Pier:**

![Wireframe Gestor da Pier](/img/sprint-3/interface/GestorDaPierUpdate.png)
---

### Protótipo High-Fidelity (Gerado por IA)

O protótipo de alta fidelidade foi gerado com auxílio de inteligência artificial (nesse caso usamos o Gemini). Entretanto, **não atendeu às expectativas** por dois motivos principais:

1. **Cores incorretas** — a IA utilizou tons de azul claro e teal em vez do rosa `#FF3366` e do azul escuro `#1A1F36` da identidade visual da Pier.
2. **Sidebar com ícones desnecessários** — o protótipo adicionou múltiplas abas na sidebar que não fazem parte do fluxo definido, tornando a interface confusa e inconsistente com os papéis de usuário do sistema.

**HIFI — Login:**

![HIFI Login](/img/sprint-3/interface/Login_HIFI.png)

**HIFI — Gestor de Drones:**

![HIFI Gestor de Drones](/img/sprint-3/interface/GestorDeDrone_HIFI.png)

**HIFI — Gestor de Operação Pier:**

![HIFI Gestor de Operação](/img/sprint-3/interface/GestorOperação_HIFI.png)

---

### Implementação Final

A implementação final foi desenvolvida em React seguindo as cores corretas da Pier e o fluxo de papéis definido. A sidebar exibe abas de navegação **somente para o Analista Pier**, e a sidebar do Gestor de Campo exibe apenas a logo e o botão de logout.

---

## Telas

### Login

Rota de entrada do sistema. Layout dividido em dois painéis:
- **Painel esquerdo:** fundo escuro com logo e slogan da Pier.
- **Painel direito:** formulário de autenticação com campos de e-mail e senha.

Na parte inferior do formulário, dois botões de atalho permitem acessar diretamente as telas de demonstração sem credenciais reais:
- **Entrar como Gestor de Campo** → navega para `OperationsManager`
- **Entrar como Analista Pier** → navega para `AlertCenter`

![Tela Login](/img/sprint-3/interface/Tela_Login.png)

---

### Gestor de Operação (`OperationsManager`)

Tela destinada ao Gestor de Campo que opera o drone.

**Componentes da tela:**
- **Feed da câmera:** placeholder preto com animação de pulso verde (`livePulse`) indicando transmissão ao vivo, e overlay com coordenadas GPS simuladas.
- **Cards de telemetria:** Drone ID, status de conectividade e percentual de bateria.
- **Mapa de pré-visualização:** área clicável que abre um modal com grade CSS simulando um mapa, incluindo círculo tracejado representando o raio de cobertura do drone.

A sidebar desta tela exibe apenas a logo Pier e o botão de logout — sem abas de navegação.

![Tela Gestor Operações](/img/sprint-3/interface/Tela_Gestor_de_Drones.png)

---

### Central de Alertas (`AlertCenter`)

Tela principal do Analista Pier. Dividida em duas seções verticais:

**Seção superior — Alertas Ativos:**
- Cards vermelhos com informações do veículo suspeito: placa, modelo, cor, drone responsável e localização.
- Clicar em um card abre o **Modal de Aprovação**.

**Seção inferior — Registros Limpos:**
- Tabela de placas já analisadas pelo **operador** e consideradas limpas, ou seja placas que foram recusadas como sendo roubadas por erro ou outro motivo, elas teram uma foto ao lado também provando que realmente não são roubados.
- **Barra de pesquisa:** filtro em tempo real por placa. A borda do campo fica rosa ao estar ativo. Durante a pesquisa, a paginação é ocultada e todos os resultados filtrados são exibidos.
- **Paginação:** 8 registros por página com botões de navegação anterior/próxima e indicador de página atual. Exibida somente quando não há pesquisa ativa.

![Central de alerta 1](/img/sprint-3/interface/GestorDaPierUpdate.png)

**Modal de Aprovação:**
- Exibe foto placeholder do veículo, dados completos e dois botões de ação:
  - **Recusar:** fecha o modal e o registro sairá da lista de alertas e vai para a parte de baixo da tela com uma prova.
  - **Aceitar Resgate:** move o veículo para a tela de Veículos Confirmados e remove o alerta da lista.

![Central de alerta 2](/img/sprint-3/interface/GestorDaPierUpdate.png)

---

### Veículos Confirmados (`AcceptedVehicles`)

Tela exclusiva do Analista Pier, acessada pela aba "Confirmados" na sidebar.

Exibe cards dos veículos cujo resgate foi aprovado, contendo:
- Placeholder da foto do veículo
- Placa, modelo, cor
- ID do drone que detectou
- Localização da detecção
- Horário em que foi aceito

Quando não há veículos confirmados, uma mensagem de estado vazio é exibida.

![Veiculos Confirmados](/img/sprint-3/interface/GestorDaPierUpdate.png)

---

### Navegação

A navegação é controlada por um único `useState('screen')` no `App.jsx`. Não há React Router. Cada tela recebe `onNavigate` como prop para trocar de tela.

### Estado Compartilhado

`acceptedVehicles` e `handleAccept` vivem no `App.jsx` e são passados por props para `AlertCenter` e `AcceptedVehicles`. Isso garante que os veículos confirmados persistam ao navegar entre abas.

### Sidebar Role-Aware

A `Sidebar` detecta o papel do usuário pelo valor de `currentScreen`. Se a tela atual estiver em `PIER_SCREENS = ['alerts', 'accepted']`, as abas de navegação são exibidas. Caso contrário (Gestor de Campo em `operations`), apenas logo e logout aparecem.

---

## Como Rodar o Frontend

```bash
cd src/frontend
npm install
npm run dev
```

O servidor de desenvolvimento será iniciado em `http://localhost:5173`.

Para gerar o build de produção:

```bash
npm run build
```
