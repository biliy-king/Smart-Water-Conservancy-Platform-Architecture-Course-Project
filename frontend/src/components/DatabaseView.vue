<template>
  <div class="database-view">
    <!-- 顶部标题栏 -->
    <header class="db-header">
      <div class="header-left">
        <div class="db-title">数据库管理</div>
      </div>
    </header>

    <div class="db-body">
      <!-- 左侧菜单 -->
      <aside class="db-sidebar">
        <div class="menu-item" :class="{ active: false }" @click="$emit('switch-to-scene')">
          <div class="menu-rectangle"></div>
          <div class="menu-text">数<br/>字<br/>监<br/>控<br/>大<br/>屏</div>
        </div>
        <div class="menu-item active">
          <div class="menu-rectangle"></div>
          <div class="menu-text">数<br/>据<br/>库<br/>界<br/>面</div>
        </div>
      </aside>

      <!-- 主要内容区域 -->
      <main class="db-main">
        <!-- 操作栏 -->
        <div class="db-toolbar">
          <div class="toolbar-left">
            <div class="toolbar-item">
              <span class="toolbar-text">-删除数据</span>
            </div>
            <div class="toolbar-item">
              <span class="toolbar-text">+增加数据</span>
            </div>
            <div class="toolbar-item">
              <span class="toolbar-label">选择测点</span>
            </div>
          </div>
        </div>

        <!-- 筛选区域 -->
        <div class="db-filters">
          <div class="filter-group">
            <span class="filter-label">选择时间段:</span>
            <input v-model="startDate" type="date" class="date-input" />
            <span class="date-separator">至</span>
            <input v-model="endDate" type="date" class="date-input" />
            <button class="confirm-btn" @click="applyDateFilter">确定</button>
          </div>
          <div class="filter-group">
            <span class="sort-label">升序</span>
            <div class="radio-group">
              <input type="radio" id="asc" v-model="sortOrder" value="asc" />
              <label for="asc"></label>
            </div>
            <span class="sort-label">降序</span>
            <div class="radio-group">
              <input type="radio" id="desc" v-model="sortOrder" value="desc" />
              <label for="desc"></label>
            </div>
            <button class="export-btn" @click="exportData">导出</button>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="db-table-container">
          <table class="db-table">
            <thead>
              <tr>
                <th>测点</th>
                <th>时间</th>
                <th>数值</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedData" :key="item.id">
                <td>{{ item.name }}</td>
                <td>{{ item.date }}</td>
                <td>{{ item.value }}</td>
                <td>
                  <span :class="['status-badge', item.status]">{{ item.statusText }}</span>
                </td>
                <td>
                  <button class="action-btn" @click="editItem(item)">编辑</button>
                  <button class="action-btn delete" @click="deleteItem(item)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控制 -->
        <div class="db-pagination">
          <div class="pagination-left">
            <span class="page-size-label">每页记录条数</span>
            <select v-model="pageSize" class="page-size-select">
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
          <div class="pagination-center">
            <button class="page-btn" @click="goToFirstPage" :disabled="currentPage === 1">&lt;首页</button>
            <button 
              v-for="page in visiblePages" 
              :key="page" 
              class="page-number"
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
            <button class="page-btn" @click="goToLastPage" :disabled="currentPage === totalPages">末页&gt;</button>
          </div>
          <div class="pagination-right">
            <span class="page-info">共{{ totalItems }}条数据，共{{ totalPages }}页</span>
          </div>
        </div>

        <!-- 测点选择面板 -->
        <div class="sensor-select-panel" v-if="showSensorSelect">
          <div class="panel-header">选择测点</div>
          <div class="sensor-options">
            <div 
              v-for="sensor in sensors" 
              :key="sensor.id"
              class="sensor-option"
              :class="{ selected: selectedSensors.includes(sensor.id) }"
              @click="toggleSensor(sensor.id)"
            >
              {{ sensor.name }}
            </div>
          </div>
          <div class="collection-method">
            <div class="method-label">采集方式</div>
            <div class="method-options">
              <label class="method-option">
                <input type="radio" v-model="collectionMethod" value="auto" />
                <span>自动</span>
              </label>
              <label class="method-option">
                <input type="radio" v-model="collectionMethod" value="manual" />
                <span>人工</span>
              </label>
              <label class="method-option">
                <input type="radio" v-model="collectionMethod" value="other" />
                <span>其它</span>
              </label>
            </div>
          </div>
          <button class="confirm-btn" @click="applySensorFilter">确定</button>
        </div>
      </main>

      <!-- 右侧滚动条区域 -->
      <aside class="db-scrollbar">
        <div class="scrollbar-track">
          <div class="scrollbar-thumb" :style="{ height: scrollbarHeight + '%', top: scrollbarTop + '%' }"></div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const emit = defineEmits(['switch-to-scene'])

