import { useEffect, useState } from 'react'
import { MapPin, AlertTriangle, X } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import { getScanMatches, resolveAssetUrl, validarScan } from '../services/api.js'

const C = {
  pink: '#FF3366',
  dark: '#1A1F36',
  gray: '#6B7280',
  border: '#E5E7EB',
  bg: '#F7F8FA',
}

export default function AlertCenter({ onLogout, onNavigate, currentScreen, activeTourStep }) {
  const [scans, setScans] = useState([])
  const [selectedScan, setSelectedScan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState('')
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  useEffect(() => {
    loadScans()
  }, [])

  useEffect(() => {
    if (!activeTourStep) {
      return
    }

    if (activeTourStep.openMode === 'alert-decision' && scans[0]) {
      setSelectedScan(scans[0])
      return
    }

    if (selectedScan && activeTourStep.openMode !== 'alert-decision') {
      setSelectedScan(null)
    }
  }, [activeTourStep, scans, selectedScan])

  useEffect(() => {
    if (!activeTourStep) {
      return
    }

    if (activeTourStep.openMode === 'alert-decision' && scans[0]) {
      setSelectedScan(scans[0])
      return
    }

    if (selectedScan && activeTourStep.openMode !== 'alert-decision') {
      setSelectedScan(null)
    }
  }, [activeTourStep, scans, selectedScan])

  async function loadScans() {
    setLoading(true)
    setError('')

    try {
      const data = await getScanMatches()
      const rawScans = Array.isArray(data) ? data : data?.scans || []
      const pendingMatches = rawScans
        .filter((scan) => scan.match === true && scan.status_validacao === 'pendente')
        .map(normalizeScan)

      setScans(pendingMatches)
    } catch (err) {
      setError(err.message || 'Não foi possível carregar os alertas')
      setScans([])
    } finally {
      setLoading(false)
    }
  }

  async function handleValidate(statusValidacao, editedPlate = null, editedColor = null, editedModel = null) {
    if (!selectedScan) {
      return
    }

    setActionLoading(selectedScan.id)
    setError('')
    setSuccessMessage('')

    try {
      await validarScan(selectedScan.id, statusValidacao, editedPlate, editedColor, editedModel)

      setSelectedScan(null)
      setSuccessMessage(
        statusValidacao === 'aprovado'
          ? 'Alerta aprovado com sucesso.'
          : 'Alerta recusado com sucesso.'
      )
      await loadScans()
    } catch (err) {
      setError(err.message || 'Não foi possível validar o scan')
    } finally {
      setActionLoading('')
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: C.bg }}>
      <Sidebar
        onLogout={onLogout}
        currentScreen={currentScreen}
        onNavigate={onNavigate}
      />

      <main style={{ flex: 1, overflowY: 'auto', padding: '32px' }}>
        <div style={{ marginBottom: '28px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: '700', color: C.dark, display: 'inline' }}>
            Central de Alertas
          </h1>
          <span style={{ fontSize: '16px', fontWeight: '400', color: C.gray, marginLeft: '8px' }}>
            / Analista Pier
          </span>
        </div>

        {error && (
          <FeedbackBox tone="error">
            {error}
          </FeedbackBox>
        )}

        {successMessage && (
          <FeedbackBox tone="success">
            {successMessage}
          </FeedbackBox>
        )}

        <section style={{ marginBottom: '36px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '16px',
              marginBottom: '14px',
            }}
          >
            <SectionLabel style={{ marginBottom: 0 }}>
              Alertas Ativos (Matches Positivos)
            </SectionLabel>
            <button
              onClick={loadScans}
              disabled={loading}
              style={{
                padding: '8px 12px',
                borderRadius: '8px',
                border: `1px solid ${loading ? C.border : C.pink}`,
                background: '#fff',
                color: loading ? C.gray : C.pink,
                fontSize: '12px',
                fontWeight: '700',
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              {loading ? 'Atualizando...' : 'Atualizar'}
            </button>
          </div>

          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {scans.map((scan, index) => (
              <AlertCard
                key={scan.id}
                alert={scan}
                onClick={() => setSelectedScan(scan)}
                tourId={index === 0 ? 'alert-card-first' : undefined}
              />
            ))}
            {loading && <AlertCardPending label="Carregando..." />}
          </div>

          {!loading && scans.length === 0 && (
            <EmptyAlertsState />
          )}
        </section>

      </main>

      {selectedScan && (
        <ApprovalModal
          alert={selectedScan}
          loading={actionLoading === selectedScan.id}
          onAccept={(plate, color, model) => handleValidate('aprovado', plate, color, model)}
          onRefuse={(plate, color, model) => handleValidate('rejeitado', plate, color, model)}
          onClose={() => setSelectedScan(null)}
        />
      )}
    </div>
  )
}

function SectionLabel({ children, style }) {
  return (
    <p
      style={{
        fontSize: '11px',
        fontWeight: '700',
        color: C.gray,
        letterSpacing: '1.2px',
        textTransform: 'uppercase',
        marginBottom: '14px',
        ...style,
      }}
    >
      {children}
    </p>
  )
}

function FeedbackBox({ children, tone }) {
  const tones = {
    error: {
      background: '#FEF2F2',
      border: '#FECACA',
      color: '#B91C1C',
    },
    success: {
      background: '#F0FDF4',
      border: '#BBF7D0',
      color: '#166534',
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

function AlertCard({ alert, onClick, tourId }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      data-tour={tourId}
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: hovered ? '#FEE2E2' : '#FEF2F2',
        border: `2px solid ${hovered ? '#EF4444' : '#FECACA'}`,
        borderRadius: '12px',
        padding: '16px',
        cursor: 'pointer',
        width: '290px',
        transition: 'all 0.18s',
        boxShadow: hovered ? '0 4px 16px rgba(239,68,68,0.14)' : 'none',
        display: 'flex',
        gap: '14px',
        animation: 'fadeIn 0.3s ease',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: '10px',
            fontWeight: '700',
            color: '#EF4444',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            marginBottom: '6px',
          }}
        >
          Alerta (Roubo)
        </div>
        <div style={{ fontSize: '15px', fontWeight: '700', color: C.dark, marginBottom: '5px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {alert.plate}
          <span style={{ fontWeight: '400', color: C.gray, fontSize: '13px', marginLeft: '8px' }}>
            | {alert.time}
          </span>
        </div>
        <div style={{ fontSize: '13px', color: C.gray, display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
          <MapPin size={12} style={{ flexShrink: 0 }} />
          <span title={alert.location} style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {alert.location}
          </span>
        </div>
        <div title={alert.model} style={{ fontSize: '12px', color: C.gray, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          <strong>Modelo:</strong> {alert.model}
        </div>
        <div title={alert.color} style={{ fontSize: '12px', color: C.gray, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          <strong>Cor:</strong> {alert.color}
        </div>
      </div>
      <AlertImage
        src={alert.imageUrl}
        alt={`Imagem do scan ${alert.plate}`}
        width="68px"
        height="68px"
        borderRadius="8px"
      />
    </div>
  )
}

function AlertCardPending({ label }) {
  return (
    <div
      style={{
        border: '2px dashed #FECACA',
        borderRadius: '12px',
        padding: '16px',
        width: '290px',
        minHeight: '104px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: '10px',
            fontWeight: '700',
            color: '#F87171',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            marginBottom: '6px',
          }}
        >
          Alerta (Roubo)
        </div>
        <div style={{ fontSize: '13px', color: '#F87171' }}>{label}</div>
      </div>
    </div>
  )
}

function EmptyAlertsState() {
  return (
    <div
      style={{
        padding: '28px',
        borderRadius: '12px',
        background: '#fff',
        border: `1px solid ${C.border}`,
        color: C.gray,
        fontSize: '14px',
      }}
    >
      Nenhum match pendente para validação no momento.
    </div>
  )
}


function ApprovalModal({ alert, loading, onAccept, onRefuse, onClose }) {
  const [editedPlate, setEditedPlate] = useState(alert.plate)
  const [editedColor, setEditedColor] = useState(alert.color)
  const [editedModel, setEditedModel] = useState(alert.model)
  const [hasChanges, setHasChanges] = useState(false)

  const handlePlateChange = (value) => {
    setEditedPlate(value)
    setHasChanges(true)
  }

  const handleColorChange = (value) => {
    setEditedColor(value)
    setHasChanges(true)
  }

  const handleModelChange = (value) => {
    setEditedModel(value)
    setHasChanges(true)
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(15,18,36,0.6)',
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
          borderRadius: '24px',
          width: '90vw',
          height: '85vh',
          maxWidth: '1400px',
          overflow: 'hidden',
          animation: 'modalIn 0.25s ease',
          boxShadow: '0 24px 64px rgba(0,0,0,0.3)',
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <button
          onClick={onClose}
          aria-label="Fechar"
          onMouseEnter={(e) => (e.currentTarget.style.background = '#F3F4F6')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
          style={{
            position: 'absolute',
            top: '14px',
            right: '14px',
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: C.gray,
            transition: 'background 0.15s',
            zIndex: 1,
          }}
        >
          <X size={18} />
        </button>

        <div style={{ display: 'flex', flex: 1, height: '100%' }}>
          <div
            style={{
              flex: 1,
              background: '#F3F4F6',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
            }}
          >
            <AlertImage
              src={alert.imageUrl}
              alt={`Imagem do scan ${alert.plate}`}
              width="100%"
              height="100%"
              borderRadius="0"
              large
            />
            <div
              style={{
                position: 'absolute',
                top: 12,
                left: 12,
                background: 'rgba(239,68,68,0.1)',
                border: '1px solid rgba(239,68,68,0.25)',
                borderRadius: '6px',
                padding: '3px 8px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <AlertTriangle size={11} color="#EF4444" />
              <span style={{ fontSize: '14px', fontWeight: '700', color: '#EF4444', letterSpacing: '0.5px' }}>
                ROUBO
              </span>
            </div>
          </div>

          <div style={{ flex: 1, padding: '48px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: '32px' }}>
              <p
                style={{
                  fontSize: '14px',
                  fontWeight: '700',
                  color: '#EF4444',
                  letterSpacing: '1.4px',
                  textTransform: 'uppercase',
                  marginBottom: '10px',
                }}
              >
                Verificação de Alerta
              </p>
              <h2 style={{ fontSize: '32px', fontWeight: '800', color: C.dark }}>
                ID Drone: <br/> {alert.drone}
              </h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px 40px', marginBottom: 'auto' }}>
              <EditableField 
                label="Placa Identificada" 
                value={editedPlate}
                onChange={handlePlateChange}
                large 
              />
              <EditableField 
                label="Cor" 
                value={editedColor}
                onChange={handleColorChange}
                large 
              />
              <Field label="Localização" value={alert.location} large />
              <EditableField 
                label="Modelo" 
                value={editedModel}
                onChange={handleModelChange}
                large 
              />
            </div>

            {hasChanges && (
              <div style={{
                marginBottom: '16px',
                padding: '12px',
                borderRadius: '8px',
                background: '#FEF3C7',
                border: '1px solid #FCD34D',
                color: '#92400E',
                fontSize: '12px',
                fontWeight: '600'
              }}>
                ✓ Você tem alterações pendentes
              </div>
            )}

            {hasChanges && (
              <div style={{
                marginBottom: '16px',
                padding: '12px',
                borderRadius: '8px',
                background: '#FEF3C7',
                border: '1px solid #FCD34D',
                color: '#92400E',
                fontSize: '12px',
                fontWeight: '600'
              }}>
                ✓ Você tem alterações pendentes
              </div>
            )}

            <div data-tour="alert-decision" style={{ display: 'flex', gap: '16px', marginTop: '40px' }}>
              <button
                onClick={() => onRefuse(editedPlate, editedColor, editedModel)}
                disabled={loading}
                onMouseEnter={(e) => (e.currentTarget.style.background = '#FEF2F2')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                style={{
                  flex: 1,
                  padding: '20px',
                  borderRadius: '14px',
                  border: '2px solid #EF4444',
                  color: '#EF4444',
                  fontSize: '18px',
                  fontWeight: '700',
                  letterSpacing: '0.5px',
                  background: 'transparent',
                  transition: 'background 0.18s',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading ? 'Processando...' : 'Recusar'}
              </button>
              <button
                onClick={() => onAccept(editedPlate, editedColor, editedModel)}
                disabled={loading}
                onMouseEnter={(e) => (e.currentTarget.style.filter = 'brightness(0.88)')}
                onMouseLeave={(e) => (e.currentTarget.style.filter = 'brightness(1)')}
                style={{
                  flex: 1.5,
                  padding: '20px',
                  borderRadius: '14px',
                  background: C.pink,
                  color: '#fff',
                  fontSize: '18px',
                  fontWeight: '700',
                  letterSpacing: '0.5px',
                  transition: 'filter 0.18s',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading ? 'Processando...' : 'Aceitar Resgate'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function AlertImage({ src, alt, width, height, borderRadius, large = false }) {
  if (!src) {
    return (
      <div
        style={{
          width,
          height,
          borderRadius,
          background: '#F3F4F6',
          color: '#9CA3AF',
          fontSize: large ? '12px' : '11px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: '12px',
          letterSpacing: '1px',
          textTransform: 'uppercase',
        }}
      >
        [ Foto da Placa ]
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      style={{
        width,
        height,
        borderRadius,
        objectFit: large ? 'contain' : 'cover',
        display: 'block',
        background: large ? '#111827' : 'transparent',
      }}
    />
  )
}

function EditableField({ label, value, onChange, large }) {
  return (
    <div style={{ minWidth: 0 }}>
      <p style={{ fontSize: large ? '14px' : '10px', fontWeight: '700', color: C.gray, letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: '8px' }}>
        {label}
      </p>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: '100%',
          fontSize: large ? '24px' : '16px',
          fontWeight: '600',
          color: C.dark,
          border: `2px solid ${C.border}`,
          borderRadius: '8px',
          padding: '12px',
          boxSizing: 'border-box',
          transition: 'border-color 0.2s',
        }}
        onFocus={(e) => (e.target.style.borderColor = C.pink)}
        onBlur={(e) => (e.target.style.borderColor = C.border)}
      />
    </div>
  )
}

function Field({ label, value, large }) {
  return (
    <div style={{ minWidth: 0 }}>
      <p style={{ fontSize: large ? '14px' : '10px', fontWeight: '700', color: C.gray, letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: '8px' }}>
        {label}
      </p>
      <p title={value} style={{ fontSize: large ? '24px' : '16px', fontWeight: '600', color: C.dark, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
        {value}
      </p>
    </div>
  )
}

function normalizeScan(scan) {
  return {
    id: scan.id,
    plate: scan.placa || 'Placa não informada',
    time: formatTime(scan.horario_scan),
    location: formatLocation(scan),
    drone: scan.id_drone || scan.drone_id || 'Não informado',
    color: scan.veiculo_cor || scan.cor || 'Não informado',
    model: scan.veiculo_modelo || scan.modelo || 'Não informado',
    imageUrl: resolveAssetUrl(scan.imagem_url),
    acceptedAt: formatTime(scan.validado_em),
    raw: scan,
  }
}

function formatTime(value) {
  if (!value) {
    return '--:--'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return String(value)
  }

  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatLocation(scan) {
  if (scan.localizacao) {
    return scan.localizacao
  }

  if (scan.latitude != null && scan.longitude != null) {
    return `${Number(scan.latitude).toFixed(5)}, ${Number(scan.longitude).toFixed(5)}`
  }

  return 'Localização indisponível'
}
