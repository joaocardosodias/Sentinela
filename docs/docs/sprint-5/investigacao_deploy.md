---
sidebar_position: 4
title: Investigacao de Deploy
---

# Investigacao de Deploy

## Objetivo

Esta investigacao avalia se faz sentido investir em deploy para o projeto G03, quais partes da solucao se beneficiam mais desse processo e como essa escolha se compara a apenas criar um arquivo `.sh` para automatizar a execucao.

O projeto possui uma arquitetura hibrida: parte da solucao roda na borda, no computador do operador conectado ao drone DJI Tello, e parte da solucao atende gestores por meio de API, banco, dashboard e documentacao. Por isso, "fazer deploy" nao deve ser entendido como colocar tudo na nuvem. A decisao mais adequada e separar o que precisa estar online do que precisa continuar perto do hardware.

## Contexto do projeto

A solucao combina:

- Backend Flask, localizado em `src/backend`, responsavel pelas rotas da API, autenticacao, operacoes, scans, drones e veiculos.
- Frontend React + Vite, localizado em `src/frontend`, usado como dashboard operacional.
- Pipeline de visao computacional e OCR, com YOLO, EasyOCR/PaddleOCR e modelos `.pt`.
- Servidor WebRTC local, em `src/drone_webrtc_server.py`, que recebe video UDP do Tello e disponibiliza video/telemetria para o dashboard.
- Scripts PowerShell em `scripts/`, usados para preparar ambiente, validar portas, configurar firewall e iniciar o servidor WebRTC.
- Documentacao Docusaurus em `docs/`, ja preparada para build e publicacao via GitLab Pages.

Essa separacao mostra que existem pelo menos tres superficies de deploy:

1. **Documentacao**: publicacao estatica do Docusaurus.
2. **Aplicacao web e API**: frontend, backend e banco acessiveis por gestores.
3. **Operacao de borda**: notebook/computador do operador com drone, Wi-Fi local, dependencias de video, OCR e rede.

## Premissas tecnicas usadas

- O Tello depende de uma rede Wi-Fi propria, portas UDP e recepcao de video local. Isso torna a camada de borda sensivel a latencia, firewall, interfaces de rede e disponibilidade fisica do drone.
- O backend Flask atual inicia com `app.run(debug=True)`, adequado para desenvolvimento, mas nao para producao.
- O frontend Vite pode gerar artefatos estaticos para publicacao, desde que variaveis como `VITE_API_URL` e caminhos de assets estejam configurados para o ambiente correto.
- A documentacao ja possui pipeline `.gitlab-ci.yml` com etapas `build` e `deploy` para GitLab Pages.

## Pesquisa sobre alternativas de deploy

### 1. Deploy da documentacao

A documentacao Docusaurus ja e o caso mais maduro de deploy do repositorio. O arquivo `.gitlab-ci.yml` usa `node:20-alpine`, executa `npm ci --legacy-peer-deps`, roda `npm run build` dentro de `docs/` e copia `docs/build/*` para `public/`. Isso esta alinhado ao modelo do GitLab Pages, que publica os arquivos finais a partir de um diretorio `public` quando o job de Pages termina com sucesso.

**Utilidade para o projeto:** alta. Mantem um ponto unico de consulta para stakeholders, professores e equipe, sem exigir instalacao local do projeto. Como o artefato e estatico, o custo operacional e baixo e a automacao ja existe.

**Cuidados:** validar o build antes de merge na branch padrao, manter links internos corretos e evitar dependencias de ambiente local na documentacao.

### 2. Deploy do frontend web

O Vite recomenda gerar a versao de producao com `npm run build`; por padrao, o resultado fica em `dist` e pode ser publicado em uma plataforma estatica. No projeto, isso se aplica ao dashboard React, desde que as variaveis `VITE_API_URL`, `VITE_ASSET_BASE_URL`, `VITE_DRONE_WEBRTC_URL` e `VITE_DRONE_TELEMETRY_WS_URL` estejam coerentes com o ambiente.

