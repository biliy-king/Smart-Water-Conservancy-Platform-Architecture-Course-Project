<template>
  <div class="view-switch-panel">
    <div class="panel-title">视角切换</div>
    <div class="view-list">
      <div 
        v-for="view in views" 
        :key="view.id" 
        class="view-item" 
        :class="{ active: selectedView === view.id }"
        @click="selectView(view)"
      >
        <div class="view-rectangle"></div>
        <div class="view-text">{{ view.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const views = ref([
  { id: 1, name: '水库视角' },
  { id: 2, name: '大坝视角' },
  { id: 3, name: '全景视角' },
  { id: 4, name: '地球视角' }
])

const selectedView = ref(1)

const emit = defineEmits(['switch-view'])

function selectView(view) {
  selectedView.value = view.id
  // 触发视角切换事件
  const viewMap = {
    1: 'reservoirView',
    2: 'damView',
    3: 'panoramaView',
    4: 'earthView'
  }
  emit('switch-view', viewMap[view.id] || 'frontendView')
}
</script>

<style scoped>
.view-switch-panel {
  padding: 20px;
  background: rgba(255, 249, 189, 0.65);
}

.panel-title {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #000000;
  margin-bottom: 20px;
}

.view-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.view-item {
  position: relative;
  width: 240px;
  height: 57px;
  margin-bottom: 0;
  cursor: pointer;
  transition: all 0.3s;
}

.view-item:not(:last-child) {
  border-bottom: 3px solid #9E9D8C;
}

.view-rectangle {
  position: absolute;
  width: 240px;
  height: 57px;
  background: #FFFCD5;
  border: 3px solid #9E9D8C;
  transition: background 0.3s;
}

.view-item.active .view-rectangle {
  background: #D9D9D9;
}

.view-text {
  position: absolute;
  left: 52px;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
  line-height: 1.21;
}
</style>
