import request from './request.js'

export function login(data) {
  return request.post('/api/auth/login', data)
}

export function getMe() {
  return request.get('/api/auth/me')
}
