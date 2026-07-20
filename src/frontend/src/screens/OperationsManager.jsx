import { useEffect, useMemo, useRef, useState } from 'react'
import { Wifi, Battery, Cpu, X, MapPin, ArrowUp, ArrowDown, ChevronsUp, ChevronsDown, RotateCcw, RotateCw, PlaneTakeoff, PlaneLanding, Keyboard, Square, AlertTriangle, Gauge } from 'lucide-react'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import Sidebar from '../components/Sidebar.jsx'
import { getDrones } from '../services/api.js'
import { startDroneStream, sendDroneCommand, openControlSocket } from '../services/droneStream.js'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

const C = {
  pink: '#FF3366',
  dark: '#1A1F36',
  gray: '#6B7280',
  border: '#E5E7EB',
  bg: '#F7F8FA',
}

const DEFAULT_MAP_CENTER = [-14.235, -51.9253]
const DEFAULT_MAP_ZOOM = 4

const droneMarker = L.icon({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

export default function OperationsManager({ onLogout }) {
  const [mapOpen, setMapOpen] = useState(false)
  const [drones, setDrones] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // 'connecting' | 'connected' | 'offline'
  const [streamStatus, setStreamStatus] = useState('connecting')
  const [liveTelemetry, setLiveTelemetry] = useState({
    battery: null,
    connectivity: null,
    status: null,
    drone_connected: null,
  })
  const videoRef = useRef(null)

  // true = drone ativo | false = drone offline | null = ainda aguardando info
  const droneConnected = liveTelemetry.drone_connected

  // Controles de voo aparecem com o servidor conectado, mesmo sem o drone ativo
  // (com disclaimer). Só funcionam de fato quando o drone está transmitindo estado.
  const showFlightControls = streamStatus === 'connected'

  useEffect(() => {
    loadDrones()
  }, [])

  useEffect(() => {
    const cleanup = startDroneStream(videoRef.current, setLiveTelemetry, setStreamStatus)
    return cleanup
  }, [])

  async function loadDrones() {
    setLoading(true)
    setError('')

    try {
      const data = await getDrones()
      const rawDrones = Array.isArray(data) ? data : data?.drones || []
      setDrones(rawDrones.map(normalizeDrone))
    } catch (err) {
      setError(err.message || 'Não foi possível carregar os drones')
      setDrones([])
    } finally {
      setLoading(false)
    }
  }

  const activeDrone = useMemo(() => {
    return (
      drones.find((drone) => drone.isLiveTelemetry && drone.hasCoords && drone.status === 'EM VOO') ||
      drones.find((drone) => drone.isLiveTelemetry && drone.hasCoords) ||
      drones.find((drone) => drone.isLiveTelemetry) ||
      null
    )
  }, [drones])

  return (
    <div style={{ display: 'flex', height: '100vh', background: C.bg }}>
      <Sidebar onLogout={onLogout} />

      <main style={{ flex: 1, overflowY: 'auto', padding: '32px' }}>
        <div style={{ marginBottom: '28px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: '700', color: C.dark, display: 'inline' }}>
            Gestor da Operação
          </h1>
          <span style={{ fontSize: '16px', fontWeight: '400', color: C.gray, marginLeft: '8px' }}>
            / Monitoramento Ativo
          </span>
        </div>

        {error && (
          <FeedbackBox tone="error">
            {error}
          </FeedbackBox>
        )}

        {loading && (
          <FeedbackBox tone="info">
            Carregando dados do drone...
          </FeedbackBox>
        )}

        <div style={{ display: 'flex', gap: '20px', marginBottom: showFlightControls ? '12px' : '20px', alignItems: 'stretch' }}>
          <div
            data-tour="local-video"
            style={{
              flex: '0 0 64%',
              background: '#0F1224',
              borderRadius: '14px',
              aspectRatio: '16/9',
              position: 'relative',
              overflow: 'hidden',
              border: `1px solid rgba(255,255,255,0.06)`,
            }}
          >
            {/* Feed de vídeo WebRTC — só exibido quando drone ativo */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{
                position: 'absolute',
                inset: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                display: streamStatus === 'connected' ? 'block' : 'none',
              }}
            />

            {/* Badge AO VIVO — só quando drone está efetivamente transmitindo */}
            {streamStatus === 'connected' && droneConnected === true && (
              <div
                style={{
                  position: 'absolute',
                  top: 14,
                  left: 14,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: 'rgba(22,163,74,0.85)',
                  borderRadius: '6px',
                  padding: '4px 10px',
                  fontSize: '11px',
                  fontWeight: '700',
                  color: '#fff',
                  letterSpacing: '0.5px',
                }}
              >
                <span style={{ animation: 'livePulse 1.4s ease-in-out infinite' }}>●</span>
                AO VIVO
              </div>
            )}

            {/* Coordenadas no canto superior direito */}
            {activeDrone?.hasCoords && droneConnected === true && (
              <div
                style={{
                  position: 'absolute',
                  top: 16,
                  right: 16,
                  color: 'rgba(255,255,255,0.6)',
                  fontSize: '12px',
                  fontWeight: '500',
                  background: 'rgba(0,0,0,0.45)',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  letterSpacing: '0.3px',
                }}
              >
                {activeDrone.coordsLabel}
              </div>
            )}

            {/* Overlay: servidor WebRTC offline ou conectando */}
            {streamStatus !== 'connected' && (
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  padding: '24px',
                  textAlign: 'center',
                }}
              >
                {streamStatus === 'connecting' ? (
                  <>
                    <span style={{ fontSize: '22px', animation: 'livePulse 1.2s ease-in-out infinite' }}>⟳</span>
                    <span style={{ color: 'rgba(255,255,255,0.55)', fontSize: '13px', letterSpacing: '1px' }}>
                      Conectando ao servidor...
                    </span>
                  </>
                ) : (
                  <>
                    <span style={{ color: 'rgba(255,255,255,0.18)', fontSize: '13px', letterSpacing: '2.5px', textTransform: 'uppercase' }}>
                      Sem sinal
                    </span>
                    <span style={{ color: 'rgba(255,255,255,0.45)', fontSize: '13px', maxWidth: '320px', lineHeight: 1.5 }}>
                      Servidor de vídeo não disponível. Inicie o drone_webrtc_server.py e conecte o dongle ao Tello.
                    </span>
                  </>
                )}
              </div>
            )}

            {/* Overlay: servidor OK mas drone desconectado — aparece sobre o vídeo */}
            {streamStatus === 'connected' && droneConnected === false && (
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'rgba(0,0,0,0.72)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  padding: '24px',
                  textAlign: 'center',
                }}
              >
                <span
                  style={{
                    color: '#F59E0B',
                    fontSize: '13px',
                    letterSpacing: '2.5px',
                    textTransform: 'uppercase',
                    fontWeight: '700',
                  }}
                >
                  Drone desconectado
                </span>
                <span style={{ color: 'rgba(255,255,255,0.55)', fontSize: '13px', maxWidth: '320px', lineHeight: 1.5 }}>
                  O drone parou de transmitir. Verifique se está ligado e conectado ao dongle Wi-Fi.
                </span>
              </div>
            )}
          </div>

          <div data-tour="local-telemetry" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <TelemetryCard
              icon={<Cpu size={19} color={C.pink} />}
              label="Drone ID"
              value={activeDrone?.name || 'Não há informações'}
              badge={
                droneConnected === false
                  ? { text: 'OFFLINE', color: '#92400E', bg: '#FFF7ED' }
                  : activeDrone
                    ? statusBadge(liveTelemetry.status || activeDrone.status)
                    : null
              }
            />
            <TelemetryCard
              icon={<Wifi size={19} color={C.pink} />}
              label="Conectividade"
              value={
                droneConnected === false
                  ? 'Sem conexão'
                  : liveTelemetry.connectivity || activeDrone?.connectivity || 'Não há informações'
              }
              live={droneConnected === true && !!liveTelemetry.connectivity}
            />
            <TelemetryCard
              icon={<Battery size={19} color={C.pink} />}
              label="Bateria"
              value={
                droneConnected === false
                  ? 'Indisponível'
                  : liveTelemetry.battery || activeDrone?.batteryLabel || 'Não há informações'
              }
              live={droneConnected === true && !!liveTelemetry.battery}
            />
          </div>
        </div>

        {/* Controle de voo — abaixo da câmera, na mesma coluna (64%) */}
        {showFlightControls && (
          <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
            <div style={{ flex: '0 0 64%' }}>
              <DroneControls status={liveTelemetry.status} droneConnected={droneConnected} />
            </div>
          </div>
        )}

        <MapPreview
          drone={activeDrone}
          onClick={() => setMapOpen(true)}
        />
      </main>

      {mapOpen && (
        <MapModal
          drone={activeDrone}
          onClose={() => setMapOpen(false)}
        />
      )}
    </div>
  )
}

