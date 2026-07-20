# Inteli - Instituto de Tecnologia e Liderança

<p align="center">
<a href= "https://www.inteli.edu.br/"><img src="https://res.cloudinary.com/dwewomj84/image/upload/v1761355911/inteli_lfuayp.png" alt="Inteli - Instituto de Tecnologia e Liderança" border="0" width=40% height=40%></a>
</p>

<br>

# G03

## 👨‍🎓 Integrantes:

- <a href="https://www.linkedin.com/in/caue-taddeo/">Caue Taddeo</a>
- <a href="https://www.linkedin.com/in/carlosicaro/">Carlos Icaro Paiva</a>
- <a href="https://www.linkedin.com/in/felipecaiafa/">Felipe Caiafa</a>
- <a href="https://www.linkedin.com/in/jo%C3%A3ocardosodias/">João Cardoso Dias</a>
- <a href="https://www.linkedin.com/in/leandro-precaro-barankiewicz-filho/">Leandro Precaro Barankiewicz Filho</a>
- <a href="https://www.linkedin.com/in/llorengarcia/">Lorena Garcia</a>
- <a href="https://www.linkedin.com/in/rafael-santana-rodrigues/">Rafael Santana Rodrigues</a>
- <a href="https://www.linkedin.com/in/stefannesoares/">Stefanne Soares</a>

## 👩‍🏫 Professores:

### Orientador(a)

- <a href="https://www.linkedin.com/in/rodrigo-mangoni-nicola-537027158/">Rodrigo Mangoni Nicola</a>

### Instrutores

- <a href="https://www.linkedin.com/in/filipe-gon%C3%A7alves-08a55015b/">Filipe Gonçalves de Souza Nogueira da Silva</a>
- <a href="https://www.linkedin.com/in/geraldo-magela-severino-vasconcelos-22b1b220/">Geraldo Magela Severino Vasconcelos</a>
- <a href="https://www.linkedin.com/in/gui-cestari/">Guilherme Henrique de Oliveira Cestari</a>
- <a href="https://www.linkedin.com/in/rafaeldonairelima/">Rafael Donaire Bindo de Lima</a>
- <a href="https://www.linkedin.com/in/fabiana-iegawa/">Fabiana Iegawa</a>
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi</a>

## 📜 Descrição

&emsp;Este projeto, desenvolvido em parceria com a **Pier Seguradora**, tem como objetivo aumentar a taxa de recuperação de veículos roubados ou furtados por meio de um sistema automatizado de fiscalização aérea. A Pier enfrenta um desafio operacional crítico: dos aproximadamente 70 casos de roubo/furto registrados por mês, apenas 5 a 7 veículos são recuperados — uma taxa baixa que gera altos custos de indenização e pressiona a sinistralidade da carteira.

&emsp;A solução proposta combina **drones equipados com câmeras**, **visão computacional** e **integração em tempo real com a API da Pier**, formando um pipeline automatizado de detecção e alerta. O sistema captura imagens de veículos estacionados durante o sobrevoo, extrai e lê as placas automaticamente (ALPR), consulta a base de sinistros da Pier e, em caso de correspondência positiva, gera um alerta imediato com a localização e a imagem do veículo para as equipes responsáveis — tudo em menos de 5 segundos.

&emsp;A arquitetura é distribuída em duas camadas: uma **camada de borda (edge)**, executada localmente no computador do operador de campo, responsável pelo processamento de vídeo, visão computacional e validação em tempo real; e uma **camada de nuvem**, responsável pelo armazenamento de evidências e pelo monitoramento remoto via dashboard pelos gestores da Pier. Essa divisão garante baixa latência na operação e rastreabilidade das ocorrências.

&emsp;O projeto atua diretamente na **janela crítica de recuperação** — as primeiras 72 horas após o sinistro —, período em que o veículo costuma permanecer estacionado antes de ser desmontado. Ao ampliar a cobertura geográfica, automatizar a identificação e reduzir o tempo de resposta, a solução busca tornar a operação de pronta resposta mais eficiente, escalável e menos dependente de processos manuais.

## 📄 Documentação Adicional (Deploy do Docusaurus)

