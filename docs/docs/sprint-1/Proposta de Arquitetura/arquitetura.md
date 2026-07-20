---
sidebar_position: 2
title: Arquitetura do Sistema
---

# Arquitetura do Sistema


## 1. Diagrama de Arquitetura



> **Aviso:** A arquitetura ilustrada abaixo representa o **cenário ideal do sistema em produção**, não levando em consideração todos os problemas e as limitações de hardware atuais do drone que estamos utilizando (que limitam certas operações).

<div align="center">Figura 1: Diagrama da Arquitetura da Solução</div>
<div align="center"><img src="/img/sprint-1/Arquitetura_Solucao_basica.png" alt="Diagrama da arquitetura distribuída do sistema (borda local e nuvem)" /></div>
<div align="center">Fonte: Autores, 2026.</div>

## 2. Componentes da Arquitetura Distribuída

O sistema divide a operação em duas frentes: a execução em campo (camada local) e a gestão remota (camada de nuvem). Um único computador concentra todas as funções da camada local (visão computacional, Backend e frontend). Isso simplifica a implantação, elimina a latência de rede entre os componentes e reduz as chances de falha.

### 2.1. Camada de Borda (Edge - Local)

Responsável pelo processamento pesado e tomada de decisão em tempo real. Como o drone opera em áreas de risco, atrasos na transmissão de vídeo podem comprometer a segurança do voo. Por esse motivo, o processamento ocorre integralmente no local. O Backend roda na mesma rede do drone e processa o vídeo localmente, garantindo que o operador não sofra com latência.

* **DJI Tello:** Agente aéreo de captura visual.

* **Backend Local (Orquestrador Edge):** O "cérebro" da operação local. Suas funções incluem:
  * **Stream Splitting:** O fluxo de vídeo recebido do drone é dividido em duas vias simultâneas. A primeira exibe o vídeo em tempo real no **Frontend Local** (Dashboard Tático). A segunda extrai frames isolados (1 a 2 frames por segundo) para enviar ao **Motor de Visão Computacional**. Essa separação é necessária porque a análise visual consome muito processamento, e rodar o modelo de visão em 30 FPS prejudicaria a fluidez do vídeo para o operador.
  * **Motor de Visão Computacional:** Detecta o veículo, faz a leitura da placa e salva uma imagem do momento exato, incluindo uma marcação visual (bounding box) sobre a placa detectada. A decisão de processar isso localmente visa reduzir o tempo de resposta, já que o upload contínuo de vídeo para a nuvem geraria atrasos. A detecção acontece no instante em que o drone filma o veículo, e a imagem gerada serve como evidência fotográfica no fluxo de upload detalhado na Seção 3.
  * **Validação:** O Backend Local consulta a API da Pier de forma automática para verificar se a placa detectada tem registro de roubo ou furto. Durante o voo, o drone capta inúmeros veículos regulares. O filtro do Backend impede que o operador tenha que checar placas manualmente, gerando alertas apenas em caso de detecção positiva.

* **Frontend Local (Dashboard Tático):** Interface de operação no local. Exibe o fluxo de vídeo recebido do drone, permitindo que o operador acompanhe o voo em tempo real. Também apresenta os alertas imediatos gerados em caso de interceptação.

### 2.2. Topologia de Rede (Dual-Homing)

O DJI Tello funciona como um Access Point offline. Isso significa que o computador do operador precisa estar conectado à rede Wi-Fi do drone (`TELLO-XXXX`) para controlá-lo e receber o vídeo, ficando sem internet por padrão. Para resolver essa limitação e manter a comunicação com a nuvem, o computador utiliza múltiplas interfaces de rede (Dual-Homing):

| Interface | Tipo | Finalidade |
|---|---|---|
| **Interface 1** | Wi-Fi Local (TELLO-XXXX) | Via offline dedicada exclusivamente ao recebimento do vídeo via UDP (porta 11111, 30 FPS) enviado pelo drone. |
| **Interface 2** | Rede Cabeada / Tethering | Via com acesso à internet para consultar a API da Pier, fazer upload de evidências e sincronizar logs. |

> A separação física garante que o alto tráfego de vídeo do drone não interfira nas requisições de rede do sistema. O stream de vídeo utiliza o protocolo UDP pois a baixa latência é prioridade . Perder um frame ocasionalmente não é um problema, mas travamentos no vídeo prejudicam a operação.

### 2.3. Camada de Nuvem (Cloud)

Camada focada em armazenamento, auditoria e monitoramento remoto. O sistema utiliza redes móveis no local da operação, o que torna o envio de vídeo contínuo inviável devido a limitações de pacote de dados e instabilidade do sinal. Para resolver isso, somente as evidências dos veículos roubados são enviadas para a nuvem.

* **Cloud Storage (Repositório de Evidências):** Serviço de armazenamento de arquivos (ex: AWS S3 ou Firebase Storage). Recebe as imagens dos veículos identificados como sinistrados e gera URLs públicas de acesso permanente a cada arquivo.

* **Banco de Dados Central:** Banco de dados relacional (SQL). Guarda os registros estruturados das ocorrências confirmadas, salvando a placa, geolocalização, horário e o link de acesso da foto no Cloud Storage.

* **Backend Cloud:** Servidor que atua como ponte segura entre o Banco de Dados e o Dashboard Externo. Ao confirmar uma ocorrência, alimenta o **Dashboard Externo** em tempo real via WebSockets, notificando os gestores remotos da Pier.

* **Frontend Externo (Dashboard Remoto):** Painel acessado remotamente pelos gestores da Pier para acompanhar a operação em andamento. O fluxo de como esses dados chegam até aqui é detalhado na Seção 3.

## 3. Fluxo de Evidência Digital e Cadeia de Custódia

O sistema implementa um fluxo de upload condicional focado em economizar a banda de internet e preservar a cadeia de custódia. Toda a triagem acontece no computador local, e somente dados relevantes são transferidos para a nuvem:

1. **Captura e Análise:** O Motor de Visão Computacional identifica a placa, e o Backend Local armazena o frame resultante temporariamente na memória RAM do computador.

2. **Triagem Local:** O Backend Local consulta a API da Pier pela interface de rede conectada à internet para verificar se a placa possui restrição.

3. **Processo de Upload Condicional:**
   * **Veículo Regular:** A imagem temporária é descartada da memória, evitando o uso desnecessário da rede móvel.
   * **Veículo Roubado ou Furtado:**
     * O Backend Local faz o upload da imagem marcada para o Cloud Storage.
     * O armazenamento retorna uma URL pública.
     * O Backend Local registra a ocorrência no Banco de Dados, salvando a placa, a hora, o link da imagem e a geolocalização (mockada¹).

4. **Acionamento e Alertas:** O Backend Local avisa o operador de campo exibindo o alerta em tempo real no Dashboard Local via WebSockets. Em paralelo, o Backend Cloud identifica a nova ocorrência no banco de dados e notifica os gestores no Dashboard Externo. A equipe remota recebe os metadados e a foto do veículo, agilizando o acionamento da polícia ou da equipe de resgate.

---

> ¹ **Geolocalização Simulada (Mock):** Como o DJI Tello não possui GPS integrado, o sistema usa uma localização fixa pré-configurada para os testes em ambiente controlado. No futuro, drones mais robustos ou módulos externos poderiam fornecer os dados de localização reais.