// Modo continuo (rc a b c d): magnitude por eixo (0-100), taxa de envio e
// mapeamento de teclas/botoes para eixos. fb=frente/tras, ud=cima/baixo,
// yaw=giro (esquerda/direita). Velocidade conservadora por seguranca interna.
const RC_SPEED = 40
const RC_SEND_INTERVAL_MS = 80
const CONT_MAP = {
  ArrowUp: { fb: 1 }, forward: { fb: 1 },
  ArrowDown: { fb: -1 }, back: { fb: -1 },
  ArrowLeft: { yaw: -1 }, left: { yaw: -1 },
  ArrowRight: { yaw: 1 }, right: { yaw: 1 },
  Shift: { ud: 1 }, up: { ud: 1 },
  Control: { ud: -1 }, down: { ud: -1 },
}

function DroneControls({ status, droneConnected }) {
  const [busy, setBusy] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [keyboardEnabled, setKeyboardEnabled] = useState(false)
  // Modo continuo (rc) e o padrao desde o teste de campo bem-sucedido: segurar
  // move, soltar paira. Desligar (Continuo OFF) volta ao discreto (1 clique = 1 passo).
  const [continuousEnabled, setContinuousEnabled] = useState(true)

  // Modo continuo (rc): direcoes pressionadas (teclas + botoes), socket de
  // controle e contador de "zeros" enviados logo apos soltar (garante parada).
  const controlRef = useRef(null)
  const heldRef = useRef(new Set())
  const zeroBurstRef = useRef(0)
  // Estado do Teclado sempre atual para os listeners do modo continuo, sem
  // precisar reabrir o socket quando o Teclado liga/desliga.
  const keyboardEnabledRef = useRef(keyboardEnabled)
  keyboardEnabledRef.current = keyboardEnabled

  const airborne = status === 'EM VOO' || status === 'em_voo'

  async function run(action, label) {
    setBusy(action)
    setFeedback(null)
    try {
      const result = await sendDroneCommand(action)
      const reply = result?.response
      setFeedback({
        tone: 'ok',
        text: reply ? `${label}: Tello respondeu "${reply}"` : `Comando enviado: ${label}`,
      })
    } catch (err) {
      setFeedback({ tone: 'error', text: err.message || 'Falha ao enviar comando' })
    } finally {
      setBusy(null)
    }
  }

  // Modo arcade: mantem uma referencia sempre atual de run() para o listener
  const runRef = useRef(run)
  runRef.current = run

  useEffect(() => {
    // Teclado discreto (1 toque = 1 passo) so vale com o Continuo desligado.
    // No modo continuo as teclas viram "segurar para mover" (outro efeito).
    if (!keyboardEnabled || continuousEnabled) return undefined

    const keyMap = {
      ArrowLeft: ['left', 'Esquerda'],
      ArrowRight: ['right', 'Direita'],
      ArrowUp: ['forward', 'Frente'],
      ArrowDown: ['back', 'Trás'],
      Control: ['down', 'Baixo'],
      Shift: ['up', 'Cima'],
      ' ': ['land', 'Pousar'],
    }

    function onKeyDown(event) {
      const mapping = keyMap[event.key]
      if (!mapping) return
      // Impede rolagem da pagina e ativacao de botao focado pelas mesmas teclas
      event.preventDefault()
      if (event.repeat) return
      runRef.current(mapping[0], mapping[1])
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [keyboardEnabled, continuousEnabled])

  // Modo continuo: faz streaming de rc enquanto teclas/botoes estao pressionados
  // e tem salvaguardas (keyup, blur, aba oculta) para nao deixar comando "grudado".
  useEffect(() => {
    if (!continuousEnabled) return undefined

    heldRef.current.clear()
    zeroBurstRef.current = 0
    controlRef.current = openControlSocket()

    const computeAxes = () => {
      const v = { lr: 0, fb: 0, ud: 0, yaw: 0 }
      heldRef.current.forEach((id) => {
        const m = CONT_MAP[id]
        if (!m) return
        v.fb += (m.fb || 0) * RC_SPEED
        v.ud += (m.ud || 0) * RC_SPEED
        v.yaw += (m.yaw || 0) * RC_SPEED
        v.lr += (m.lr || 0) * RC_SPEED
      })
      const clamp = (x) => Math.max(-RC_SPEED, Math.min(RC_SPEED, x))
      return { lr: clamp(v.lr), fb: clamp(v.fb), ud: clamp(v.ud), yaw: clamp(v.yaw) }
    }

    const sendZero = () => controlRef.current?.send({ lr: 0, fb: 0, ud: 0, yaw: 0 })

    const stopAll = () => {
      heldRef.current.clear()
      zeroBurstRef.current = 3
      sendZero()
    }

    const tick = () => {
      const axes = computeAxes()
      const moving = axes.fb || axes.ud || axes.yaw || axes.lr
      if (moving) {
        controlRef.current?.send(axes)
        zeroBurstRef.current = 3
      } else if (zeroBurstRef.current > 0) {
        sendZero()
        zeroBurstRef.current -= 1
      }
    }

    const onKeyDown = (event) => {
      // No continuo, as teclas so movem o drone com o Teclado ligado; os botoes
      // direcionais funcionam independente disso (toggles independentes).
      if (!keyboardEnabledRef.current) return
      if (event.key === ' ' || event.key === 'Spacebar') {
        // Espaco pousa o drone (encerra o voo). Zera o rc antes para nao
        // competir com o comando de pouso.
        event.preventDefault()
        if (event.repeat) return
        stopAll()
        runRef.current('land', 'Pousar')
        return
      }
      if (CONT_MAP[event.key]) {
        event.preventDefault()
        heldRef.current.add(event.key)
      }
    }
    const onKeyUp = (event) => {
      if (CONT_MAP[event.key]) {
        event.preventDefault()
        heldRef.current.delete(event.key)
      }
    }
    const onVisibility = () => {
      if (document.hidden) stopAll()
    }

    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    window.addEventListener('blur', stopAll)
    document.addEventListener('visibilitychange', onVisibility)
    const interval = setInterval(tick, RC_SEND_INTERVAL_MS)

    return () => {
      clearInterval(interval)
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
      window.removeEventListener('blur', stopAll)
      document.removeEventListener('visibilitychange', onVisibility)
      heldRef.current.clear()
      controlRef.current?.close()
      controlRef.current = null
    }
  }, [continuousEnabled])

  const hold = (id) => heldRef.current.add(id)
  const release = (id) => heldRef.current.delete(id)

  // Botao direcional: clique discreto (1 passo) ou segurar (rc continuo).
  const dirProps = (action, label) =>
    continuousEnabled
      ? { onPressStart: () => hold(action), onPressEnd: () => release(action) }
      : { onClick: () => run(action, label) }

  return (
    <div
      style={{
        background: '#fff',
        borderRadius: '12px',
        border: `1px solid ${C.border}`,
        padding: '14px 16px',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '10px',
          marginBottom: '12px',
        }}
      >
        <span
          style={{
            fontSize: '11px',
            fontWeight: '700',
            letterSpacing: '0.6px',
            textTransform: 'uppercase',
            color: C.gray,
          }}
        >
          Controle de voo
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
          {feedback && (
            <span
              style={{
                fontSize: '12px',
                fontWeight: '600',
                color: feedback.tone === 'error' ? '#B91C1C' : '#166534',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {feedback.text}
            </span>
          )}
          <button
            type="button"
            onClick={(event) => {
              setKeyboardEnabled((value) => !value)
              event.currentTarget.blur()
            }}
            title="Controle por teclado: setas, Shift, Ctrl e Espaço. O estilo segue o modo Contínuo (segurar para mover) ou discreto (1 toque = 1 passo)."
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              flexShrink: 0,
              padding: '5px 10px',
              borderRadius: '8px',
              border: `1px solid ${keyboardEnabled ? C.pink : C.border}`,
              background: keyboardEnabled ? 'rgba(255,51,102,0.08)' : '#fff',
              color: keyboardEnabled ? C.pink : C.gray,
              fontSize: '11px',
              fontWeight: '700',
              letterSpacing: '0.3px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'background 0.15s, border-color 0.15s, color 0.15s',
            }}
          >
            <Keyboard size={14} />
            {keyboardEnabled ? 'Teclado ON' : 'Teclado OFF'}
          </button>
          <button
            type="button"
            onClick={(event) => {
              setContinuousEnabled((value) => !value)
              event.currentTarget.blur()
            }}
            title="Modo contínuo (rc): segure os botões direcionais (ou as teclas, com Teclado ON) para mover; solte para pairar"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              flexShrink: 0,
              padding: '5px 10px',
              borderRadius: '8px',
              border: `1px solid ${continuousEnabled ? C.pink : C.border}`,
              background: continuousEnabled ? 'rgba(255,51,102,0.08)' : '#fff',
              color: continuousEnabled ? C.pink : C.gray,
              fontSize: '11px',
              fontWeight: '700',
              letterSpacing: '0.3px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'background 0.15s, border-color 0.15s, color 0.15s',
            }}
          >
            <Gauge size={14} />
            {continuousEnabled ? 'Contínuo ON' : 'Contínuo OFF'}
          </button>
        </div>
      </div>

      {droneConnected !== true && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '12px',
            padding: '8px 10px',
            borderRadius: '8px',
            border: '1px solid #FED7AA',
            background: '#FFF7ED',
            color: '#92400E',
            fontSize: '12px',
            fontWeight: '600',
            lineHeight: 1.35,
          }}
        >
          <AlertTriangle size={16} style={{ flexShrink: 0 }} />
          <span>Os controles só funcionam quando o drone está ativo. Conecte e ligue o drone para pilotar.</span>
        </div>
      )}

      {continuousEnabled && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '12px',
            padding: '8px 10px',
            borderRadius: '8px',
            border: '1px solid #BFDBFE',
            background: '#EFF6FF',
            color: '#1E40AF',
            fontSize: '12px',
            fontWeight: '600',
            lineHeight: 1.35,
          }}
        >
          <Gauge size={16} style={{ flexShrink: 0 }} />
          <span>Modo contínuo: segure os botões direcionais para mover; solte para pairar. Ative o Teclado para pilotar também pelas teclas (setas/Shift/Ctrl). Velocidade {RC_SPEED}%.</span>
        </div>
      )}

      <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
        <ControlButton
          onClick={() => run('takeoff', 'Decolar')}
          disabled={busy !== null}
          icon={<PlaneTakeoff size={18} />}
          label="Decolar"
          variant="primary"
        />
        <ControlButton
          onClick={() => run('land', 'Pousar')}
          disabled={busy !== null}
          icon={<PlaneLanding size={18} />}
          label="Pousar"
          variant="warn"
        />
        <ControlButton
          onClick={() => run('stop', 'Parar')}
          disabled={busy !== null}
          icon={<Square size={18} />}
          label="Parar"
          variant="stop"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        <ControlButton
          {...dirProps('forward', 'Frente')}
          disabled={busy !== null}
          icon={<ArrowUp size={18} />}
          label="Frente"
        />
        <ControlButton
          {...dirProps('up', 'Cima')}
          disabled={busy !== null}
          icon={<ChevronsUp size={18} />}
          label="Cima"
        />
        <ControlButton
          {...dirProps('left', 'Esquerda')}
          disabled={busy !== null}
          icon={<RotateCcw size={18} />}
          label="Esquerda"
        />
        <ControlButton
          {...dirProps('back', 'Trás')}
          disabled={busy !== null}
          icon={<ArrowDown size={18} />}
          label="Trás"
        />
        <ControlButton
          {...dirProps('down', 'Baixo')}
          disabled={busy !== null}
          icon={<ChevronsDown size={18} />}
          label="Baixo"
        />
        <ControlButton
          {...dirProps('right', 'Direita')}
          disabled={busy !== null}
          icon={<RotateCw size={18} />}
          label="Direita"
        />
      </div>

      {keyboardEnabled && (
        <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {[
            ['←', 'Esquerda'],
            ['→', 'Direita'],
            ['↑', 'Frente'],
            ['↓', 'Trás'],
            ['Shift', 'Sobe'],
            ['Ctrl', 'Desce'],
            ['Espaço', 'Parar'],
          ].map(([keyLabel, action]) => (
            <span
              key={action}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                fontSize: '11px',
                color: C.gray,
                background: '#F3F4F6',
                borderRadius: '6px',
                padding: '3px 8px',
              }}
            >
              <kbd style={{ fontWeight: '700', color: C.dark, fontFamily: 'inherit' }}>{keyLabel}</kbd>
              {action}
            </span>
          ))}
        </div>
      )}

      {!airborne && (
        <div style={{ marginTop: '10px', fontSize: '12px', color: C.gray }}>
          Use <strong style={{ color: C.dark }}>Decolar</strong> antes dos comandos de movimento. Esquerda/Direita giram o drone no próprio eixo.
        </div>
      )}
    </div>
  )
}

