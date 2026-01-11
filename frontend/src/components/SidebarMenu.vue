<template>
  <div class="sidebar-menu">
    <el-menu default-active="scene" class="el-menu-vertical-demo" background-color="#1a2736" text-color="#fff" active-text-color="#ffd04b">
      <el-menu-item index="scene">
        <span>三维场景模型</span>
      </el-menu-item>
      <el-menu-item index="database">
        <span>实测数据库</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
// 侧边栏逻辑可根据需要扩展
</script>

<style scoped>
.sidebar-menu {
  width: 60px;
  height: 100vh;
  background: #1a2736;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 2px 0 8px rgba(0,0,0,0.08);
}
.el-menu {
  border-right: none;
  width: 100%;
}
</style>
