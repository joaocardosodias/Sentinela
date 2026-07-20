---
sidebar_position: 5
title: CLI
---

# Pier CLI — Documentação de Uso

Esta documentação descreve as funcionalidades e comandos da **Pier CLI**, uma interface de linha de comando desenvolvida para validar o fluxo operacional e administrativo da solução nesta Sprint 2.

---

## Introdução

A **Pier CLI** (`pier`) é a interface inicial do sistema para operadores e administradores. Nesta sprint, ela cumpre dois papéis diferentes:

- **CLI administrativa**, já integrada ao backend para autenticação e gestão de entidades como usuários, veículos, operações, drones e scans;
- **CLI de teleoperação/protótipo**, usada para experimentação de comandos ligados ao drone e a rotinas locais de captura.

Essa distinção é importante. A parte administrativa trabalha bem com requisições HTTP comuns, consulta de dados e atualização de registros. Já a teleoperação em campo exige resposta rápida, estado atualizado do drone, tratamento de perda de conexão, bateria, stream e comandos de segurança. Na Sprint 2, essa segunda frente foi validada de forma incremental e ainda não representa uma integração ponta a ponta equivalente à camada administrativa.

---

## Configuração Inicial

Para que a CLI administrativa funcione corretamente, ela precisa se comunicar com o backend Flask.

- **Variável de Ambiente**: Defina a URL do backend através da variável `PIER_API_URL`.
  - Exemplo (Linux/macOS): `export PIER_API_URL="http://localhost:5000"`
  - Exemplo (Windows PowerShell): `$env:PIER_API_URL="http://localhost:5000"`

---

## Comandos Gerais

### 1. Informações e Ajuda
Exibe uma guia rápida de todos os comandos disponíveis.
```bash
pier info
```

### 2. Verificação de Saúde (Health Check)
Verifica se o backend está online e acessível.
```bash
pier health
```

---

## Autenticação e Usuários (`pier api`)

Gerencia a sessão do usuário e permissões no sistema.

| Comando | Descrição |
| :--- | :--- |
| `pier api register` | Cria uma nova conta de usuário. |
| `pier api login` | Autentica e salva o token JWT localmente. |
| `pier api logout` | Encerra a sessão e remove o token salvo. |
| `pier api me` | Exibe os dados do perfil do usuário logado. |
| `pier api users-list` | Lista todos os usuários cadastrados (Requer privilégios). |
| `pier api users-search <nome>` | Busca usuários por nome. |

---

## Controle do Drone (`pier drone`)

Comandos para interação com o drone Tello e com rotinas de captura. Nesta sprint, essa área deve ser entendida como uma **camada em evolução**: parte dos comandos representa a direção da integração final, mas o núcleo entregue e validado do sistema está no backend REST, no banco e na CLI administrativa.

- **`connect`**: Estabelece o link inicial com o drone.
- **`status`**: Mostra telemetria em tempo real (bateria, altitude, velocidade).
- **`takeoff` / `land`**: Comandos de decolagem e pouso.
- **`capture`**: Rotina automatizada que decola, tira uma foto, salva no DAM e pousa.
  - `--analyze`: Adicione esta flag para enviar a foto para análise da visão computacional imediatamente.
- **`emergency`**: Comando crítico para parar os motores instantaneamente.

---

## Gestão de Imagens e IA (`pier dam`)

Gerencia as imagens capturadas e os processos de análise por Visão Computacional.

- **`pier dam list`**: Lista todas as imagens armazenadas no Supabase.
- **`pier dam analyze <id>`**: Solicita que o modelo de visão computacional analise uma imagem específica (ex: detecção de danos em veículos).

---

## Gestão de Dados (CRUD)

A CLI também permite gerenciar as entidades fundamentais do negócio:

- **`pier scans`**: Listagem e gestão de sessões de mapeamento.
- **`pier veiculos`**: Gerenciamento de frotas e busca de veículos por placa/modelo.
- **`pier operacoes`**: Controle de missões de campo e vistorias.
- **`pier drones`**: Cadastro e status dos equipamentos disponíveis na frota.

---

## Exemplo de Fluxo de Trabalho

Um operador típico seguiria este fluxo para uma vistoria:

1. **Login**: `pier api login`
2. **Conexão**: `pier drone connect`
3. **Vistoria Automática**: `pier drone capture --label "Vistoria_FIAT_2024" --analyze`
4. **Verificação**: `pier dam list` para confirmar o upload.

---

## Conclusão

Na Sprint 2, a **Pier CLI** funciona principalmente como a primeira interface operacional do sistema, permitindo validar autenticação, consultas e cadastros de forma reprodutível. Ela também serve como ponte para os experimentos de drone e captura, mas essa parte ainda deve ser lida como evolução técnica em andamento, não como fluxo final totalmente integrado.
