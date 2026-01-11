<template>
  <div class="view-switch-panel">
    <el-card shadow="never" class="panel-card">
      <div class="panel-title">视角切换</div>
      <el-button-group>
        <el-button type="primary" size="small">俯视角</el-button>
        <el-button type="primary" size="small">功能角</el-button>
        <el-button type="primary" size="small">场景角</el-button>
      </el-button-group>
    </el-card>
  </div>
</template>

<script setup>
// 可根据需要添加视角切换逻辑
</script>

<style scoped>
.view-switch-panel {
  padding: 12px 8px;
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
