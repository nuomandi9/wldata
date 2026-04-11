import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getMe } from '../api/auth.js'
import router from '../router/index.js'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  async function login(username, password) {
    const data = await loginApi({ username, password })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    userInfo.value = { username, role: data.role, real_name: data.real_name }
  }

  async function fetchUser() {
    const data = await getMe()
    userInfo.value = data
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, userInfo, login, fetchUser, logout }
})
