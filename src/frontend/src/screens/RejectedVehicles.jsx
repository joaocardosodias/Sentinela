import { useEffect, useState } from 'react'
import { XCircle, MapPin, Clock, X } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import { getRejectedScans, resolveAssetUrl } from '../services/api.js'

const C = {
  red: '#EF4444',
  dark: '#1A1F36',
  gray: '#6B7280',
  border: '#E5E7EB',
  bg: '#F7F8FA',
}

export default function RejectedVehicles({ onLogout, onNavigate, currentScreen, activeTourStep }) {
  const [rejectedVehicles, setRejectedVehicles] = useState([])
  const [selectedScan, setSelectedScan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadRejectedScans()
  }, [])

  useEffect(() => {
    if (!activeTourStep) {
      return
    }

    if (activeTourStep.openMode === 'rejected-detail' && rejectedVehicles[0]) {
      setSelectedScan(rejectedVehicles[0])
      return
    }

    if (selectedScan && activeTourStep.openMode !== 'rejected-detail') {
      setSelectedScan(null)
    }
  }, [activeTourStep, rejectedVehicles, selectedScan])

  async function loadRejectedScans() {
    setLoading(true)
    setError('')

    try {
      const data = await getRejectedScans()
      const rawScans = Array.isArray(data) ? data : data?.scans || []
      const rejected = rawScans
        .filter((scan) => scan.match === true && scan.status_validacao === 'rejeitado')
        .map(normalizeRejectedScan)

      setRejectedVehicles(rejected)
    } catch (err) {
      setError(err.message || 'Não foi possível carregar os veículos recusados')
    } finally {
      setLoading(false)
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
            Veículos Recusados
          </h1>
          <span style={{ fontSize: '16px', fontWeight: '400', color: C.gray, marginLeft: '8px' }}>
            / Analista Pier
          </span>
        </div>

        {error && (
          <div
            style={{
              marginBottom: '18px',
              padding: '12px 14px',
              borderRadius: '10px',
              background: '#FEF2F2',
              border: '1px solid #FECACA',
              color: '#B91C1C',
              fontSize: '13px',
              fontWeight: '600',
            }}
          >
            {error}
          </div>
        )}

        {loading && (
          <div
            style={{
              marginBottom: '18px',
              padding: '12px 14px',
              borderRadius: '10px',
              background: '#fff',
              border: `1px solid ${C.border}`,
              color: C.gray,
              fontSize: '13px',
              fontWeight: '600',
            }}
          >
            Carregando recusados...
          </div>
        )}

        {rejectedVehicles.length === 0 ? (
          <EmptyState />
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '16px',
            }}
          >
            {rejectedVehicles.map((v, i) => (
              <VehicleCard
                key={`${v.plate}-${i}`}
                vehicle={v}
                onClick={() => setSelectedScan(v)}
                tourId={i === 0 ? 'rejected-card-first' : undefined}
              />
            ))}
          </div>
        )}
      </main>

      {selectedScan && (
        <VehicleModal vehicle={selectedScan} onClose={() => setSelectedScan(null)} />
      )}
    </div>
  )
}

function VehicleCard({ vehicle, onClick, tourId }) {
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
        background: '#fff',
        borderRadius: '14px',
        border: `1px solid ${hovered ? C.red : C.border}`,
        overflow: 'hidden',
        animation: 'fadeIn 0.3s ease',
        cursor: 'pointer',
        transition: 'all 0.18s',
        boxShadow: hovered ? '0 4px 16px rgba(239,68,68,0.14)' : 'none',
      }}
    >
      <div
        data-tour="rejected-detail"
        style={{
          height: '120px',
          background: '#F3F4F6',
          position: 'relative',
        }}
      >
        {vehicle.imageUrl ? (
          <img
            src={vehicle.imageUrl}
            alt={`Imagem do veículo ${vehicle.plate}`}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              display: 'block',
              filter: 'grayscale(100%)',
            }}
          />
        ) : (
          <div
            style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span
              style={{
                color: '#9CA3AF',
                fontSize: '12px',
                letterSpacing: '1px',
                textTransform: 'uppercase',
              }}
            >
              Imagem não disponível
            </span>
          </div>
        )}
        <div
          style={{
            position: 'absolute',
            top: 10,
            left: 10,
            background: 'rgba(239,68,68,0.1)',
            border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: '6px',
            padding: '3px 8px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          <XCircle size={11} color={C.red} />
          <span
            style={{
              fontSize: '10px',
              fontWeight: '700',
              color: C.red,
              letterSpacing: '0.5px',
            }}
          >
            RECUSADO
          </span>
        </div>
      </div>

      <div style={{ padding: '16px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px',
          }}
        >
          <span style={{ fontSize: '18px', fontWeight: '800', color: C.dark }}>
            {vehicle.plate}
          </span>
          <span
            style={{
              fontSize: '12px',
              fontWeight: '600',
              color: C.gray,
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Clock size={12} />
            {vehicle.rejectedAt}
          </span>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '10px 16px',
          }}
        >
          <Detail label="Modelo" value={vehicle.model} />
          <Detail label="Cor" value={vehicle.color} />
          <Detail label="Drone" value={vehicle.drone} />
          <Detail
            label="Local"
            value={vehicle.location}
            icon={<MapPin size={11} color={C.gray} />}
          />
        </div>
      </div>
    </div>
  )
}

