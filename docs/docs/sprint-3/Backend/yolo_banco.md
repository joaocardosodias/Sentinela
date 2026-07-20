---
sidebar_position: 2
---

# Avanços da YOLO e Conexão com a "API da Pier"

O trabalho teve como objetivo evoluir o sistema de reconhecimento de placas do drone para que, ao detectar uma placa por YOLO + OCR, o projeto armazenasse evidências localmente e sincronizasse os dados posteriormente com o banco remoto.

A principal decisão técnica foi separar o momento de captura do momento de sincronização: durante o voo, o computador fica conectado ao Wi-Fi do Tello e pode ficar sem internet. Por isso, as detecções são guardadas primeiro em SQLite local. Depois, com internet disponível, um script de sincronização processa os registros pendentes e envia os scans para o Supabase/PostgreSQL.

O resultado final foi um fluxo em duas etapas: coleta local offline e sincronização online posterior. Essa separação deixou o sistema mais robusto, porque evita perder frames quando a rede externa não está disponível. 

## 1. Objetivos da implementação

- Salvar localmente o frame quando uma placa válida for detectada.
- Evitar dependência de internet durante o voo do drone.
- Usar SQLite como fila temporária de detecções pendentes.
- Comparar placas detectadas com veículos já cadastrados no banco remoto.
- Criar registros de scan no banco PostgreSQL/Supabase.
- Guardar o caminho da imagem no campo `imagem_url` da tabela `scans` quando houver match.
- Criar um roteiro claro de execução e teste para o grupo.

## 2. Arquitetura final do fluxo

A arquitetura foi organizada em duas camadas principais: uma **local**, responsável por capturar e armazenar temporariamente os dados, e outra **remota**, responsável por persistir os scans no banco principal.

| Camada | Responsabilidade | Arquivos principais |
|---|---|---|
| Captura/OCR | Detectar placas com YOLO + OCR e retornar placa, formato, bbox, confiança e validade. | `plate_recognizer.py`, `drone.py` |
| Fila local | Guardar frame e metadados em SQLite quando a placa for considerada válida. | `local_detections.db`, funções em `plate_recognizer.py` |
| Sincronização | Buscar pendências do SQLite, comparar com veículos no PostgreSQL e criar scans. | `sync_pending.py`, `supabase_matcher.py` |
| Banco remoto | Armazenar veículos cadastrados e scans gerados pelo processamento. | Tabelas `veiculos` e `scans` |

## 3. Linha cronológica do trabalho realizado

### 3.1 Primeira proposta: salvar frame como arquivo local

A primeira solução desenhada foi salvar o frame diretamente em uma pasta local, como `detections/`.

Essa abordagem era simples e visualmente fácil de auditar, mas foi substituída pela ideia de usar SQLite como fila temporária.

### 3.2 Decisão por SQLite local

Foi escolhido o SQLite para guardar os frames temporariamente em formato BLOB, junto com:

- placa;
- formato;
- confiança;
- bbox;
- status;
- timestamp.

O motivo foi criar uma fila local resiliente, capaz de armazenar detecções mesmo sem internet.

### 3.3 Criação automática do banco SQLite

Foi implementada uma inicialização automática com:

```python
sqlite3.connect(SQLITE_DB_PATH)
```

```SQL
CREATE TABLE IF NOT EXISTS plate_frames
```
Assim, o arquivo local_detections.db é criado apenas quando necessário, e a tabela plate_frames não é recriada a cada execução.

## 3.4 Salvamento do frame no SQLite

A função save_plate_frame_to_sqlite passou a converter o frame para JPG em memória com:

```bash
cv2.imencode(".jpg", frame)
```

Depois, a imagem é transformada em bytes e inserida no SQLite com status pending.

## 3.5 Integração com Supabase/PostgreSQL

A integração foi adaptada para usar DATABASE_URL via psycopg2, porque o .env do projeto não utilizava SUPABASE_URL nem SERVICE_ROLE_KEY.

