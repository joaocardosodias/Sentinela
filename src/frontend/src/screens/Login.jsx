import { useState } from 'react'
import logo from '../../img/logo_pier.png'
import { login as loginRequest } from '../services/api.js'

const C = {
  pink: '#FF3366',
  dark: '#1A1F36',
  gray: '#6B7280',
  border: '#E5E7EB',
}

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [focus, setFocus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await loginRequest(email, password)
      localStorage.setItem('token', data.token)
      localStorage.setItem('role', data.role)
      onLogin(data.role === 'gestor_local' ? 'operations' : 'alerts')
    } catch (err) {
      setError(err.message || 'Não foi possível fazer login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
      <div
        style={{
          flex: '0 0 58%',
          background: 'linear-gradient(150deg, #0D1117 0%, #1A1F36 60%, #0D1117 100%)',
          position: 'relative',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-end',
          padding: '48px',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: `
              linear-gradient(rgba(255,51,102,0.04) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,51,102,0.04) 1px, transparent 1px)
            `,
            backgroundSize: '56px 56px',
            pointerEvents: 'none',
          }}
        />

        {[300, 200, 100].map((size, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: '38%',
              left: '42%',
              transform: 'translate(-50%, -50%)',
              width: size,
              height: size,
              borderRadius: '50%',
              border: `1px solid rgba(255,51,102,${0.12 + i * 0.1})`,
              pointerEvents: 'none',
            }}
          />
        ))}

        <div
          style={{
            position: 'absolute',
            top: '38%',
            left: '42%',
            transform: 'translate(-50%, -50%)',
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: C.pink,
            boxShadow: `0 0 18px ${C.pink}`,
            pointerEvents: 'none',
          }}
        />

        <div style={{ position: 'absolute', top: 32, left: 32 }}>
          <span
            style={{
              background: 'rgba(255,51,102,0.12)',
              border: '1px solid rgba(255,51,102,0.28)',
              borderRadius: '6px',
              padding: '4px 10px',
              color: C.pink,
              fontSize: '11px',
              fontWeight: '600',
              letterSpacing: '1.4px',
              textTransform: 'uppercase',
            }}
          >
            Sistema Ativo
          </span>
        </div>

        <div style={{ position: 'relative' }}>
          <h2
            style={{
              color: '#fff',
              fontSize: '30px',
              fontWeight: '700',
              lineHeight: 1.25,
              marginBottom: '14px',
            }}
          >
            Fiscalização Aérea
            <br />
            <span style={{ color: C.pink }}>Automatizada</span>
          </h2>
          <p
            style={{
              color: 'rgba(255,255,255,0.42)',
              fontSize: '14px',
              lineHeight: 1.7,
              maxWidth: '360px',
            }}
          >
            Drones com visão computacional para recuperação de veículos
            roubados em tempo real.
          </p>
        </div>
      </div>

      <div
        style={{
          flex: 1,
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '48px',
        }}
      >
        <form style={{ width: '100%', maxWidth: '376px' }} onSubmit={handleSubmit}>
          <img
            src={logo}
            alt="Pier"
            style={{ height: '44px', width: 'auto', objectFit: 'contain', marginBottom: '28px' }}
          />

          <h1
            style={{
              fontSize: '26px',
              fontWeight: '700',
              color: C.dark,
              marginBottom: '6px',
            }}
          >
            Bem-vindo
          </h1>
          <p style={{ color: C.gray, fontSize: '14px', marginBottom: '32px' }}>
            Acesse o Sistema de Recuperação
          </p>

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

          <div style={{ marginBottom: '18px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: '600',
                color: C.dark,
                marginBottom: '7px',
              }}
            >
              Usuário
            </label>
            <input
              type="email"
              placeholder="seu.email@pier.digital"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setFocus('email')}
              onBlur={() => setFocus(null)}
              style={{
                display: 'block',
                width: '100%',
                padding: '13px 16px',
                border: `2px solid ${focus === 'email' ? C.pink : C.border}`,
                borderRadius: '10px',
                fontSize: '14px',
                color: C.dark,
                background: '#FAFAFA',
                transition: 'border-color 0.18s',
              }}
            />
          </div>

          <div style={{ marginBottom: '28px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: '600',
                color: C.dark,
                marginBottom: '7px',
              }}
            >
              Senha
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => setFocus('password')}
              onBlur={() => setFocus(null)}
              style={{
                display: 'block',
                width: '100%',
                padding: '13px 16px',
                border: `2px solid ${focus === 'password' ? C.pink : C.border}`,
                borderRadius: '10px',
                fontSize: '14px',
                color: C.dark,
                background: '#FAFAFA',
                transition: 'border-color 0.18s',
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            onMouseEnter={(e) => (e.currentTarget.style.filter = 'brightness(0.88)')}
            onMouseLeave={(e) => (e.currentTarget.style.filter = 'brightness(1)')}
            style={{
              width: '100%',
              padding: '14px',
              background: C.pink,
              color: '#fff',
              fontSize: '15px',
              fontWeight: '700',
              borderRadius: '12px',
              letterSpacing: '0.2px',
              transition: 'filter 0.18s',
              marginBottom: '20px',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Entrando...' : 'Entrar no Sistema'}
          </button>

        </form>
      </div>
    </div>
  )
}