function Detail({ label, value, icon }) {
  return (
    <div style={{ minWidth: 0 }}>
      <p
        style={{
          fontSize: '10px',
          fontWeight: '700',
          color: C.gray,
          letterSpacing: '0.5px',
          textTransform: 'uppercase',
          marginBottom: '2px',
        }}
      >
        {label}
      </p>
      <div
        title={value}
        style={{
          fontSize: '13px',
          fontWeight: '600',
          color: C.dark,
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
        }}
      >
        {icon && <span style={{ flexShrink: 0, display: 'flex' }}>{icon}</span>}
        <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', minWidth: 0 }}>
          {value}
        </span>
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '80px 0',
        color: C.gray,
      }}
    >
      <div
        style={{
          width: '64px',
          height: '64px',
          borderRadius: '16px',
          background: 'rgba(239,68,68,0.06)',
          border: '1px solid rgba(239,68,68,0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '16px',
        }}
      >
        <XCircle size={28} color="rgba(239,68,68,0.4)" />
      </div>
      <p style={{ fontSize: '15px', fontWeight: '600', color: C.dark, marginBottom: '6px' }}>
        Nenhum veículo recusado
      </p>
      <p style={{ fontSize: '13px', color: C.gray }}>
        Os alertas recusados na Central de Alertas aparecerão aqui.
      </p>
    </div>
  )
}

function normalizeRejectedScan(scan) {
  return {
    id: scan.id,
    plate: scan.placa || 'Placa não informada',
    rejectedAt: formatTime(scan.validado_em || scan.horario_scan),
    model: scan.veiculo_modelo || scan.modelo || 'Não informado',
    color: scan.veiculo_cor || scan.cor || 'Não informado',
    drone: scan.id_drone || scan.drone_id || 'Não informado',
    location: formatLocation(scan),
    imageUrl: resolveAssetUrl(scan.imagem_url),
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

function VehicleModal({ vehicle, onClose }) {
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
            {vehicle.imageUrl ? (
              <img
                src={vehicle.imageUrl}
                alt={`Imagem do veículo ${vehicle.plate}`}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                  display: 'block',
                  background: '#111827',
                }}
              />
            ) : (
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#9CA3AF',
                  fontSize: '12px',
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                }}
              >
                [ Foto da Placa ]
              </div>
            )}
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
              <XCircle size={11} color={C.red} />
              <span style={{ fontSize: '14px', fontWeight: '700', color: C.red, letterSpacing: '0.5px' }}>
                RECUSADO
              </span>
            </div>
          </div>

          <div style={{ flex: 1, padding: '48px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: '32px' }}>
              <p
                style={{
                  fontSize: '14px',
                  fontWeight: '700',
                  color: C.red,
                  letterSpacing: '1.4px',
                  textTransform: 'uppercase',
                  marginBottom: '10px',
                }}
              >
                Detalhes do Veículo
              </p>
              <h2 style={{ fontSize: '32px', fontWeight: '800', color: C.dark }}>
                ID Drone: <br/> {vehicle.drone}
              </h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px 40px', marginBottom: 'auto' }}>
              <Field label="Placa Identificada" value={vehicle.plate} large />
              <Field label="Cor" value={vehicle.color} large />
              <Field label="Localização" value={vehicle.location} large />
              <Field label="Modelo" value={vehicle.model} large />
              <Field label="Rejeitado Em" value={vehicle.rejectedAt} large />
            </div>
          </div>
        </div>
      </div>
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
