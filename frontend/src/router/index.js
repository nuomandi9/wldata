import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user.js'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/Home.vue'),
      },
      {
        path: 'import',
        name: 'Import',
        component: () => import('../views/import/Index.vue'),
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/report/Index.vue'),
      },
      {
        path: 'dict/person',
        name: 'DictPerson',
        component: () => import('../views/dict/Person.vue'),
      },
      {
        path: 'dict/vehicle',
        name: 'DictVehicle',
        component: () => import('../views/dict/Vehicle.vue'),
      },
      {
        path: 'dict/route',
        name: 'DictRoute',
        component: () => import('../views/dict/Route.vue'),
      },
      {
        path: 'dict/customer',
        name: 'DictCustomer',
        component: () => import('../views/dict/Customer.vue'),
      },
      {
        path: 'dict/cigarette',
        name: 'DictCigarette',
        component: () => import('../views/dict/Cigarette.vue'),
      },
      {
        path: 'system/audit',
        name: 'AuditLog',
        component: () => import('../views/system/AuditLog.vue'),
        meta: { adminOnly: true },
      },
      {
        path: 'system/users',
        name: 'Users',
        component: () => import('../views/system/Users.vue'),
        meta: { adminOnly: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.public) {
    next()
    return
  }
  if (!token) {
    next('/login')
    return
  }
  const userStore = useUserStore()
  if (!userStore.userInfo) {
    try {
      await userStore.fetchUser()
    } catch {
      next('/login')
      return
    }
  }
  if (to.meta.adminOnly && userStore.userInfo?.role !== 'admin') {
    next('/')
    return
  }
  next()
})

export default router
