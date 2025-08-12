import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'
import Home from '@/views/Home.vue'
import ImageGallery from '@/views/ImageGallery.vue'
import TreeView from '@/views/TreeView.vue'
import TagManagement from '@/views/TagManagement.vue'
import ProjectManagement from '@/views/ProjectManagement.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '/dashboard',
        name: 'dashboard',
        component: Home,
        meta: { title: '首页' }
      },
      {
        path: '/projects',
        name: 'ProjectManagement',
        component: ProjectManagement,
        meta: { title: '项目管理' }
      },
      {
        path: '/gallery',
        name: 'ImageGallery',
        component: ImageGallery,
        meta: { title: '图库管理' }
      },
      {
        path: '/tree',
        name: 'TreeView',
        component: TreeView,
        meta: { title: '树形浏览' }
      },
      {
        path: '/tags',
        name: 'TagManagement',
        component: TagManagement,
        meta: { title: '标签管理' }
      }
    ]
  }
]


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