// 数据
const tableData = ref([
  { id: 1, name: '传感器1', date: '2026-01-15 10:00:00', value: 0.21, status: 'normal', statusText: '正常' },
  { id: 2, name: '传感器2', date: '2026-01-15 10:05:00', value: 0.18, status: 'normal', statusText: '正常' },
  { id: 3, name: '传感器3', date: '2026-01-15 10:10:00', value: 0.25, status: 'abnormal', statusText: '异常' },
  { id: 4, name: '传感器4', date: '2026-01-15 10:15:00', value: 0.19, status: 'normal', statusText: '正常' },
  { id: 5, name: '传感器5', date: '2026-01-15 10:20:00', value: 0.22, status: 'normal', statusText: '正常' },
  // 添加更多数据用于测试分页
  ...Array.from({ length: 95 }, (_, i) => ({
    id: i + 6,
    name: `传感器${(i % 5) + 1}`,
    date: `2026-01-15 ${String(10 + Math.floor(i / 5)).padStart(2, '0')}:${String((i % 5) * 5).padStart(2, '0')}:00`,
    value: (0.15 + Math.random() * 0.1).toFixed(2),
    status: Math.random() > 0.8 ? 'abnormal' : 'normal',
    statusText: Math.random() > 0.8 ? '异常' : '正常'
  }))
])

// 筛选和排序
const startDate = ref('')
const endDate = ref('')
const sortOrder = ref('asc')
const filteredData = ref([...tableData.value])

// 测点选择
const showSensorSelect = ref(false)
const sensors = ref([
  { id: 1, name: '传感器1' },
  { id: 2, name: '传感器2' },
  { id: 3, name: '传感器3' },
  { id: 4, name: '传感器4' },
  { id: 5, name: '传感器5' }
])
const selectedSensors = ref([1, 2, 3, 4, 5])
const collectionMethod = ref('auto')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

const totalItems = computed(() => filteredData.value.length)
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 10
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  start = Math.max(1, end - maxVisible + 1)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// 滚动条
const scrollbarHeight = ref(20)
const scrollbarTop = ref(0)

// 方法
function applyDateFilter() {
  // 应用日期筛选逻辑
  console.log('应用日期筛选:', startDate.value, endDate.value)
}

function applySensorFilter() {
  showSensorSelect.value = false
  // 应用测点筛选逻辑
  console.log('应用测点筛选:', selectedSensors.value, collectionMethod.value)
}

function toggleSensor(sensorId) {
  const index = selectedSensors.value.indexOf(sensorId)
  if (index > -1) {
    selectedSensors.value.splice(index, 1)
  } else {
    selectedSensors.value.push(sensorId)
  }
}

function exportData() {
  console.log('导出数据')
  // 实现导出逻辑
}

function editItem(item) {
  console.log('编辑:', item)
}

function deleteItem(item) {
  const index = tableData.value.findIndex(d => d.id === item.id)
  if (index > -1) {
    tableData.value.splice(index, 1)
    applyDateFilter()
  }
}

function goToPage(page) {
  currentPage.value = page
}

function goToFirstPage() {
  currentPage.value = 1
}

function goToLastPage() {
  currentPage.value = totalPages.value
}

onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.database-view {
  width: 100vw;
  height: 100vh;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
}

.db-header {
  height: 89px;
  background: #DEEFFB;
  display: flex;
  align-items: center;
  padding: 0 48px;
}

.header-left {
  display: flex;
  align-items: center;
}

.db-title {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
}

.db-body {
  flex: 1;
  display: flex;
  position: relative;
  height: calc(100vh - 89px);
}

.db-sidebar {
  width: 48px;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  gap: 0;
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 10;
}

.menu-item {
  position: relative;
  width: 48px;
  height: 271px;
  cursor: pointer;
}

.menu-item.active .menu-rectangle {
  background: #D9D9D9;
}

.menu-item:not(.active) .menu-rectangle {
  background: #DEEFFB;
}

.menu-rectangle {
  width: 48px;
  height: 271px;
  transition: background 0.3s;
}

.menu-text {
  position: absolute;
  left: 8px;
  top: 27px;
  width: 32px;
  height: 234px;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
  writing-mode: vertical-lr;
  text-align: center;
}

.db-main {
  flex: 1;
  margin-left: 48px;
  padding: 20px;
  overflow-y: auto;
  background: #FFFFFF;
}