Clique [aqui](https://g03-76b664.pages.git.inteli.edu.br/solucao) para acessar a documentação do projeto.

## 📁 Estrutura de Pastas

```text
g03/
├── docs/                          --> documentação do projeto (Docusaurus)
│   ├── blog/                      --> posts do blog do Docusaurus
│   ├── docs/                      --> conteúdo da documentação por sprint
│   │   ├── solucao/               --> visão geral da solução
│   │   ├── sprint-1/              --> sprint 1: contexto, arquitetura e proposta
│   │   │   ├── Análise de Valor/
│   │   │   ├── Entendimento do Problema/
│   │   │   ├── Proposta de Arquitetura/
│   │   │   └── Proposta de Solução/
│   │   ├── sprint-2/              --> sprint 2: CLI, backend e documentação técnica
│   │   ├── sprint-3/              --> sprint 3: em desenvolvimento
│   │   ├── sprint-4/              --> sprint 4: em desenvolvimento
│   │   └── sprint-5/              --> sprint 5: em desenvolvimento
│   ├── src/                       --> componentes e páginas do site Docusaurus
│   │   ├── components/
│   │   ├── css/
│   │   └── pages/
│   ├── static/                    --> arquivos estáticos (imagens, ícones)
│   │   └── img/
│   │       └── docs/              --> imagens usadas na documentação
│   ├── docusaurus.config.ts       --> configuração do Docusaurus
│   ├── sidebars.ts                --> estrutura da barra lateral
│   └── package.json
│
├── src/                              --> código-fonte principal do projeto
│   ├── backend/                      --> backend da aplicação (API em Flask)
│   │   ├── app/                      --> núcleo da API
│   │   │   ├── entities/             --> entidades de domínio (drone, operação, scan, user, veículo)
│   │   │   ├── middleware/           --> decorators e middlewares (ex.: autenticação)
│   │   │   ├── models/               --> acesso a dados / queries por entidade
│   │   │   ├── routes/               --> definição dos endpoints da API
│   │   │   ├── services/             --> regras de negócio por entidade
│   │   │   ├── config.py             --> configurações e variáveis de ambiente
│   │   │   ├── db.py                 --> conexão com o PostgreSQL
│   │   │   └── __init__.py           --> fábrica da aplicação (create_app)
│   │   ├── schema/                   --> schema do banco de dados
│   │   │   └── schema.sql            --> definição das tabelas (scans, veiculos, users, operacoes, etc.)
│   │   ├── scripts/                  --> scripts auxiliares (init_user, seed_data)
│   │   └── main.py                   --> ponto de entrada do backend
│   │
│   ├── frontend/                     --> frontend web da aplicação (React + Vite)
│   │   ├── img/                      --> imagens, ícones e assets de onboarding
│   │   └── src/                      --> código-fonte do frontend
│   │       ├── components/           --> componentes reutilizáveis (Sidebar, onboarding)
│   │       ├── config/               --> configurações (passos de onboarding)
│   │       ├── hooks/                --> hooks customizados de React
│   │       ├── screens/              --> telas (Login, AlertCenter, AcceptedVehicles, etc.)
│   │       ├── services/             --> integração com a API e stream do drone
│   │       ├── App.jsx               --> componente raiz
│   │       └── main.jsx              --> ponto de entrada do frontend
│   │
│   ├── database/                     --> camada de dados local e sincronização com a nuvem
│   │   ├── local_detections.py       --> gerenciador local de detecções (SQLite)
│   │   └── supabase_matcher.py        --> verificação na Pier, criação de scans e sincronização
│   │
│   ├── drone/                        --> controle do drone e transmissão de vídeo
│   │   ├── drone.py                  --> integração e controle do drone Tello
│   │   ├── drone_webrtc_server.py     --> servidor WebRTC + detecção (vídeo UDP do Tello)
│   │   └── network_routes.py          --> configuração de rotas Tello/local e APIs
│   │
│   ├── visao_computacional/          --> inteligência artificial (detecção de placas)
│   │   ├── ocr/                      --> pipeline de OCR (pré-processamento, métricas, qualidade)
│   │   ├── yolov8n/                  --> modelo YOLOv8n, plate_recognizer e notebooks
│   │   ├── yolo11/                   --> modelo YOLO11, plate_recognizer e notebooks
│   │   ├── yolo26/                   --> modelo YOLO26, plate_recognizer e notebooks
│   │   ├── benchmark_ocr.py          --> benchmark de desempenho do OCR
│   │   └── processar_imagem.py        --> processamento de imagem avulsa
│   │
│   └── cli/                          --> interface de linha de comando
│       ├── index.py                  --> demo de comunicação com o drone Tello
│       └── tui.py                    --> interface de terminal interativa (TUI)
│
├── scripts/                       --> scripts de setup, diagnóstico e execução local
│   ├── setup_tello_cli_env.ps1    --> prepara a .venv e dependências do Tello no Windows
│   ├── check_tello_cli_env.py     --> valida OpenCV, WebRTC e dependências Python
│   ├── run_tello_webrtc_server.ps1 --> preflight e execução do servidor WebRTC do Tello
│   └── enable_tello_video_firewall_rule.ps1 --> libera portas UDP do Tello no firewall
│
├── .env.example                   --> exemplo de variáveis de ambiente
├── .gitignore
├── .github/workflows/             --> pipeline de CI/CD (GitHub Actions)
├── requirements.txt               --> dependências Python
├── package.json                   --> dependências Node.js
├── start.sh                       --> inicia o projeto 
└── README.md                      
```


## 🔧 Instalação

### Pré-requisitos

* **Python:** 3.10 ou superior
* **Node.js:** 20 ou superior
* **Gerenciadores:** `pip` e `venv`
* **Banco de Dados:** PostgreSQL ou Supabase configurado

### Passo a Passo

#### 1. Clonar o repositório
```bash
git clone https://git.inteli.edu.br/graduacao/2026-1b/t16/g03.git
cd g03

```

#### 2. Criar e ativar o ambiente virtual

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate

```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

```

#### 3. Instalar dependências do Python

```bash
pip install -r requirements.txt

```

#### 4. Instalar dependências do frontend

```bash
cd src/frontend
npm install
cd ../..

```

#### 5. Instalar dependências da documentação

```bash
cd docs
npm install
cd ..

```

#### 6. Configurar variáveis de ambiente

Crie o arquivo `.env` na raiz do repositório a partir do exemplo:

```bash
cp .env.example .env

```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env

```

> ⚠️ **Importante:** Abra o arquivo `.env` criado e configure as seguintes chaves com as suas credenciais reais:
> * `DATABASE_URL`
> * `SECRET_KEY`
> * `JWT_SECRET_KEY`
>
> O backend carrega o `.env` a partir da raiz do projeto. Se `DATABASE_URL` estiver ausente ou apontar para um banco desligado, a inicialização do Flask pode falhar com erro de conexão em `localhost:5432`.

As variáveis do DJI Tello, do servidor WebRTC e da conexão dual também ficam no mesmo `.env`:

```dotenv
TELLO_HOST=192.168.10.1
TELLO_COMMAND_PORT=8889
TELLO_LOCAL_PORT=9000
TELLO_STATE_PORT=8890
TELLO_VIDEO_HOST=0.0.0.0
TELLO_VIDEO_PORT=11111
TELLO_WEBRTC_HOST=0.0.0.0
TELLO_WEBRTC_PORT=8765
VITE_DRONE_WEBRTC_URL=http://localhost:8765
VITE_DRONE_TELEMETRY_WS_URL=ws://localhost:8765/telemetry
PIER_API_URL=http://localhost:5000

```

#### 7. Inicializar o banco de dados

Execute o script contido em `src/backend/schema/schema.sql` no PostgreSQL ou Supabase configurado no seu `.env`.



## ▶️ Execução do Projeto

Para rodar or projeto, deve apenas rodar um arquivo na raiz do projeto e no mesmo terminal. Copie e cole no terminal:

```bash
./start.sh
```

#### Configuracao do OCR

O OCR ativo fica em `src/visao_computacional/yolo26/plate_recognizer.py`.
Por padrao, o projeto usa `OCR_PROVIDER=easyocr`. O PaddleOCR fica disponivel
como alternativa local para testes, e `OCR_PROVIDER=compare` permite comparar os
dois modelos no mesmo recorte.

Opcoes suportadas:

```env
OCR_PROVIDER=easyocr
OCR_PROVIDER=paddle
OCR_PROVIDER=compare
OCR_COMPARE_PRIMARY=paddle
```

Para comparar EasyOCR e PaddleOCR em uma pasta de recortes de placas:

```bash
python -m src.visao_computacional.benchmark_ocr caminho/para/recortes --output resultados_ocr.csv --json-summary
```

Observacao: o PaddlePaddle usado pelo PaddleOCR precisa de uma versao de Python
com wheel disponivel. Nos testes locais, Python 3.12 funcionou; Python 3.14 nao
encontrou pacote compativel.

### Wifi Dual Connection e Streaming WebRTC do Tello

O Tello usa uma rede Wi-Fi própria e não se conecta diretamente à Internet. Para operar o drone e continuar acessando APIs externas, use Wifi Dual Connection: duas interfaces de rede simultâneas no PC.

- Wi-Fi conectado ao `TELLO-...`, dedicado a comando, estado e vídeo UDP do drone.
- Internet por segunda interface, como dongle Wi-Fi USB, cabo/Ethernet, iPhone USB com Acesso Pessoal ou outro adaptador.

Nos testes de Sprint 4, o dongle Wi-Fi USB foi o caminho mais simples observado, cabo/Ethernet também funcionou bem, e iPhone USB permaneceu válido como alternativa móvel após instalação/validação dos drivers Apple.

No Windows, antes de abrir o streaming, execute a regra de firewall uma vez em PowerShell como Administrador:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\enable_tello_video_firewall_rule.ps1

```

Depois, com a `.venv` criada e o PC conectado ao Wi-Fi do Tello, rode na raiz do repositório:

```powershell
.\scripts\run_tello_webrtc_server.ps1

```

Esse script valida dependências, portas UDP/TCP, perfil de rede do Tello e abre o servidor WebRTC em:

- WebRTC/API local: [http://localhost:8765](http://localhost:8765)
- Telemetria WebSocket: `ws://localhost:8765/telemetry`
- Vídeo UDP validado: `udp://@0.0.0.0:11111`

Com o servidor WebRTC ativo, abra o frontend (`npm run dev`) e use a tela de operações para visualizar o vídeo do drone.

### TUI (Interface de Terminal)

A TUI consome a API Flask. Se necessário, defina a URL da API antes de rodar o comando:

**Linux/macOS:**

```bash
export PIER_API_URL=http://localhost:5000
python -m src.cli.tui

```

**Windows (PowerShell):**

```powershell
$env:PIER_API_URL="http://localhost:5000"
python -m src.cli.tui

```

### Documentação (Docusaurus)

Para executar a documentação localmente:

```bash
cd docs
npm start

```

Para gerar a build estática da documentação:

```bash
npm run build

```


## 🗃 Histórico de lançamentos

- 0.1.0 - 30/04/2026
  - [Sprint 1] Análise do contexto de negócio, compreensão dos usuários, definição da proposta de solução e estruturação inicial da arquitetura do sistema.

- 0.2.0 - 15/05/2026
  - [Sprint 2] Implementação inicial da solução, incluindo backend, modelagem do banco de dados, integração com o drone, treinamento do modelo de visão computacional, desenvolvimento da CLI e revisão da arquitetura do projeto.

- 0.3.0 - 29/05/2026
  - [Sprint 3] Integração entre frontend e backend, implementação do fluxo de validação de scans, evolução da Central de Alertas, integração de dados reais no frontend, migração do modelo YOLOv8n para YOLO26, refinamento do pipeline de visão computacional e atualização da documentação técnica do sistema.

- 0.4.0 - 12/06/2026
  - [Sprint 4] Finalização da integração e testes do fluxo inteiro do projeto. aprimoração do frontend, finalização da comunicação do vídeo do drone para o frontend, análise financeira, comunicação com a API da Pier, validação do fluxo inteiro completas, além de escrever os testes de usuário e testes unitários para a próxima sprint.

- 0.5.0 - 26/06/2026
  - [Sprint 5] Polimento do projeto, com a implementação de alertas no frontend, possíveis alterações manuais no modelo do carro, cor e placa, testes de usuário e testes unitários, integração total do projeto, além de unir todos os arquivos para rodar apenas em um.


## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/">G03 by [Inteli](https://www.inteli.edu.br/), <a href="https://www.linkedin.com/in/caue-taddeo/">Caue Taddeo</a>, <a href="https://www.linkedin.com/in/carlosicaro/">Carlos Icaro Paiva</a>, <a href="https://www.linkedin.com/in/felipecaiafa/">Felipe Caiafa</a>, <a href="https://www.linkedin.com/in/jo%C3%A3ocardosodias/">João Cardoso Dias</a>, [Leandro Precaro Barankiewicz Filho](https://www.linkedin.com/in/leandro-precaro-barankiewicz-filho-8a293a345/), <a href="https://www.linkedin.com/in/llorengarcia/">Lorena Garcia</a>, [Rafael Santana Rodrigues](https://www.linkedin.com/in/rafael-santana-rodrigues/), <a href="https://www.linkedin.com/in/stefannesoares/">Stefanne Soares</a> is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
