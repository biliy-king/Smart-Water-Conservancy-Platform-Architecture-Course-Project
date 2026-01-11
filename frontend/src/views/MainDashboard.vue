<template>
  <div class="dashboard-root">
    <TopBar />
    <div class="dashboard-body">
      <SidebarMenu />
      <div class="left-panel">
        <EffectPanel />
        <ViewSwitchPanel />
      </div>
      <div class="scene-panel">
        <CesiumScene />
      </div>
      <DataPanel />
    </div>
  </div>
</template>

<script setup>
import TopBar from '@/components/TopBar.vue'
import SidebarMenu from '@/components/SidebarMenu.vue'
import EffectPanel from '@/components/EffectPanel.vue'
import ViewSwitchPanel from '@/components/ViewSwitchPanel.vue'
import CesiumScene from '@/components/CesiumScene.vue'
import DataPanel from '@/components/DataPanel.vue'
</script>

<style scoped>
.dashboard-root {
  height: 100vh;
  width: 100vw;
  background: #0a1a2a;
  overflow: hidden;
}
.dashboard-body {
  display: flex;
  height: calc(100vh - 50px);
}
.left-panel {
  width: 180px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: #223044;
  padding: 0 0 0 8px;
}
.scene-panel {
  flex: 1;
  position: relative;
  min-width: 0;
  background: #000;
}
</style>
