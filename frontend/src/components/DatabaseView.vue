<template>
  <div class="db-view-root screen-bg">
    <header class="db-header screen-header">
      <div class="screen-title">数据库管理</div>
    </header>
    <div class="db-body screen-body">
      <aside class="db-sidebar screen-side screen-side-left">
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">数据分类</div>
          <el-tree :data="treeData" :props="treeProps" default-expand-all />
        </el-card>
      </aside>
      <main class="db-main screen-main">
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">数据表格</div>
          <el-table :data="tableData" style="width:100%">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="value" label="测值" width="80" />
            <el-table-column prop="date" label="日期" width="120" />
          </el-table>
        </el-card>
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">数据图表</div>
          <div style="height:180px;">数据库图表区</div>
        </el-card>
      </main>
      <aside class="db-filter screen-side screen-side-right">
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">筛选条件</div>
          <div>筛选条件区</div>
        </el-card>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const treeData = ref([
  { label: '水库', children: [ { label: '监测点1' }, { label: '监测点2' } ] },
  { label: '大坝', children: [ { label: '监测点A' }, { label: '监测点B' } ] }
])
const treeProps = { children: 'children', label: 'label' }
const tableData = ref([
  { id: 1, name: '监测点1', value: 0.21, date: '2025-01-15' },
  { id: 2, name: '监测点2', value: 0.18, date: '2025-01-15' }
])
</script>

<style scoped>
/* 引入主屏幕科技感样式，复用 screen-bg、screen-header、screen-title、screen-side、screen-card 等类 */
</style>