A conexão passou a ser feita diretamente no PostgreSQL do Supabase.

## 3.6 Ajuste ao schema real do banco

O código foi alinhado às tabelas existentes:

- users;
- veiculos;
- operacoes;
- drones;
- scans;
- veiculos_scans;
- usuarios_scans.

A tabela principal de comparação passou a ser veiculos, e a gravação do resultado passou a ocorrer em scans.

## 3.7 Mock de drone para testes

Como scans exige id_drone, foi criado um fallback com um drone mockado fixo.

Se DEFAULT_DRONE_ID não existir ou não for UUID válido, o sistema usa MOCK_DRONE_ID.

Isso evita quebrar testes quando não há drone real cadastrado.

## 3.8 Separação entre captura e sincronização

Durante o teste com o Tello, foi identificado erro de DNS ao tentar acessar o Supabase conectado ao Wi-Fi do drone.

A solução foi separar os fluxos:

- drone.py coleta e salva localmente;
- sync_pending.py sincroniza depois, quando o computador estiver com internet.

## 4. Principais decisões técnicas e motivos

| Decisão | Por que foi tomada | Benefício |
|---|---|---|
| SQLite local | O drone usa Wi-Fi próprio e pode deixar a máquina sem internet. | Evita perda de detecção quando o Supabase não está acessível. |
| Salvar frame como BLOB temporário | O frame precisa ficar preservado até o sync. | Permite sincronizar posteriormente sem depender da câmera ainda estar ativa. |
| Separar `sync_pending.py` | Sincronização remota durante o voo gerou erro de DNS. | Deixa o voo leve e robusto, e o sync roda só com internet. |
| Usar `DATABASE_URL` | O `.env` do projeto já possui conexão PostgreSQL e não deve mudar. | Integra com o banco atual sem exigir novas variáveis. |
| `imagem_url` em `scans` | O schema já prevê o campo `imagem_url`. | Evita criar tabelas extras e mantém aderência ao modelo do projeto. |
| Drone mockado | A tabela `scans` exige `id_drone`. | Permite testar sem depender de cadastro manual de drone real. |

## 5. Arquivos envolvidos

- `plate_recognizer.py`: detecta placas, valida o OCR e salva frames válidos no SQLite local.

- `local_detections.db`: banco SQLite local usado como fila temporária de detecções.

- `local_detections.py`: contém funções para buscar pendências, apagar registros e alterar status no SQLite.

- `supabase_matcher.py`: conecta ao PostgreSQL/Supabase, compara placas, salva imagens com match e cria scans.

- `sync_pending.py`: script manual para sincronizar registros pendentes depois que a internet estiver disponível.

- `drone.py`: controla o Tello e chama o processamento de frames.

## 6. Fluxo de dados implementado

### 6.1 Durante o voo

1. O usuário conecta o computador ao Wi-Fi do Tello.
2. O script `drone.py` abre o stream de vídeo.
3. Cada frame é enviado para a função `process_frame`.
4. O YOLO detecta regiões candidatas a placa.
5. O EasyOCR tenta ler o texto da placa.
6. O sistema valida o formato da placa.
7. Se a placa for válida, o frame é salvo no SQLite com status `pending`.
8. Nenhuma chamada ao Supabase é feita durante o voo.

### 6.2 Depois do voo

9. O computador é reconectado à internet.
10. O usuário executa o script `sync_pending.py`.
11. O script busca registros com status `pending` no SQLite.
12. Para cada placa, consulta a tabela `veiculos` no PostgreSQL/Supabase.
13. Se encontrar match, salva o frame como arquivo local e usa o caminho em `scans.imagem_url`.
14. Cria um registro na tabela `scans`.
15. Depois do sucesso, remove a detecção do SQLite.

