<template>
  <div class="page flex-col">
    <!-- 顶部浅蓝色条 -->
    <div class="group_1 flex-col"></div>
    
    <div class="group_2 flex-col">
      <!-- 顶部筛选栏 -->
      <div class="box_1 flex-row">
        <input type="date" class="group_3 flex-col" v-model="startDate" />
        <span class="text_1">至</span>
        <input type="date" class="group_4 flex-col" v-model="endDate" />
        <div class="group_5 flex-row">
          <div class="block_1 flex-col" :class="{ active: sortOrder === 'asc' }" @click="sortOrder = 'asc'"></div>
          <span class="text_2">升序</span>
          <div class="block_2 flex-col" :class="{ active: sortOrder === 'desc' }" @click="sortOrder = 'desc'"></div>
          <span class="text_3">降序</span>
        </div>
        <div class="text-wrapper_1 flex-col" @click="applyFilters">
          <span class="text_4">确定</span>
        </div>
        <span class="text_5">选择时间段:</span>
        <input type="date" class="group_6 flex-col" v-model="timeRange" />
      </div>
      
      <!-- 主体内容区域 -->
      <div class="box_2 flex-row justify-between">
        <!-- 左侧菜单 -->
        <div class="box_3 flex-col justify-between">
          <div class="text-wrapper_2 flex-col" @click="$emit('switch-to-scene')">
            <span class="paragraph_1">数字监控大屏</span>
          </div>
          <div class="text-wrapper_3 flex-col">
            <span class="paragraph_2">数据库界面</span>
          </div>
        </div>
        
        <!-- 中间数据表格区域 -->
        <div class="box_4 flex-col justify-between">
          <!-- 数据表格 -->
          <div class="section_1 flex-col">
            <table class="data-table">
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
                <tr v-if="loading">
                  <td colspan="5" style="text-align: center; padding: 20px;">加载中...</td>
                </tr>
                <tr v-else-if="errorMessage">
                  <td colspan="5" style="text-align: center; padding: 20px; color: #f56c6c;">{{ errorMessage }}</td>
                </tr>
                <tr v-else-if="paginatedData.length === 0">
                  <td colspan="5" style="text-align: center; padding: 20px;">暂无数据</td>
                </tr>
                <tr v-else v-for="item in paginatedData" :key="item.id">
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
          
          <!-- 底部分页控件 -->
          <div class="section_2 flex-row">
            <span class="text_6">每页记录条数</span>
            <select v-model="pageSize" class="group_7 flex-col">
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
            <div class="text-wrapper_4 flex-col" @click="goToFirstPage">
              <span class="text_7">&lt;首页</span>
            </div>
            <div 
              v-for="page in visiblePages" 
              :key="page"
              class="text-wrapper-page flex-col"
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              <span class="text-page">{{ page }}</span>
            </div>
            <div class="text-wrapper_18 flex-col" @click="goToLastPage">
              <span class="text_28">末页&gt;</span>
            </div>
            <span class="text_18">共{{ totalItems }}条数据，共{{ totalPages }}页</span>
            <div class="text-wrapper_15 flex-col" @click="exportData">
              <span class="text_19">导出</span>
            </div>
          </div>
        </div>
        
        <!-- 右侧边栏 -->
        <div class="box_5 flex-col justify-end">
          <div class="block_3 flex-row justify-between">
            <div class="text-wrapper_16 flex-col justify-between">
              <span class="text_20">选择测点</span>
              <span class="text_21" @click="addData">+增加数据</span>
              <span class="text_22" @click="deleteData">-删除数据</span>
            </div>
            <!-- 滚动条区域 -->
            <div class="section_3 flex-row">
              <div class="block_4 flex-col">
                <div class="box_6 flex-col"></div>
              </div>
              <div class="block_5 flex-col">
                <div class="group_8 flex-col"></div>
              </div>
            </div>
          </div>
          
          <!-- 滚动条指示器 -->
          <div class="block_6 flex-row">
            <div class="block_7 flex-col"></div>
            <div class="block_8 flex-col"></div>
            <div class="block_9 flex-col"></div>
          </div>
          
          <div class="block_10 flex-col">
            <div class="box_7 flex-col"></div>
          </div>
          <div class="block_11 flex-col"></div>
          
          <!-- 采集方式选择 -->
          <div class="block_12 flex-row justify-between">
            <div class="group_9 flex-col">
              <span class="text_23">采集方式</span>
              <div class="box_8 flex-row justify-between" @click="collectionMethod = 'auto'">
                <div class="box_9 flex-col" :class="{ active: collectionMethod === 'auto' }"></div>
                <span class="text_24">自动</span>
              </div>
              <div class="box_10 flex-row justify-between" @click="collectionMethod = 'manual'">
                <div class="box_11 flex-col" :class="{ active: collectionMethod === 'manual' }"></div>
                <span class="text_25">人工</span>
              </div>
              <div class="box_12 flex-row justify-between" @click="collectionMethod = 'other'">
                <div class="box_13 flex-col" :class="{ active: collectionMethod === 'other' }"></div>
                <span class="text_26">其它</span>
              </div>
              <div class="text-wrapper_17 flex-col" @click="applyCollectionMethod">
                <span class="text_27">确定</span>
              </div>
            </div>
            <img
              class="image_1"
              src="/images/FigmaDDSSlicePNGf41f4dea0dfa8bd566685f1150ea9a25.png"
              alt="Character"
            />
          </div>
          
          <div class="block_13 flex-row">
            <div class="box_14 flex-col">
              <div class="group_10 flex-col"></div>
            </div>
            <div class="box_15 flex-col"></div>
          </div>
          <div class="block_14 flex-col">
            <div class="group_11 flex-col"></div>
            <div class="group_12 flex-col">
              <div class="box_16 flex-col"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 装饰图片 -->
      <img
        class="image_2"
        src="/images/FigmaDDSSlicePNG1f4b2902883b8d2d3f02893fa0ddb898.png"
        alt="Decoration"
      />
      <img
        class="image_3"
        src="/images/FigmaDDSSlicePNGaaaadd2dc756d0715946a78b360166a8.png"
        alt="Decoration"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getMonitorDataList } from '@/api/monitoring'
