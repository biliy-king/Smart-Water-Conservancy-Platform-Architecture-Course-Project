<template>
  <div class="effect-panel">
    <div class="panel-title">效果设置</div>
    <div class="effect-list">
      <div 
        v-for="effect in effects" 
        :key="effect.id" 
        class="effect-item"
        :class="{ active: effect.enabled }"
        @click="toggleEffect(effect)"
      >
        <div class="effect-rectangle"></div>
        <div class="effect-text">{{ effect.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['effect-changed'])

const effects = ref([
  { id: 1, name: '抗锯齿', enabled: true, key: 'antiAliasing' },
  { id: 2, name: '光效开关', enabled: true, key: 'lighting' },
  { id: 3, name: '阴影开关', enabled: true, key: 'shadows' }
])

function toggleEffect(effect) {
  effect.enabled = !effect.enabled
  emit('effect-changed', {
    key: effect.key,
    enabled: effect.enabled,
    name: effect.name
  })
  console.log('切换效果:', effect.name, effect.enabled ? '开启' : '关闭')
}
</script>

<style scoped>
.effect-panel {
  padding: 0;
  background: transparent;
  min-width: 240px;
}

.panel-title {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #000000;
  margin-bottom: 0;
  padding: 10px 20px;
  background: rgba(255, 250, 193, 0.9);
  border-radius: 8px 8px 0 0;
}

.effect-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: rgba(255, 250, 193, 0.9);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

.effect-item {
  position: relative;
  width: 240px;
  height: 57px;
  margin-bottom: 0;
  cursor: pointer;
  transition: all 0.3s;
  user-select: none;
}

.effect-item:not(:last-child) {
  border-bottom: 3px solid #9E9D8C;
}

.effect-item:hover {
  opacity: 0.9;
}

.effect-rectangle {
  position: absolute;
  width: 100%;
  height: 100%;
  background: #FFFCD5;
  border: none;
  transition: background 0.3s;
}

.effect-item.active .effect-rectangle {
  background: #D9D9D9;
}

.effect-text {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
  line-height: 1.21;
  pointer-events: none;
  z-index: 1;
}
</style>
