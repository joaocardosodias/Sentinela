import { useEffect, useMemo, useState } from 'react'
import { BarChart3, RefreshCw, ShieldCheck, XCircle, Bell, Radar, CalendarDays } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import { getAllMatchScans } from '../services/api.js'

const C = {
  pink: '#FF3366',
  dark: '#1A1F36',
  gray: '#6B7280',
  border: '#E5E7EB',
  bg: '#F7F8FA',
}

export default function Analytics({ onLogout, onNavigate, currentScreen }) {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadAnalytics()
  }, [])

  async function loadAnalytics() {
    setLoading(true)
    setError('')

    try {
      const data = await getAllMatchScans()
      setScans(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Não foi possível carregar as análises')
      setScans([])
    } finally {
      setLoading(false)
    }
  }

  const metrics = useMemo(() => {
    const totalMatches = scans.length
    const approved = scans.filter((scan) => scan.status_validacao === 'aprovado').length
    const rejected = scans.filter((scan) => scan.status_validacao === 'rejeitado').length
    const pending = scans.filter((scan) => scan.status_validacao === 'pendente').length

    const modelCounts = scans.reduce((acc, scan) => {
      const model = normalizeModel(scan)
      acc[model] = (acc[model] || 0) + 1
      return acc
    }, {})

    const droneCounts = scans.reduce((acc, scan) => {
     const drone = normalizeDrone(scan)
     acc[drone] = (acc[drone] || 0) + 1
     return acc
    }, {})

    const dayCounts = scans.reduce((acc, scan) => {
     const day = normalizeDay(scan)
     acc[day] = (acc[day] || 0) + 1
     return acc
    }, {})

    const modelRanking = Object.entries(modelCounts)
     .map(([model, count]) => ({ model, count }))
     .sort((a, b) => b.count - a.count)
     .slice(0, 5)

    const droneRanking = Object.entries(droneCounts)
     .map(([drone, count]) => ({ drone, count }))
     .sort((a, b) => b.count - a.count)
     .slice(0, 5)

    const dayTrend = Object.entries(dayCounts)
     .map(([day, count]) => ({ day, count }))
     .sort((a, b) => a.day.localeCompare(b.day))
     .slice(-7)

    return {
     totalMatches,
     approved,
     rejected,
     pending,
     modelRanking,
     droneRanking,
     dayTrend,
    }
  }, [scans])

  const maxModelCount = Math.max(...metrics.modelRanking.map((item) => item.count), 1)
  const maxDroneCount = Math.max(...metrics.droneRanking.map((item) => item.count), 1)
  const maxDayCount = Math.max(...metrics.dayTrend.map((item) => item.count), 1)

  return (
    <div style={{ display: 'flex', height: '100vh', background: C.bg }}>
      <Sidebar
        onLogout={onLogout}
        currentScreen={currentScreen}
        onNavigate={onNavigate}
      />

      <main style={{ flex: 1, overflowY: 'auto', padding: '32px' }}>
        <div style={{ marginBottom: '28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: '700', color: C.dark, display: 'inline' }}>
              Análises
            </h1>
            <span style={{ fontSize: '16px', fontWeight: '400', color: C.gray, marginLeft: '8px' }}>
              / Gestor Remoto
            </span>
          </div>

          <button
            onClick={loadAnalytics}
            disabled={loading}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 14px',
              borderRadius: '10px',
              border: `1px solid ${C.border}`,
              background: '#fff',
              color: loading ? C.gray : C.dark,
              fontSize: '13px',
              fontWeight: '700',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            <RefreshCw size={14} />
            {loading ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>

        {error && <FeedbackBox tone="error">{error}</FeedbackBox>}

        <section style={{ marginBottom: '28px' }}>
          <SectionLabel>Resumo dos Matches</SectionLabel>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
              gap: '16px',
            }}
          >
            <StatCard
              label="Total de matches"
              value={metrics.totalMatches}
              icon={<Bell size={18} />}
              accent="#FFB020"
            />
            <StatCard
              label="Aprovados"
              value={metrics.approved}
              icon={<ShieldCheck size={18} />}
              accent={C.pink}
            />
            <StatCard
              label="Recusados"
              value={metrics.rejected}
              icon={<XCircle size={18} />}
              accent="#EF4444"
            />
            <StatCard
              label="Pendentes"
              value={metrics.pending}
              icon={<BarChart3 size={18} />}
              accent="#0EA5E9"
            />
          </div>
        </section>

        <section>
          <SectionLabel>Visões principais</SectionLabel>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <ChartCard title="Modelos mais detectados" icon={<BarChart3 size={16} />} loading={loading && scans.length === 0} emptyLabel="Nenhum match disponível para análise.">
              {metrics.modelRanking.map((item) => (
                <RankBar key={item.model} label={item.model} value={item.count} maxValue={maxModelCount} />
              ))}
            </ChartCard>

            <ChartCard title="Drones com mais matches" icon={<Radar size={16} />} loading={loading && scans.length === 0} emptyLabel="Nenhum drone encontrado.">
              {metrics.droneRanking.map((item) => (
                <RankBar key={item.drone} label={item.drone} value={item.count} maxValue={maxDroneCount} accent="#F59E0B" />
              ))}
            </ChartCard>

            <ChartCard title="Volume por dia" icon={<CalendarDays size={16} />} loading={loading && scans.length === 0} emptyLabel="Nenhuma data encontrada.">
              {metrics.dayTrend.map((item) => (
                <RankBar key={item.day} label={item.day} value={item.count} maxValue={maxDayCount} accent="#8B5CF6" compact />
              ))}
            </ChartCard>
          </div>
        </section>

      </main>
    </div>
  )
}

function StatCard({ label, value, icon, accent }) {
  return (
    <div
      style={{
        background: '#fff',
        border: `1px solid ${C.border}`,
        borderRadius: '16px',
        padding: '20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
      }}
    >
      <div>
        <div style={{ fontSize: '12px', fontWeight: '700', color: C.gray, textTransform: 'uppercase', letterSpacing: '0.8px' }}>
          {label}
        </div>
        <div style={{ fontSize: '32px', fontWeight: '800', color: C.dark, marginTop: '8px' }}>
          {value}
        </div>
      </div>
      <div
        style={{
          width: '44px',
          height: '44px',
          borderRadius: '12px',
          background: `${accent}18`,
          color: accent,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        {icon}
      </div>
    </div>
  )
}

function ChartCard({ title, icon, loading, emptyLabel, children }) {
  const content = Array.isArray(children) ? children.filter(Boolean) : children
  const hasItems = Array.isArray(content) ? content.length > 0 : Boolean(content)

  return (
    <div
      style={{
        background: '#fff',
        border: `1px solid ${C.border}`,
        borderRadius: '16px',
        padding: '20px',
        minHeight: '220px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <div
          style={{
            width: '30px',
            height: '30px',
            borderRadius: '10px',
            background: 'rgba(255,51,102,0.08)',
            color: C.pink,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </div>
        <h2 style={{ fontSize: '16px', fontWeight: '800', color: C.dark }}>{title}</h2>
      </div>

      {loading ? (
        <EmptyState label="Carregando análises..." />
      ) : !hasItems ? (
        <EmptyState label={emptyLabel} />
      ) : (
        <div style={{ display: 'grid', gap: '14px' }}>{children}</div>
      )}
    </div>
  )
}

function RankBar({ label, value, maxValue, accent = C.pink, compact = false }) {
  const width = Math.max((value / maxValue) * 100, 6)

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', marginBottom: '6px' }}>
        <span
          style={{
            fontSize: compact ? '13px' : '14px',
            fontWeight: '700',
            color: C.dark,
            minWidth: 0,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
          title={label}
        >
          {label}
        </span>
        <span style={{ fontSize: '13px', fontWeight: '700', color: C.gray }}>
          {value}
        </span>
      </div>
      <div style={{ height: '12px', borderRadius: '999px', background: '#F3F4F6', overflow: 'hidden' }}>
        <div
          style={{
            width: `${width}%`,
            height: '100%',
            borderRadius: '999px',
            background: `linear-gradient(90deg, ${accent}, #FF7A99)`,
          }}
        />
      </div>
    </div>
  )
}

function ModelBar({ label, value, maxValue }) {
  const width = Math.max((value / maxValue) * 100, 6)

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', marginBottom: '6px' }}>
        <span style={{ fontSize: '14px', fontWeight: '700', color: C.dark, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {label}
        </span>
        <span style={{ fontSize: '13px', fontWeight: '700', color: C.gray }}>
          {value}
        </span>
      </div>
      <div style={{ height: '12px', borderRadius: '999px', background: '#F3F4F6', overflow: 'hidden' }}>
        <div
          style={{
            width: `${width}%`,
            height: '100%',
            borderRadius: '999px',
            background: `linear-gradient(90deg, ${C.pink}, #FF7A99)`,
          }}
        />
      </div>
    </div>
  )
}

function MiniStat({ label, value }) {
  return (
    <div
      style={{
        background: '#fff',
        border: `1px solid ${C.border}`,
        borderRadius: '14px',
        padding: '16px',
      }}
    >
      <div style={{ fontSize: '11px', fontWeight: '700', color: C.gray, textTransform: 'uppercase', letterSpacing: '0.8px' }}>
        {label}
      </div>
      <div style={{ fontSize: '24px', fontWeight: '800', color: C.dark, marginTop: '6px' }}>
        {value}
      </div>
    </div>
  )
}

function SectionLabel({ children }) {
  return (
    <p
      style={{
        fontSize: '11px',
        fontWeight: '700',
        color: C.gray,
        letterSpacing: '1.2px',
        textTransform: 'uppercase',
        marginBottom: '14px',
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

function EmptyState({ label }) {
  return (
    <div
      style={{
        padding: '20px',
        borderRadius: '12px',
        background: '#F9FAFB',
        color: C.gray,
        fontSize: '14px',
      }}
    >
      {label}
    </div>
  )
}

function normalizeModel(scan) {
  return scan.veiculo_modelo || scan.modelo || 'Não informado'
}

function normalizeDrone(scan) {
  return scan.id_drone || scan.drone_id || 'Não informado'
}

function normalizeDay(scan) {
  const raw = scan.horario_scan || scan.validado_em || ''
  if (!raw) {
    return 'Sem data'
  }

  return String(raw).slice(0, 10)
}
