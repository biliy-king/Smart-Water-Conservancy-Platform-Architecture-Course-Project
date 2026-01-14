<template>
  <div class="page-scaler-wrapper">
    <div class="page-scaler-content" :style="scalerStyle">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageScaler',
  data() {
    return {
      scale: 1,
      designWidth: 2560,
      designHeight: 1400
    }
  },
  computed: {
    scalerStyle() {
      return {
        transform: `scale(${this.scale})`,
        transformOrigin: 'top center',
        width: `${this.designWidth}px`,
        minHeight: `${this.designHeight}px`
      }
    }
  },
  mounted() {
    this.updateScale()
    window.addEventListener('resize', this.updateScale)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateScale)
  },
  methods: {
    updateScale() {
      const windowWidth = window.innerWidth
      const windowHeight = window.innerHeight
      
      // 计算宽度和高度的缩放比例
      const scaleX = windowWidth / this.designWidth
      const scaleY = windowHeight / this.designHeight
      
      // 使用较小的缩放比例以确保完全显示
      this.scale = Math.min(scaleX, scaleY, 1)
      
      // 如果缩放后仍然太小，至少保持一定的可读性
      if (this.scale < 0.4) {
        this.scale = 0.4
      }
    }
  }
}
</script>

<style scoped>
.page-scaler-wrapper {
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow: auto;
  background-color: #f5f5f5;
  padding: 20px 0;
}

.page-scaler-content {
  transition: transform 0.3s ease;
}
</style>
