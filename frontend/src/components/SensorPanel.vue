<template>
  <div class="sensor-panel">
    <div class="panel-title">传感器信息</div>
    <div class="sensor-list">
      <div v-for="sensor in sensors" :key="sensor.id" class="sensor-item" @click="selectSensor(sensor)">
        <div class="sensor-name">{{ sensor.name }}</div>
        <div class="sensor-status" :class="sensor.status">{{ sensor.statusText }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const sensors = ref([
  { id: 1, name: '传感器1', status: 'normal', statusText: '正常' },
  { id: 2, name: '传感器2', status: 'normal', statusText: '正常' },
  { id: 3, name: '传感器3', status: 'abnormal', statusText: '异常' },
  { id: 4, name: '传感器4', status: 'normal', statusText: '正常' },
  { id: 5, name: '传感器5', status: 'normal', statusText: '正常' }
])

function selectSensor(sensor) {
  console.log('选择传感器:', sensor)
  // 可以触发事件通知父组件
}
</script>

<style scoped>
.sensor-panel {
  padding: 20px;
}

.panel-title {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
  margin-bottom: 20px;
}

.sensor-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sensor-item {
  padding: 12px;
  background: #FFFFFF;
  border: 1px solid #D9D9D9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.sensor-item:hover {
  background: #F5F5F5;
  border-color: #000000;
}

.sensor-name {
  font-size: 18px;
  font-weight: 500;
  color: #000000;
  margin-bottom: 8px;
}

.sensor-status {
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.sensor-status.normal {
  background: #6DEC61;
  color: #000000;
}

.sensor-status.abnormal {
  background: #FF5227;
  color: #FFFFFF;
}
</style>
