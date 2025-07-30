import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ImageGallery from '../views/ImageGallery.vue'
import TreeView from '../views/TreeView.vue'
import TagManagement from '../views/TagManagement.vue'
import ProjectManagement from '../views/ProjectManagement.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/gallery',
    name: 'ImageGallery',
    component: ImageGallery
  },
  {
    path: '/tree',
    name: 'TreeView',
    component: TreeView
  },
  {
    path: '/tags',
    name: 'TagManagement',
    component: TagManagement
  },
  {
    path: '/projects',
    name: 'ProjectManagement',
    component: ProjectManagement
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router