function ControlButton({ onClick, onPressStart, onPressEnd, disabled, icon, label, variant }) {
  const [hovered, setHovered] = useState(false)
  const continuous = !!onPressStart

  const pressProps = continuous
    ? {
        onPointerDown: (event) => {
          if (disabled) return
          event.preventDefault()
          try {
            event.currentTarget.setPointerCapture(event.pointerId)
          } catch {
            // navegador sem pointer capture: blur/watchdog cobrem o release
          }
          onPressStart()
        },
        onPointerUp: () => onPressEnd && onPressEnd(),
        onPointerCancel: () => onPressEnd && onPressEnd(),
        onPointerLeave: () => onPressEnd && onPressEnd(),
      }
    : { onClick }

  const palette = {
    primary: { bg: '#16A34A', color: '#fff', border: '#16A34A', hover: '#15803D' },
    warn: { bg: '#FFF7ED', color: '#92400E', border: '#FED7AA', hover: '#FFEDD5' },
    stop: { bg: '#FEF2F2', color: '#B91C1C', border: '#FECACA', hover: '#FEE2E2' },
    default: { bg: '#fff', color: C.dark, border: C.border, hover: '#F9FAFB' },
  }[variant || 'default']

  return (
    <button
      type="button"
      {...pressProps}
      disabled={disabled}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '4px',
        flex: 1,
        padding: '10px 8px',
        borderRadius: '10px',
        border: `1px solid ${disabled ? C.border : palette.border}`,
        background: disabled ? '#F3F4F6' : hovered ? palette.hover : palette.bg,
        color: disabled ? '#9CA3AF' : palette.color,
        fontSize: '12px',
        fontWeight: '600',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'background 0.15s, border-color 0.15s',
      }}
    >
      {icon}
      {label}
    </button>
  )
}

