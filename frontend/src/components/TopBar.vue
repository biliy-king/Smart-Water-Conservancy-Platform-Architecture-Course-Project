<template>
  <div class="top-bar">
    <div class="title">青山水电站防汛安全在线监控系统</div>
    <div class="right-info">
      <span class="time">{{ now }}</span>
      <el-avatar icon="el-icon-user" size="small" style="margin-left: 16px;" />
      <span class="user">管理员</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const now = ref('')
function updateTime() {
  const d = new Date()
  now.value = d.toLocaleString('zh-CN', { hour12: false })
}
onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000)
})
</script>

<style scoped>
.top-bar {
  width: 100vw;
  height: 50px;
  background: linear-gradient(90deg, #0a1a2a 60%, #1a2736 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  box-sizing: border-box;
  font-size: 18px;
}
.title {
  font-weight: bold;
  letter-spacing: 2px;
}
.right-info {
  display: flex;
  align-items: center;
  font-size: 15px;
}
.time {
  margin-right: 12px;
}
.user {
  margin-left: 8px;
}
</style>