.db-toolbar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  gap: 20px;
  align-items: center;
}

.toolbar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.toolbar-text {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
}

.toolbar-label {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
}

.db-filters {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #000000;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid #0F1419;
  border-radius: 4px;
  font-size: 16px;
}

.date-separator {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #000000;
}

.confirm-btn {
  padding: 8px 16px;
  background: #DEEFFB;
  border: 1px solid #000000;
  border-radius: 5px;
  font-family: 'Inter', sans-serif;
  font-weight: 300;
  font-size: 32px;
  color: #000000;
  cursor: pointer;
}

.confirm-btn:hover {
  background: #D9D9D9;
}

.sort-label {
  font-family: 'Inter', sans-serif;
  font-weight: 300;
  font-size: 32px;
  color: #000000;
}

.radio-group {
  display: flex;
  align-items: center;
}

.radio-group input[type="radio"] {
  width: 18px;
  height: 18px;
  margin: 0 8px;
}

.export-btn {
  padding: 8px 16px;
  background: #DEEFFB;
  border: 1px solid #000000;
  border-radius: 15px;
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 40px;
  color: #000000;
  cursor: pointer;
  margin-left: 20px;
}

.export-btn:hover {
  background: #D9D9D9;
}

.db-table-container {
  margin-bottom: 20px;
  border: 1px solid #0F1419;
  border-radius: 4px;
  overflow: hidden;
}

.db-table {
  width: 100%;
  border-collapse: collapse;
  background: #FFFFFF;
}

.db-table thead {
  background: #DEEFFB;
}

.db-table th {
  padding: 12px;
  text-align: left;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 18px;
  color: #000000;
  border-bottom: 1px solid #0F1419;
}

.db-table td {
  padding: 12px;
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 16px;
  color: #000000;
  border-bottom: 1px solid #D9D9D9;
}

.db-table tbody tr:hover {
  background: #F5F5F5;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.status-badge.normal {
  background: #6DEC61;
  color: #000000;
}

.status-badge.abnormal {
  background: #FF5227;
  color: #FFFFFF;
}

.action-btn {
  padding: 4px 8px;
  margin-right: 8px;
  background: #DEEFFB;
  border: 1px solid #000000;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.action-btn:hover {
  background: #D9D9D9;
}

.action-btn.delete {
  background: #FFE5E5;
}

.action-btn.delete:hover {
  background: #FFCCCC;
}

.db-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid #0F1419;
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-size-label {
  font-family: 'Inter', sans-serif;
  font-weight: 300;
  font-size: 32px;
  color: #000000;
}

.page-size-select {
  padding: 8px 12px;
  border: 1px solid #626262;
  border-radius: 4px;
  font-size: 16px;
}

.pagination-center {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-btn {
  padding: 8px 12px;
  background: #FFFFFF;
  border: 1px solid #626262;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-weight: 300;
  font-size: 32px;
  color: #000000;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #F5F5F5;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  border: 1px solid #626262;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-weight: 300;
  font-size: 36px;
  color: #000000;
  cursor: pointer;
}

.page-number:hover {
  background: #F5F5F5;
}

.page-number.active {
  background: #DEEFFB;
  border-color: #000000;
}

.pagination-right {
  font-family: 'Inter', sans-serif;
  font-weight: 300;
  font-size: 36px;
  color: #000000;
}

.sensor-select-panel {
  position: absolute;
  top: 100px;
  right: 20px;
  width: 494px;
  background: #FFFFFF;
  border: 1px solid #0F1419;
  border-radius: 8px;
  padding: 20px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.panel-header {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
  margin-bottom: 20px;
}

.sensor-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.sensor-option {
  padding: 12px;
  background: #FEFBFB;
  border: 1px solid #0F1419;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.sensor-option:hover {
  background: #F5F5F5;
}

.sensor-option.selected {
  background: #DEEFFB;
  border-color: #000000;
}

.collection-method {
  margin-bottom: 20px;
}

.method-label {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 36px;
  color: #000000;
  margin-bottom: 12px;
}

.method-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.method-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.method-option input[type="radio"] {
  width: 24px;
  height: 24px;
}

.method-option span {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #000000;
}

.db-scrollbar {
  width: 29px;
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  background: #FFFFFF;
  border-left: 1px solid #0F1419;
}

.scrollbar-track {
  position: relative;
  width: 100%;
  height: 100%;
}

.scrollbar-thumb {
  position: absolute;
  width: 22px;
  background: #D9D9D9;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s;
}

.scrollbar-thumb:hover {
  background: #B0B0B0;
}
</style>