function TelemetryCard({ icon, label, value, badge, live }) {
  return (
    <div
      style={{
        background: '#fff',
        borderRadius: '12px',
        padding: '16px 18px',
        border: `1px solid ${C.border}`,
        display: 'flex',
        alignItems: 'center',
        gap: '14px',
        flex: 1,
      }}
    >
      <div
        style={{
          width: '40px',
          height: '40px',
          background: 'rgba(255,51,102,0.08)',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        {icon}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: '10px',
            fontWeight: '700',
            color: C.gray,
            letterSpacing: '0.6px',
            textTransform: 'uppercase',
            marginBottom: '3px',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
          }}
        >
          {label}
          {live && (
            <span
              style={{
                display: 'inline-block',
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: '#16A34A',
                animation: 'livePulse 1.4s ease-in-out infinite',
              }}
            />
          )}
        </div>
        <div
          style={{
            fontSize: '16px',
            fontWeight: '700',
            color: C.dark,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {value}
        </div>
      </div>
      {badge && (
        <span
          style={{
            padding: '3px 9px',
            borderRadius: '20px',
            background: badge.bg,
            color: badge.color,
            fontSize: '11px',
            fontWeight: '700',
            letterSpacing: '0.4px',
            flexShrink: 0,
          }}
        >
          {badge.text}
        </span>
      )}
    </div>
  )
}

function MapPreview({ drone, onClick }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      data-tour="local-map"
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      aria-label="Abrir mapa da operação em tela cheia"
      style={{
        background: '#fff',
        borderRadius: '14px',
        border: `1px solid ${hovered ? C.pink : C.border}`,
        overflow: 'hidden',
        cursor: 'pointer',
        transition: 'border-color 0.2s, box-shadow 0.2s',
        boxShadow: hovered ? '0 0 0 3px rgba(255,51,102,0.12)' : 'none',
      }}
    >
      <div style={{ height: '200px', position: 'relative' }}>
        {drone?.hasCoords ? (
          <DroneLeafletMap drone={drone} interactive={false} />
        ) : (
          <NeutralLeafletMap interactive={false} />
        )}
        {hovered && (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background: 'rgba(255,51,102,0.04)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              pointerEvents: 'none',
            }}
          >
            <span
              style={{
                background: C.pink,
                color: '#fff',
                padding: '6px 16px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: '600',
              }}
            >
              Clique para expandir o mapa
            </span>
          </div>
        )}
      </div>
      <div
        style={{
          padding: '12px 16px',
          borderTop: `1px solid ${C.border}`,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <MapPin size={14} color={C.pink} />
        <span style={{ fontSize: '13px', fontWeight: '600', color: C.dark }}>
          Mapa da Operação
        </span>
        <span style={{ marginLeft: 'auto', fontSize: '12px', color: C.gray }}>
          {drone?.hasCoords ? drone.coordsLabel : 'Sem destino definido'}
        </span>
      </div>
    </div>
  )
}

function MapModal({ drone, onClose }) {
  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(15,18,36,0.65)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '24px',
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div
        style={{
          background: '#fff',
          borderRadius: '16px',
          overflow: 'hidden',
          width: '100%',
          maxWidth: '780px',
          animation: 'modalIn 0.25s ease',
          boxShadow: '0 24px 64px rgba(0,0,0,0.28)',
        }}
      >
        <div
          style={{
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: `1px solid ${C.border}`,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MapPin size={17} color={C.pink} />
            <span style={{ fontWeight: '700', fontSize: '15px', color: C.dark }}>
              Mapa da Operação
            </span>
            <span style={{ fontSize: '13px', color: C.gray }}>
              · {drone?.coordsLabel || 'Localização indisponível'}
            </span>
          </div>
          <button
            onClick={onClose}
            aria-label="Fechar mapa"
            onMouseEnter={(e) => (e.currentTarget.style.background = '#F3F4F6')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: C.gray,
              transition: 'background 0.15s',
            }}
          >
            <X size={18} />
          </button>
        </div>

        <div style={{ height: '440px', position: 'relative' }}>
          {drone?.hasCoords ? (
            <DroneLeafletMap drone={drone} interactive />
          ) : (
            <NeutralLeafletMap interactive />
          )}
          {drone?.hasCoords && (
            <div
              style={{
                position: 'absolute',
                top: 16,
                right: 16,
                background: 'rgba(255,51,102,0.1)',
                border: '1px solid rgba(255,51,102,0.28)',
                borderRadius: '8px',
                padding: '5px 12px',
                fontSize: '12px',
                color: C.pink,
                fontWeight: '600',
                zIndex: 500,
              }}
            >
              {drone.name}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function NeutralLeafletMap({ interactive }) {
  return (
    <MapContainer
      center={DEFAULT_MAP_CENTER}
      zoom={DEFAULT_MAP_ZOOM}
      scrollWheelZoom={interactive}
      dragging={interactive}
      doubleClickZoom={interactive}
      zoomControl={interactive}
      attributionControl={interactive}
      style={{ width: '100%', height: '100%' }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    </MapContainer>
  )
}

function DroneLeafletMap({ drone, interactive }) {
  return (
    <MapContainer
      center={[drone.latitude, drone.longitude]}
      zoom={15}
      scrollWheelZoom={interactive}
      dragging={interactive}
      doubleClickZoom={interactive}
      zoomControl={interactive}
      attributionControl={interactive}
      style={{ width: '100%', height: '100%' }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker
        position={[drone.latitude, drone.longitude]}
        icon={droneMarker}
      >
        <Popup>
          <strong>{drone.name}</strong>
          <br />
          {drone.coordsLabel}
          <br />
          Status: {drone.status}
        </Popup>
      </Marker>
    </MapContainer>
  )
}

function FeedbackBox({ children, tone }) {
  const tones = {
    error: {
      background: '#FEF2F2',
      border: '#FECACA',
      color: '#B91C1C',
    },
    info: {
      background: '#fff',
      border: C.border,
      color: C.gray,
    },
  }

  return (
    <div
      style={{
        marginBottom: '18px',
        padding: '12px 14px',
        borderRadius: '10px',
        background: tones[tone].background,
        border: `1px solid ${tones[tone].border}`,
        color: tones[tone].color,
        fontSize: '13px',
        fontWeight: '600',
      }}
    >
      {children}
    </div>
  )
}

function statusBadge(status) {
  if (!status) {
    return { text: 'SEM LINK', color: '#991B1B', bg: '#FEF2F2' }
  }

  if (status === 'EM VOO') {
    return { text: status, color: '#166534', bg: '#F0FDF4' }
  }

  return { text: status, color: '#92400E', bg: '#FFF7ED' }
}

function normalizeDrone(drone) {
  const latitude = toNumber(drone.latitude)
  const longitude = toNumber(drone.longitude)
  const hasCoords = latitude !== null && longitude !== null
  const battery = typeof drone.bateria === 'number' ? `${drone.bateria}%` : null
  const status = formatStatus(drone.status_voo)

  return {
    id: drone.id,
    name: drone.nome || drone.id || 'Drone',
    status,
    connectivity: drone.conectividade || null,
    batteryLabel: battery,
    latitude,
    longitude,
    hasCoords,
    isLiveTelemetry: hasLiveTelemetry(drone),
    coordsLabel: hasCoords
      ? `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`
      : 'Localização indisponível',
  }
}

function hasLiveTelemetry(drone) {
  const flags = [drone.telemetria_ativa, drone.conectado, drone.online]
  return flags.some((value) => value === true || value === 'true')
}

function formatStatus(status) {
  if (!status) {
    return 'SEM LINK'
  }

  return String(status).replaceAll('_', ' ').toUpperCase()
}

function toNumber(value) {
  if (value === null || value === undefined || value === '') {
    return null
  }

  const number = Number(value)
  return Number.isFinite(number) ? number : null
}