## 7. Regra de negócio atual
O comportamento atual do código documentado é:
    • Placa detectada e existente na tabela veiculos: cria scan com match=True e imagem_url preenchida.
    • Placa detectada e não existente na tabela veiculos: cria scan com match=False e imagem_url=None.
    • Após criação do scan, o registro local é removido do SQLite.
    • O campo roubado da tabela veiculos não é alterado automaticamente pelo OCR. A validação humana continua sendo uma etapa separada.

## 8. Problemas encontrados e como foram resolvidos

| Problema | Solução |
|---|---|
| Erro ao instalar `psycopg2` | O pacote `psycopg2` tentou compilar e falhou por falta do `pg_config`. A solução recomendada para o ambiente foi instalar `psycopg2-binary`. |
| `DEFAULT_DRONE_ID` ausente ou inválido | Foi criado um fallback para `MOCK_DRONE_ID`, garantindo que scans possam ser criados mesmo quando o `.env` não trouxer UUID válido. |
| Criação indevida da tabela `scan_frames` | A ideia foi descartada para respeitar o schema existente. O frame passou a ser salvo como arquivo local, e o caminho é gravado em `scans.imagem_url`. |
| Erro de DNS ao usar o Wi-Fi do Tello | Durante o voo, o computador ficou sem internet e não conseguiu resolver o host do Supabase. A solução foi separar coleta local e sincronização posterior. |
| `create_scan` não aceitava `imagem_url` | A assinatura da função precisava receber `imagem_url=None` para aceitar o parâmetro enviado pelo `process_pending_detections`. |

## 9. Roteiro de como rodar

Este roteiro assume que o usuário está dentro da pasta `src` do projeto e com o ambiente virtual ativado.

### 9.1 Ativar o ambiente virtual

No terminal, dentro do projeto:

```bash
source ../.venv/bin/activate
```

Caso o ambiente esteja em outro caminho, use o comando equivalente do seu projeto.

### 9.2 Instalar dependências necessárias para PostgreSQL

Se o psycopg2 falhar por falta de pg_config, instale a versão binária:

```bash
pip install psycopg2-binary
```

### 9.3 Garantir que o .env existe

O arquivo .env deve conter DATABASE_URL e as demais chaves do projeto.

Não exponha secrets em repositórios ou prints públicos.

```bash
DATABASE_URL=postgresql://...
SECRET_KEY=...
JWT_SECRET_KEY=...
DEFAULT_DRONE_ID=...
```

### 9.4 Limpar a fila local antes de um teste

Dentro de src:
```bash
python - <<'PY'
import sqlite3
from pathlib import Path

db = Path('local_detections.db')
conn = sqlite3.connect(db)
cursor = conn.cursor()
cursor.execute('DELETE FROM plate_frames')
conn.commit()
conn.close()

print('Fila local SQLite limpa.')
PY
```

### 9.5 Rodar o drone e coletar placas

Conectar o computador ao Wi-Fi do Tello.

Executar o script do drone.
```bash
python drone.py
```

Mostrar uma placa de teste para a câmera.

Conferir no terminal se aparece local_detection_id com número.

### 9.6 Reconectar à internet e sincronizar
Sair do Wi-Fi do Tello.

Conectar a uma rede com internet.

Executar o script de sincronização.
```bash
python sync_pending.py
```

### 9.7 Conferir imagens salvas localmente

Quando houver match, a imagem deve aparecer em:
src/uploaded_frames/&lt;PLACA&gt;/&lt;timestamp&gt;.jpg

## 10. Checklist de validação final

- O drone detecta a placa e imprime `local_detection_id` com número.
- O SQLite contém registros `pending` após o voo.
- O `sync_pending.py` roda sem erro de conexão.
- A tabela `scans` recebe novos registros.
- Quando `match=True`, `imagem_url` é preenchida.
- Quando `match=True`, o arquivo aparece em `uploaded_frames`.
- Após o sync, os registros processados deixam de ficar pendentes no SQLite.




