import { defineStore } from 'pinia'
import type { UserInfo } from '@/types'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo>({
    username: 'Admin',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    email: 'admin@example.com',
    role: '管理员'
  })

  const logout = () => {
    // 清除用户信息和登录状态
    userInfo.value = {} as UserInfo
    // 跳转到登录页
    // router.push('/login')
  }

  return {
    userInfo,
    logout
  }
})
