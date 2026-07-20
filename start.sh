#!/usr/bin/env bash
#
# start_all.sh — Sobe o SISTEMA COMPLETO em um único terminal:
#   1) backend            — API Flask           (roda em src/backend/)
#   2) frontend           — Vite/React dev       (roda em src/frontend/)
#   3) drone_webrtc_server — vídeo + detecção     (roda em src/, PYTHONPATH=raiz)
#   4) supabase_matcher    — worker Pier->Postgres(roda em src/, PYTHONPATH=raiz)
#
# Os logs dos quatro saem MISTURADOS neste terminal, cada linha prefixada com
# [backend] / [frontend] / [drone] / [sync] para você distinguir a origem.
#
# Ctrl+C encerra os QUATRO de forma limpa (sem órfãos segurando portas).
#
# Uso:
#   ./start_all.sh

set -u

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$PROJECT_ROOT/src"
VENV_PY="$PROJECT_ROOT/.venv/bin/python"

# ---- Validações ----
if [[ ! -x "$VENV_PY" ]]; then
    echo "ERRO: Python do venv não encontrado em $VENV_PY"
    exit 1
fi
for d in backend frontend drone database; do
    if [[ ! -d "$SRC_DIR/$d" ]]; then
        echo "ERRO: pasta src/$d não encontrada."
        exit 1
    fi
done
if [[ ! -d "$SRC_DIR/frontend/node_modules" ]]; then
    echo "AVISO: src/frontend/node_modules não existe. Rode 'npm install' em src/frontend antes."
fi

pids=()
cleanup() {
    echo ""
    echo "Encerrando todos os processos..."
    for pid in "${pids[@]}"; do
        # Mata o grupo de processos do filho (-PID) para derrubar netos também
        # (ex.: o vite que o npm inicia). Ignora se já saiu.
        kill -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null
    echo "Tudo encerrado."
}
trap cleanup INT TERM EXIT

# Prefixa cada linha de log com a origem. 'setsid' põe o processo em seu próprio
# grupo, para que o cleanup consiga derrubar a árvore inteira de cada serviço.
run() {
    local label="$1"; shift
    local workdir="$1"; shift
    ( cd "$workdir" && setsid "$@" 2>&1 | sed "s/^/[$label] /" ) &
    pids+=($!)
}

echo "=================================================="
echo " Iniciando sistema completo — Pier / g03"
echo " Raiz: $PROJECT_ROOT"
echo " Ctrl+C encerra tudo."
echo "=================================================="

# 1) Backend (de dentro de src/backend, por causa do 'from app import ...')
run "backend" "$SRC_DIR/backend" "$VENV_PY" main.py

# 2) Frontend (Vite)
run "frontend" "$SRC_DIR/frontend" npm run dev

# 3) Drone + 4) Worker rodam de src/ com a raiz no PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"

# 3) Servidor WebRTC do drone
run "drone" "$SRC_DIR" "$VENV_PY" -m drone.drone_webrtc_server

# dá um tempo pro servidor do drone subir antes do worker
sleep 2

# 4) Worker de sincronização Pier -> Postgres
run "sync" "$SRC_DIR" "$VENV_PY" -m database.supabase_matcher

echo "--------------------------------------------------"
echo "4 serviços rodando: backend | frontend | drone | sync"
echo "--------------------------------------------------"

# Se QUALQUER serviço cair, derruba todos.
wait -n
echo ""
echo "Um serviço terminou — encerrando os demais."