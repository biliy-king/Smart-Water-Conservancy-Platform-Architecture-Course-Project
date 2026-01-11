<template>
  <div class="effect-panel">
    <el-card shadow="never" class="panel-card">
      <div class="panel-title">效果调整</div>
      <el-switch v-model="showPoints" active-text="显示测点" inactive-text="隐藏测点" />
      <el-switch v-model="showLabels" active-text="显示标签" inactive-text="隐藏标签" />
      <el-select v-model="selectedEffect" placeholder="选择效果" style="width: 100%; margin: 10px 0;">
        <el-option label="默认" value="default" />
        <el-option label="高亮" value="highlight" />
        <el-option label="夜间" value="night" />
      </el-select>
      <el-slider v-model="opacity" :min="0" :max="1" :step="0.01" show-input />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const showPoints = ref(true)
const showLabels = ref(true)
const selectedEffect = ref('default')
const opacity = ref(1)
</script>

<style scoped>
.effect-panel {
  padding: 12px 8px 0 8px;
  background: #223044;
}
.panel-card {
  background: #223044;
  color: #fff;
  border: none;
}
.panel-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}
</style>