**Utilidade para o projeto:** media a alta. O dashboard remoto para gestores tem valor claro em deploy, porque permite acesso sem abrir o ambiente de desenvolvimento. Porem, a visualizacao ao vivo do drone depende de um servidor WebRTC local acessivel pela rede, entao o frontend publicado precisa lidar bem com indisponibilidade da camada de borda.

**Cuidados:** separar ambiente de desenvolvimento e producao; configurar URL publica da API; tratar CORS; evitar depender do proxy local do Vite, que existe apenas durante `npm run dev`.

### 3. Deploy do backend Flask

A documentacao oficial do Flask destaca que o servidor embutido de desenvolvimento, debugger e reloader nao devem ser usados em producao. Para producao, a aplicacao deve rodar em um servidor WSGI ou plataforma de hospedagem. No G03, isso significa trocar `app.run(debug=True)` como caminho de producao por algo como Gunicorn/Waitress, reverse proxy ou uma plataforma gerenciada.

**Utilidade para o projeto:** alta para a camada de API. Um backend publicado permite que gestores remotos consultem scans, alertas, operacoes e veiculos sem depender do computador do operador. Tambem facilita integracao com banco em nuvem e auditoria dos registros.

**Cuidados:** proteger `SECRET_KEY`, `JWT_SECRET_KEY` e `DATABASE_URL`; configurar logs; definir migracao/seed de banco; usar HTTPS; e criar checagens de saude para detectar indisponibilidade.

### 4. Deploy com Docker e Docker Compose

Docker empacota aplicacao e dependencias em containers, reduzindo diferencas entre maquinas. Dockerfile define as instrucoes para gerar uma imagem, enquanto Docker Compose permite descrever multiplos servicos, redes e volumes em um unico arquivo YAML. Isso combina bem com uma solucao que tem API, frontend, banco opcional em desenvolvimento e possiveis workers de sincronizacao.

**Utilidade para o projeto:** alta para padronizar ambientes de API/frontend e media para a camada de borda. Para o backend e o frontend, containers reduzem o risco de "funciona na minha maquina". Para visao computacional, podem ajudar a fixar versoes de Python, OpenCV, OCR e YOLO, mas o acesso ao Tello, portas UDP, drivers, firewall e interfaces Wi-Fi continuam sendo dependencias do host.

**Cuidados:** imagens de visao computacional tendem a ficar grandes; modelos `.pt` precisam de estrategia de versionamento; captura de video e GPU/CPU podem exigir configuracao especifica; Docker Desktop em Windows adiciona uma camada que pode complicar acesso direto a rede do drone.

### 5. Deploy ou empacotamento da borda

No projeto, a borda nao deve ser tratada como um servico cloud tradicional. O computador do operador precisa estar conectado ao Tello, receber video UDP em `11111`, ler estado em `8890`, enviar comandos em `8889` e expor WebRTC em `8765`. Isso torna mais adequado falar em **release operacional local**: scripts de preparo, validacao automatica, instalacao controlada de dependencias e execucao assistida.

**Utilidade para o projeto:** alta, desde que "deploy" signifique instalacao reprodutivel no notebook de campo. Baixa, se significar mover o controle do drone para nuvem, pois a nuvem nao enxerga a rede local do Tello nem atende a restricao de baixa latencia da operacao.

**Cuidados:** manter scripts Windows/PowerShell, documentar portas, checar rede privada/publica, validar firewall e preservar modo offline/parcial quando a internet cair.

## Deploy estruturado vs arquivo `.sh`

Um arquivo `.sh` e um script de shell: um arquivo de texto com comandos que o Bash le e executa em uma sessao nao interativa. Ele e util para repetir uma sequencia de comandos, mas nao resolve sozinho problemas de ambiente, publicacao, disponibilidade, rollback e observabilidade.

No contexto do G03, ha uma diferenca importante: os scripts existentes para Tello sao PowerShell, porque o fluxo operacional documentado depende do Windows, firewall, portas e perfis de rede. Criar apenas um `.sh` ajudaria usuarios Linux/macOS, mas nao cobriria a maquina de campo principal caso ela continue sendo Windows.

