<template>
  <div class="page-scaler-wrapper">
    <div class="page-scaler-content" :style="scalerStyle">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const scale = ref(1)
const designWidth = 2560
const designHeight = 1400

const scalerStyle = ref({
  transform: `scale(${scale.value})`,
  transformOrigin: 'center center',
  width: `${designWidth}px`,
  height: `${designHeight}px`
})

function updateScale() {
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight
  
  // 计算宽度和高度的缩放比例
  const scaleX = windowWidth / designWidth
  const scaleY = windowHeight / designHeight
  
  // 使用较小的缩放比例以确保完全显示
  const newScale = Math.min(scaleX, scaleY, 1)
  
  // 如果缩放后仍然太小，至少保持一定的可读性
  scale.value = newScale < 0.4 ? 0.4 : newScale
  
  scalerStyle.value = {
    transform: `scale(${scale.value})`,
    transformOrigin: 'center center',
    width: `${designWidth}px`,
    height: `${designHeight}px`
  }
}

onMounted(() => {
  updateScale()
  window.addEventListener('resize', updateScale)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScale)
})
</script>

<style scoped>
.page-scaler-wrapper {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background-color: #f5f5f5;
  position: fixed;
  top: 0;
  left: 0;
}

.page-scaler-content {
  transition: transform 0.3s ease;
}
</style>
