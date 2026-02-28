import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../components/MainLayout.vue'
import Home from '../views/Home.vue'
import ProjectDetail from '../views/ProjectDetail.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', name: 'Home', component: Home },
      { path: 'quotations', name: 'Quotations', component: () => import('../views/QuotationList.vue') },
      { path: 'clients', name: 'Clients', component: () => import('../views/ClientList.vue') },
      { path: 'templates', name: 'Templates', component: () => import('../views/TemplateList.vue') }
    ]
  },
  {
    // 工作台采用独立全屏布局，获得最大视野
    path: '/project/:id',
    name: 'ProjectDetail',
    component: ProjectDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
