const WEBRTC_SERVER = import.meta.env.VITE_DRONE_WEBRTC_URL || 'http://localhost:8765'
const WS_TELEMETRY = import.meta.env.VITE_DRONE_TELEMETRY_WS_URL || 'ws://localhost:8765/telemetry'
const WS_CONTROL = import.meta.env.VITE_DRONE_CONTROL_WS_URL || 'ws://localhost:8765/control'

/**
 * Envia uma ação de controle de voo ao servidor WebRTC, que repassa o comando
 * SDK ao Tello via UDP. Ações permitidas (allowlist no servidor):
 *   takeoff | land | up | down | forward | back | left (yaw ccw) | right (yaw cw) | stop (hover)
 *
 * @param {string} action - ação de controle
 * @param {number} [value] - magnitude opcional (cm para up/down/forward/back, graus para left/right)
 * @returns {Promise<object>} resposta { ok, action, command, response } do servidor
 *   (response = resposta crua do Tello, ex.: "ok" / "error" / "out of range")
 */
export async function sendDroneCommand(action, value) {
  const body = { action }
  if (value !== undefined && value !== null) {
    body.value = value
  }

  const response = await fetch(`${WEBRTC_SERVER}/command`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  let payload = null
  try {
    payload = await response.json()
  } catch {
    // resposta sem corpo JSON
  }

  if (!response.ok || (payload && payload.ok === false)) {
    const message = (payload && payload.error) || `Servidor respondeu ${response.status}`
    throw new Error(message)
  }

  return payload
}

/**
 * Abre um WebSocket de controle contínuo (modo opt-in). O cliente envia o vetor
 * { lr, fb, ud, yaw } (cada eixo -100..100) em alta frequência; o servidor
 * traduz para `rc a b c d` e tem watchdog que faz pairar se os updates pararem.
 *
 * @param {Function} [onStatus] - callback com 'open' | 'closed' | 'error'
 * @returns {{ send: (vector: object) => void, close: () => void }}
 */
export function openControlSocket(onStatus) {
  let ws = null
  try {
    ws = new WebSocket(WS_CONTROL)
    if (onStatus) {
      ws.onopen = () => onStatus('open')
      ws.onclose = () => onStatus('closed')
      ws.onerror = () => onStatus('error')
    }
  } catch {
    if (onStatus) onStatus('error')
  }

  return {
    send(vector) {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(vector))
      }
    },
    close() {
      if (!ws) return
      try {
        // Best-effort: zera os controles antes de fechar. O servidor ainda tem
        // watchdog + stop-on-disconnect como garantia.
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ lr: 0, fb: 0, ud: 0, yaw: 0 }))
        }
      } catch {
        // ignora
      }
      ws.onclose = null
      ws.close()
    },
  }
}

/**
 * Inicia a stream WebRTC do drone e a conexão de telemetria via WebSocket.
 *
 * @param {HTMLVideoElement} videoEl  - elemento <video> onde o feed será exibido
 * @param {Function} onTelemetry     - callback com {battery, connectivity, status}
 * @param {Function} onStatus        - callback com 'connecting' | 'connected' | 'offline'
 * @returns {Function}               - função de cleanup para useEffect
 */
export function startDroneStream(videoEl, onTelemetry, onStatus) {
  let pc = null
  let ws = null
  let stopped = false

  async function connect() {
    onStatus('connecting')

    try {
      // Sem STUN — browser e servidor estão na mesma máquina (localhost)
      pc = new RTCPeerConnection({ iceServers: [] })

      // Só queremos receber vídeo, não enviar
      pc.addTransceiver('video', { direction: 'recvonly' })

      pc.ontrack = (event) => {
        if (videoEl && event.streams[0]) {
          videoEl.srcObject = event.streams[0]
        }
      }

      pc.oniceconnectionstatechange = () => {
        if (stopped) return
        const state = pc.iceConnectionState
        if (state === 'connected' || state === 'completed') {
          onStatus('connected')
        } else if (state === 'failed' || state === 'disconnected' || state === 'closed') {
          onStatus('offline')
        }
      }

      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)

      const response = await fetch(`${WEBRTC_SERVER}/offer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sdp: offer.sdp, type: offer.type }),
      })

      if (!response.ok) throw new Error(`Servidor respondeu ${response.status}`)

      const answer = await response.json()
      await pc.setRemoteDescription(new RTCSessionDescription(answer))
    } catch (err) {
      if (!stopped) {
        console.warn('[droneStream] WebRTC falhou:', err.message)
        onStatus('offline')
      }
    }

    // Conecta WebSocket de telemetria independente do WebRTC
    connectTelemetry()
  }

  function connectTelemetry() {
    if (stopped) return

    try {
      ws = new WebSocket(WS_TELEMETRY)

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onTelemetry({
            battery: data.battery ?? null,
            connectivity: data.connectivity ?? null,
            status: data.status ?? null,
            drone_connected: data.drone_connected ?? null,
          })
        } catch {
          // mensagem malformada — ignora
        }
      }

      ws.onerror = () => {
        // silencia — o status já foi definido pelo WebRTC
      }

      ws.onclose = () => {
        if (!stopped) {
          // Tenta reconectar após 3s se o componente ainda estiver montado
          setTimeout(connectTelemetry, 3000)
        }
      }
    } catch {
      // WebSocket não disponível — ignora
    }
  }

  connect()

  return function cleanup() {
    stopped = true
    if (ws) {
      ws.onclose = null
      ws.close()
    }
    if (pc) {
      pc.oniceconnectionstatechange = null
      pc.ontrack = null
      pc.close()
    }
  }
}
