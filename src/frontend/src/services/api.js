const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
const ASSET_BASE_URL = import.meta.env.VITE_ASSET_BASE_URL || ''

function getStoredToken() {
  return localStorage.getItem('token')
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {})

  if (!headers.has('Content-Type') && options.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }

  const token = getStoredToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const message =
      (payload && typeof payload === 'object' && payload.message) ||
      (typeof payload === 'string' && payload) ||
      `Erro HTTP ${response.status}`
    throw new Error(message)
  }

  return payload
}

export async function login(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function getScanMatches() {
  return request('/scans/?match=true&status=pendente')
}

export async function getApprovedScans() {
  return request('/scans/matches')
}

export async function getRejectedScans() {
  return request('/scans/?match=true&status=rejeitado')
}

export async function getAllMatchScans(perPage = 100) {
  let page = 1
  let allScans = []
  let total = Infinity

  while (allScans.length < total) {
    const response = await request(`/scans/?match=true&per_page=${perPage}&page=${page}`)
    const scans = Array.isArray(response) ? response : response?.scans || []
    total = typeof response?.total === 'number' ? response.total : scans.length
    allScans = allScans.concat(scans)

    if (scans.length < perPage) {
      break
    }

    page += 1
  }

  return allScans
}

export async function getDrones() {
  return request('/drones/?per_page=50')
}

export async function validarScan(scanId, statusValidacao, placa = null, cor = null, modelo = null) {
  const body = { status_validacao: statusValidacao }
  if (placa) body.placa = placa
  if (cor) body.cor = cor
  if (modelo) body.modelo = modelo
  return request(`/scans/${scanId}/validar`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  })
}

export function resolveAssetUrl(path) {
  if (!path) {
    return ''
  }

  if (/^https?:\/\//i.test(path)) {
    return path
  }

  return `${ASSET_BASE_URL}/${String(path).replace(/^\/+/, '')}`
}

export { API_BASE_URL, ASSET_BASE_URL }
