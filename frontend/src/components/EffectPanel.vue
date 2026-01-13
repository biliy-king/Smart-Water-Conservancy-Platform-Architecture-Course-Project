<template>
  <div class="effect-panel">
    <div class="panel-title">效果设置</div>
    <div class="effect-list">
      <div 
        v-for="effect in effects" 
        :key="effect.id" 
        class="effect-item"
        :class="{ active: selectedEffect === effect.id }"
        @click="selectEffect(effect)"
      >
        <div class="effect-rectangle"></div>
        <div class="effect-text">{{ effect.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const effects = ref([
  { id: 1, name: '抗锯齿' },
  { id: 2, name: '光效开关' },
  { id: 3, name: '阴影开关' }
])

const selectedEffect = ref(null)

function selectEffect(effect) {
  if (selectedEffect.value === effect.id) {
    selectedEffect.value = null
  } else {
    selectedEffect.value = effect.id
  }
  console.log('切换效果:', effect.name, selectedEffect.value ? '开启' : '关闭')
}
</script>

<style scoped>
.effect-panel {
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

.effect-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.effect-item {
  position: relative;
  width: 240px;
  height: 57px;
  margin-bottom: 0;
  cursor: pointer;
  transition: all 0.3s;
}

.effect-item:not(:last-child) {
  border-bottom: 3px solid #9E9D8C;
}

.effect-rectangle {
  position: absolute;
  width: 240px;
  height: 57px;
  background: #FFFCD5;
  border: 3px solid #9E9D8C;
  transition: background 0.3s;
}

.effect-item.active .effect-rectangle {
  background: #D9D9D9;
}

.effect-text {
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
