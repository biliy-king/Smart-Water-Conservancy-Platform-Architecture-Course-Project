<template>
  <div id="app">
    <PageScaler>
      <router-view/>
    </PageScaler>
    
    <!-- 页面切换按钮 -->
    <div class="page-switcher">
      <button @click="toggleMenu" class="switcher-btn">{{ showMenu ? '✕' : '☰' }}</button>
      <transition name="slide">
        <div v-if="showMenu" class="menu-list">
          <div 
            v-for="(page, index) in pages" 
            :key="page.path"
            @click="navigateTo(page.path)"
            class="menu-item"
            :class="{ active: currentPath === page.path }"
          >
            <span class="page-number">{{ index + 1 }}</span>
            <span class="page-name">{{ page.name }}</span>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import PageScaler from './components/PageScaler.vue'

export default {
  components: {
    PageScaler
  },
  data() {
    return {
      showMenu: false,
      pages: [
        { path: '/lanhu_androidexpanded3', name: 'Android Expanded 3' },
        { path: '/lanhu_groupandroidexpanded1', name: 'Group Android Expanded 1' },
        { path: '/lanhu_frame3', name: 'Frame 3' },
        { path: '/lanhu_androidexpanded2', name: 'Android Expanded 2' },
        { path: '/lanhu_androidexpanded4', name: 'Android Expanded 4' },
        { path: '/lanhu_frame4', name: 'Frame 4' }
      ]
    }
  },
  computed: {
    currentPath() {
      return this.$route.path
    }
  },
  methods: {
    toggleMenu() {
      this.showMenu = !this.showMenu
    },
    navigateTo(path) {
      this.$router.push(path)
      this.showMenu = false
    }
  }
}
</script>

<style lang="css" src="./assets/common.css"></style>

<style scoped>
.page-switcher {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
}

.switcher-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.switcher-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.switcher-btn:active {
  transform: scale(0.95);
}

.menu-list {
  position: absolute;
  top: 60px;
  right: 0;
  background: white;
  border-radius: 10px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  min-width: 250px;
  overflow: hidden;
}

.menu-item {
  padding: 15px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: #f8f9ff;
  transform: translateX(-3px);
}

.menu-item.active {
  background: linear-gradient(90deg, #667eea15 0%, #764ba215 100%);
  border-left: 3px solid #667eea;
}

.page-number {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;
}

.page-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.menu-item.active .page-name {
  color: #667eea;
  font-weight: 600;
}

/* 动画效果 */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter, .slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
