import { defineStore } from 'pinia'
import type { TabItem } from '@/types/index'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useTabsStore = defineStore('tabs', () => {
  const router = useRouter()

  const tabs = ref<TabItem[]>([
    {
      name: 'dashboard',
      title: '首页',
      path: '/dashboard',
      closable: false
    }
  ])

  const activeTab = ref('dashboard')

  // 自动修正 activeTab，如果当前不存在则回退到 fallback
  const ensureActiveTabExists = (fallback: string) => {
    if (!tabs.value.find(t => t.name === activeTab.value)) {
      activeTab.value = fallback
      if (fallback) {
        const target = tabs.value.find(t => t.name === fallback)
        if (target) {
          router.push(target.path)
        }
      }
    }
  }

  const addTab = (tab: TabItem) => {
    const exists = tabs.value.find(item => item.name === tab.name)
    if (!exists) {
      tabs.value.push(tab)
    }
    activeTab.value = tab.name
  }

  const removeTab = (name: string) => {
    const index = tabs.value.findIndex(tab => tab.name === name)
    if (index > -1) {
      tabs.value.splice(index, 1)
      ensureActiveTabExists(tabs.value[Math.max(0, index - 1)]?.name || '')
    }
  }

  const removeOtherTabs = (name: string) => {
    tabs.value = tabs.value.filter(tab => tab.name === name || !tab.closable)
    ensureActiveTabExists(name)
  }

  const removeLeftTabs = (name: string) => {
    const index = tabs.value.findIndex(tab => tab.name === name)
    if (index > -1) {
      tabs.value = tabs.value.filter((tab, i) => i >= index || !tab.closable)
      ensureActiveTabExists(name)
    }
  }

  const removeRightTabs = (name: string) => {
    const index = tabs.value.findIndex(tab => tab.name === name)
    if (index > -1) {
      tabs.value = tabs.value.filter((tab, i) => i <= index || !tab.closable)
      ensureActiveTabExists(name)
    }
  }

  const removeAllTabs = () => {
    tabs.value = tabs.value.filter(tab => !tab.closable)
    ensureActiveTabExists(tabs.value[0]?.name || '')
  }

  return {
    tabs,
    activeTab,
    addTab,
    removeTab,
    removeOtherTabs,
    removeLeftTabs,
    removeRightTabs,
    removeAllTabs
  }
})