import { isAuthenticated } from '@/utils/auth'

const emit = defineEmits(['switch-to-scene'])

// 数据
const tableData = ref([])
const loading = ref(false)
const errorMessage = ref('')

// 后端分页信息
const totalItems = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选和排序
const startDate = ref('')
const endDate = ref('')
const timeRange = ref('')
const sortOrder = ref('asc')
const collectionMethod = ref('auto')

// 将后端数据转换为前端格式
function transformDataItem(apiItem) {
  // 获取监测点名称
  const pointName = apiItem.point_info?.point_code || `监测点${apiItem.point}`
  
  // 获取监测值（根据设备类型选择对应的字段）
  let value = null
  if (apiItem.water_level_upstream !== null) value = apiItem.water_level_upstream
  else if (apiItem.water_level_downstream !== null) value = apiItem.water_level_downstream
  else if (apiItem.inverted_plumb_up_down !== null) value = apiItem.inverted_plumb_up_down
  else if (apiItem.inverted_plumb_left_right !== null) value = apiItem.inverted_plumb_left_right
  else if (apiItem.tension_wire_up_down !== null) value = apiItem.tension_wire_up_down
  else if (apiItem.hydrostatic_leveling_settlement !== null) value = apiItem.hydrostatic_leveling_settlement
  
  // 状态映射
  let status = 'normal'
  let statusText = '正常'
  if (apiItem.status === 'warning') {
    status = 'warning'
    statusText = '预警'
  } else if (apiItem.status === 'alarm') {
    status = 'abnormal'
    statusText = '告警'
  }
  
  // 格式化时间
  const dateStr = apiItem.monitor_time || ''
  const formattedDate = dateStr.replace('T', ' ').substring(0, 19)
  
  return {
    id: apiItem.id,
    name: pointName,
    date: formattedDate,
    value: value !== null ? value.toFixed(2) : '-',
    status: status,
    statusText: statusText,
    rawData: apiItem // 保存原始数据，供编辑/删除使用
  }
}

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

const paginatedData = computed(() => tableData.value)

// 加载数据
async function loadData() {
  loading.value = true
  errorMessage.value = ''
  
  try {
    // 构建查询参数
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 添加时间筛选
    if (startDate.value) {
      params.start_time = startDate.value + ' 00:00:00'
    }
    if (endDate.value) {
      params.end_time = endDate.value + ' 23:59:59'
    }
    
    // 添加排序（后端默认按时间倒序，升序需要调整）
    // 注意：如果后端不支持排序参数，可以在前端处理
    
    const response = await getMonitorDataList(params)
    
    // 转换数据格式
    tableData.value = response.data.results.map(item => transformDataItem(item))
    
    // 更新总数
    totalItems.value = response.data.count
    
    console.log('加载数据成功，共', totalItems.value, '条')
  } catch (error) {
    console.error('加载数据失败:', error)
    errorMessage.value = error.response?.data?.detail || '加载数据失败，请稍后重试'
    tableData.value = []
  } finally {
    loading.value = false
  }
}

// 方法
function applyFilters() {
  currentPage.value = 1
  loadData()
}

function applyCollectionMethod() {
  console.log('应用采集方式:', collectionMethod.value)
  // TODO: 实现采集方式筛选
}

function addData() {
  console.log('增加数据')
  // TODO: 实现增加数据功能
  alert('增加数据功能待实现，请联系管理员')
}

function deleteData() {
  console.log('删除数据')
  // TODO: 实现批量删除功能
  alert('删除数据功能待实现，请联系管理员')
}

function exportData() {
  console.log('导出数据')
  // TODO: 实现导出功能
  alert('导出功能待实现，请联系管理员')
}

function editItem(item) {
  console.log('编辑:', item)
  // TODO: 实现编辑功能
  alert('编辑功能待实现，请联系管理员')
}

async function deleteItem(item) {
  if (!confirm(`确定要删除这条数据吗？\n测点：${item.name}\n时间：${item.date}`)) {
    return
  }
  
  try {
    // TODO: 调用删除接口
    // await deleteMonitorData(item.id)
    alert('删除功能待实现，请联系管理员')
    // 删除成功后重新加载数据
    // loadData()
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败：' + (error.response?.data?.detail || '未知错误'))
  }
}

function goToPage(page) {
  currentPage.value = page
  loadData()
}

function goToFirstPage() {
  currentPage.value = 1
  loadData()
}

function goToLastPage() {
  currentPage.value = totalPages.value
  loadData()
}

// 监听分页大小变化
watch(pageSize, () => {
  currentPage.value = 1
  loadData()
})

// 组件挂载时检查登录状态并加载数据
onMounted(() => {
  // 检查登录状态，如果未登录则跳转到场景视图（会触发App.vue的登录检查）
  if (!isAuthenticated()) {
    console.warn('未登录，无法访问数据库界面')
    emit('switch-to-scene')
    return
  }
  
  loadData()
})
</script>

<style scoped lang="css" src="./DatabaseView.css"></style>