| Criterio | Deploy estruturado | Arquivo `.sh` |
| --- | --- | --- |
| Reprodutibilidade | Define artefatos, imagens, variaveis, ambientes e versoes esperadas. | Repete comandos, mas depende muito do estado previo da maquina. |
| Producao | Permite CI/CD, servidor WSGI, HTTPS, logs, healthcheck e rollback. | Pode iniciar processos, mas normalmente nao entrega governanca de producao. |
| Onboarding local | Pode exigir Docker, runner, registry ou plataforma. | E simples, rapido e facil de ler. |
| Camada de borda | Ajuda se for tratado como release local com validacoes e dependencias fixadas. | Ajuda muito para preflight e execucao do Tello, principalmente para portas e firewall. |
| Frontend | Gera e publica artefatos estaticos versionados. | Pode rodar `npm run build`, mas ainda precisa de destino de publicacao. |
| Backend | Usa servidor adequado para producao e variaveis seguras. | Pode chamar `python main.py`, mas isso manteria o Flask em modo desenvolvimento se nao houver outra configuracao. |
| Banco e segredos | Integra variaveis protegidas, ambientes e politica de acesso. | Facilmente espalha segredos se nao houver cuidado. |
| Manutencao | Mais robusto para equipe e entrega continuada. | Mais barato no curto prazo, mas tende a virar automacao fragil se crescer demais. |

### Quando um `.sh` e suficiente

Um `.sh` faz sentido quando o objetivo e automatizar tarefas locais e previsiveis, por exemplo:

- Criar ambiente virtual em Linux/macOS.
- Instalar dependencias de desenvolvimento.
- Rodar backend, frontend e documentacao em modo local.
- Executar testes e verificacoes antes de commit.
- Servir como equivalente Unix dos scripts PowerShell ja existentes.

Nesse caso, o `.sh` e uma ferramenta de produtividade, nao o deploy final.

### Quando deploy e mais adequado

Deploy estruturado passa a ser mais adequado quando existe usuario fora da maquina do desenvolvedor, necessidade de repeticao segura ou responsabilidade operacional. Para o G03, isso aparece em:

- Publicar a documentacao da sprint.
- Publicar dashboard para gestores.
- Disponibilizar API para consulta remota.
- Preservar logs e evidencias de scans.
- Garantir que a aplicacao volte ao ar apos falha.
- Separar configuracoes de desenvolvimento, homologacao e producao.

### Comparacao sintetica

A melhor escolha nao e "deploy ou `.sh`", mas **deploy com scripts auxiliares**. O deploy define o ambiente e o ciclo de vida; scripts executam tarefas repetitivas dentro desse ciclo. Para a borda, o script continua sendo central. Para dashboard, backend e documentacao, o deploy e o caminho mais profissional.

## Parecer: deploy e util para o nosso projeto?

Sim, o deploy e util para o G03, mas de forma seletiva. O projeto nao deve tentar transformar todos os componentes em uma aplicacao cloud unica, porque a operacao com o drone depende de hardware, rede local e baixa latencia. O caminho mais coerente e adotar **deploy hibrido**:

- **Deploy completo** para documentacao, dashboard web e backend.
- **Empacotamento local assistido** para a camada de borda com drone, WebRTC, OCR e YOLO.
- **Scripts auxiliares** para preparo, preflight, execucao local e troubleshooting.

### Onde o deploy vale a pena

| Parte do projeto | Vale fazer deploy? | Justificativa |
| --- | --- | --- |
| Documentacao Docusaurus | Sim | Ja existe CI/CD com GitLab Pages; e o artefato mais simples e estavel. |
| Frontend React/Vite | Sim | Gestores podem acessar o dashboard sem rodar Vite localmente. |
| Backend Flask | Sim | A API precisa ficar disponivel para usuarios remotos e deve sair do modo desenvolvimento. |
| Banco/Supabase/PostgreSQL | Sim | Dados, scans, alertas e evidencias precisam persistir fora do notebook do operador. |
| WebRTC do drone | Parcialmente | Deve ser empacotado e executado localmente; publicar na nuvem nao resolve acesso ao Tello. |
| YOLO/OCR | Parcialmente | Faz sentido fixar dependencias e versoes, mas a execucao ainda depende da maquina de campo. |
| Scripts de rede/firewall | Nao como deploy cloud | Sao rotinas de operacao local e devem continuar como scripts/preflight. |

