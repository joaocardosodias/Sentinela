import { useState } from 'react'
import { LogOut, Bell, ShieldCheck, XCircle, BarChart3 } from 'lucide-react'
import logo from '../../img/logo_pier.png'

const PIER_SCREENS = ['alerts', 'accepted', 'rejected', 'analytics']

export default function Sidebar({ onLogout, currentScreen, onNavigate, acceptedCount = 0 }) {
  const isPier = PIER_SCREENS.includes(currentScreen)

  return (
    <aside
      style={{
        width: '110px',
        minHeight: '100vh',
        background: '#1A1F36',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '20px 0',
        flexShrink: 0,
      }}
    >
      <img
        src={logo}
        alt="Pier"
        style={{ width: '100px', height: 'auto', objectFit: 'contain' }}
      />

      {isPier && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <NavBtn
            icon={<Bell size={18} />}
            label="Alertas"
            active={currentScreen === 'alerts'}
            onClick={() => onNavigate('alerts')}
          />
          <NavBtn
            icon={<ShieldCheck size={18} />}
            label="Confirmados"
            active={currentScreen === 'accepted'}
            onClick={() => onNavigate('accepted')}
            badge={acceptedCount > 0 ? acceptedCount : null}
          />
          <NavBtn
            icon={<XCircle size={18} />}
            label="Recusados"
            active={currentScreen === 'rejected'}
            onClick={() => onNavigate('rejected')}
          />
          <NavBtn
            icon={<BarChart3 size={18} />}
            label="Análises"
            active={currentScreen === 'analytics'}
            onClick={() => onNavigate('analytics')}
          />
        </div>
      )}

      <LogoutBtn onLogout={onLogout} />
    </aside>
  )
}

function NavBtn({ icon, label, active, onClick, badge }) {
  const [hovered, setHovered] = useState(false)
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      title={label}
      style={{
        width: '86px',
        padding: '10px 0',
        borderRadius: '10px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '5px',
        color: active ? '#FF3366' : hovered ? '#fff' : 'rgba(255,255,255,0.35)',
        background: active
          ? 'rgba(255,51,102,0.12)'
          : hovered
          ? 'rgba(255,255,255,0.05)'
          : 'transparent',
        transition: 'all 0.2s',
        position: 'relative',
      }}
    >
      {icon}
      <span style={{ fontSize: '10px', fontWeight: '600', letterSpacing: '0.3px' }}>
        {label}
      </span>
      {badge !== null && (
        <div
          style={{
            position: 'absolute',
            top: '6px',
            right: '6px',
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            background: '#FF3366',
            color: '#fff',
            fontSize: '9px',
            fontWeight: '700',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {badge}
        </div>
      )}
    </button>
  )
}

function LogoutBtn({ onLogout }) {
  const [hovered, setHovered] = useState(false)
  return (
    <button
      onClick={onLogout}
      title="Sair do sistema"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: '40px',
        height: '40px',
        borderRadius: '10px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: hovered ? '#FF3366' : 'rgba(255,255,255,0.35)',
        background: hovered ? 'rgba(255,255,255,0.06)' : 'transparent',
        transition: 'all 0.2s',
      }}
    >
      <LogOut size={18} />
    </button>
  )
}
