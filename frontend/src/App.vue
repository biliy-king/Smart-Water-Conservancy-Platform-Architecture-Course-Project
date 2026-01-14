<template>
  <PageScaler>
    <div class="main-container">
      <!-- 登录界面 -->
      <LoginPage 
        v-if="currentView === 'login'"
        @close="handleLoginSuccess"
        @switch-to-register="currentView = 'register'"
      />
      
      <!-- 注册界面 -->
      <RegisterPage 
        v-else-if="currentView === 'register'"
        @close="handleRegisterSuccess"
        @switch-to-login="switchView('login')"
      />
      
      <!-- 三维模型界面（需要登录，双重检查） -->
      <SceneView 
        v-else-if="currentView === 'scene' && isLoggedIn"
        @show-login="handleLogout"
        @switch-to-database="switchView('database')"
      />
      
      <!-- 数据库界面（需要登录，双重检查） -->
      <DatabaseViewPage 
        v-else-if="currentView === 'database' && isLoggedIn"
        @show-login="handleLogout"
        @switch-to-scene="switchView('scene')"
      />
      
      <!-- 未登录时访问受保护页面，强制显示登录页 -->
      <LoginPage 
        v-else
        @close="handleLoginSuccess"
        @switch-to-register="switchView('register')"
      />
    </div>
  </PageScaler>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import PageScaler from './components/PageScaler.vue'
import LoginPage from './components/LoginPage.vue'
import RegisterPage from './components/RegisterPage.vue'
import SceneView from './views/SceneView.vue'
import DatabaseViewPage from './views/DatabaseViewPage.vue'
import { useAuth } from './store/auth'

// 使用认证状态管理
const { isLoggedIn, updateAuthStatus, setLoggedIn } = useAuth()

// 当前视图：'login' | 'register' | 'scene' | 'database'
// 默认始终为登录页，只有在确认已登录后才切换
const currentView = ref('login')

// 切换视图的函数，带登录检查
function switchView(view) {
  // 如果尝试访问受保护的页面，必须先检查登录状态
  if (view === 'scene' || view === 'database') {
    updateAuthStatus()
    if (!isLoggedIn.value) {
      console.warn('未登录，无法访问受保护页面')
      currentView.value = 'login'
      return
    }
  }
  currentView.value = view
}

// 监听登录状态变化
watch(isLoggedIn, (newVal) => {
  if (!newVal) {
    // 如果未登录，强制跳转到登录页
    if (currentView.value !== 'login' && currentView.value !== 'register') {
      currentView.value = 'login'
    }
  }
})

// 监听currentView变化，防止未登录访问受保护页面
watch(currentView, (newVal) => {
  // 如果尝试切换到受保护的页面，检查登录状态
  if (newVal === 'scene' || newVal === 'database') {
    updateAuthStatus()
    if (!isLoggedIn.value) {
      console.warn('未登录，重定向到登录页')
      currentView.value = 'login'
    }
  }
})

// 监听localStorage变化（用于跨标签页同步）
function handleStorageChange(e) {
  if (e.key === 'access_token' || e.key === null) {
    updateAuthStatus()
  }
}

// 监听登出事件
function handleAuthLogout() {
  updateAuthStatus()
  if (!isLoggedIn.value) {
    currentView.value = 'login'
  }
}

// 定期检查登录状态的定时器
let checkInterval = null

// 组件挂载时检查登录状态
onMounted(() => {
  // 先更新认证状态
  updateAuthStatus()
  
  // 默认始终显示登录页，确保未登录用户看到登录界面
  // 只有在确认已登录后才切换到大屏
  if (isLoggedIn.value) {
    // 已登录，切换到场景视图
    currentView.value = 'scene'
  } else {
    // 未登录，强制显示登录页（这是默认值，但明确设置确保安全）
    currentView.value = 'login'
  }
  
  // 监听localStorage变化
  window.addEventListener('storage', handleStorageChange)
  // 监听自定义登出事件
  window.addEventListener('auth:logout', handleAuthLogout)
  
  // 定期检查登录状态（每30秒检查一次，防止token被其他标签页清除）
  checkInterval = setInterval(() => {
    updateAuthStatus()
    if (!isLoggedIn.value && (currentView.value === 'scene' || currentView.value === 'database')) {
      currentView.value = 'login'
    }
  }, 30000)
})

// 组件卸载时清理事件监听和定时器
onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
  window.removeEventListener('auth:logout', handleAuthLogout)
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
  }
})

// 处理登录成功
function handleLoginSuccess() {
  setLoggedIn()
  updateAuthStatus()
  if (isLoggedIn.value) {
    switchView('scene')
  } else {
    // 如果登录失败，保持在登录页
    currentView.value = 'login'
  }
}

// 处理注册成功
function handleRegisterSuccess() {
  setLoggedIn()
  updateAuthStatus()
  if (isLoggedIn.value) {
    switchView('scene')
  } else {
    // 如果注册失败，保持在注册页
    currentView.value = 'register'
  }
}

// 处理登出
function handleLogout() {
  switchView('login')
}
</script>

<style scoped>
.main-container {
  width: 2560px;
  height: 1400px;
  overflow: hidden;
  position: relative;
}
</style>