### Onde o deploy nao e tao util

Deploy nao agrega muito quando a tarefa depende exclusivamente da sessao local do operador. Exemplos:

- Entrar no Wi-Fi do Tello.
- Liberar firewall no Windows.
- Verificar se portas UDP estao ocupadas.
- Ligar `streamon` e receber video do drone.
- Ajustar interfaces de rede em campo.

Nesses casos, scripts sao mais praticos do que uma plataforma de deploy. O ganho esta em deixar esses scripts idempotentes, bem documentados e com mensagens de erro claras.

## Recomendacao de arquitetura de deploy

### Curto prazo

1. Manter e validar o deploy da documentacao no GitLab Pages.
2. Criar um script Unix opcional, por exemplo `scripts/run_local.sh`, apenas como paridade para Linux/macOS.
3. Criar comandos padronizados para desenvolvimento local: backend, frontend, documentacao e WebRTC.
4. Documentar variaveis obrigatorias por ambiente: `.env`, `VITE_API_URL`, `DATABASE_URL`, chaves JWT e URL WebRTC.

### Medio prazo

1. Ajustar o backend Flask para entrada de producao com WSGI.
2. Criar `Dockerfile` para backend e, se necessario, um `docker-compose.yml` para API, frontend e banco local de desenvolvimento.
3. Gerar build estatica do frontend e publicar em ambiente separado do Vite dev server.
4. Adicionar healthcheck da API e verificacao basica de autenticao, banco e rotas criticas.

### Longo prazo

1. Empacotar a camada de borda como release local versionada.
2. Versionar modelos YOLO/OCR e registrar tamanho, versao, origem e data de atualizacao.
3. Criar pipeline de CI para testes, lint/build do frontend, build da documentacao e validacao minima do backend.
4. Adicionar estrategia de rollback para backend/frontend e checklist operacional para campo.

## Riscos e mitigacoes

| Risco | Impacto | Mitigacao |
| --- | --- | --- |
| Publicar backend com `debug=True` | Exposicao indevida e baixa robustez | Usar servidor WSGI e variaveis de ambiente por ambiente. |
| Frontend publicado apontando para `localhost` | Dashboard remoto quebra fora da maquina do dev | Configurar `VITE_API_URL` e URLs WebRTC por ambiente. |
| Scripts com segredo embutido | Vazamento de credenciais | Usar `.env`, variaveis protegidas do CI/CD e nunca commitar segredos. |
| Containerizar Tello sem validar rede | Video/telemetria podem falhar | Manter camada Tello local com preflight de portas, firewall e interface. |
| Imagens Docker muito grandes | Build lento e deploy pesado | Separar API leve de componentes de visao computacional; cachear dependencias. |
| Falta de logs e healthcheck | Dificulta diagnostico em campo e producao | Padronizar logs, endpoints de saude e mensagens de erro. |

## Conclusao

O deploy e recomendado para o projeto, principalmente para documentacao, dashboard e backend. Para a camada de drone, a melhor abordagem nao e "subir para nuvem", mas transformar a operacao local em um release reprodutivel, com scripts de preparacao e validacao.



## Fontes consultadas

- [Docker: What is Docker?](https://docs.docker.com/get-started/docker-overview/)
- [Docker: Dockerfile overview](https://docs.docker.com/build/concepts/dockerfile/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Flask: Deploying to Production](https://flask.palletsprojects.com/en/stable/deploying/)
- [Vite: Deploying a Static Site](https://vite.dev/guide/static-deploy.html)
- [GitLab CI/CD](https://docs.gitlab.com/ci/)
- [GitLab Pages from scratch](https://docs.gitlab.com/user/project/pages/getting_started/pages_from_scratch/)
- [GNU Bash Manual: Shell Scripts](https://www.gnu.org/software/bash/manual/bash.html#Shell-Scripts)
