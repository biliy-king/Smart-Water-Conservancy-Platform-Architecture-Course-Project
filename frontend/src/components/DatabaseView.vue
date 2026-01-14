<template>
  <div class="page flex-col">
    <!-- 顶部浅蓝色条 -->
    <div class="group_1 flex-col"></div>
    
    <div class="group_2 flex-col">
      <!-- 顶部筛选栏 -->
      <div class="box_1 flex-row">
        <!-- 数据类型切换 -->
        <div class="data-type-selector">
          <button 
            v-for="type in dataTypes" 
            :key="type.value"
            :class="['type-btn', { active: currentDataType === type.value }]"
            @click="switchDataType(type.value)"
          >
            {{ type.label }}
          </button>
        </div>
        
        <!-- 监测数据筛选 -->
        <template v-if="currentDataType === 'monitor'">
          <input type="date" class="group_3 flex-col modern-input" v-model="filters.startDate" />
          <span class="text_1">至</span>
          <input type="date" class="group_4 flex-col modern-input" v-model="filters.endDate" />
          <select v-model="filters.pointId" class="group_3 flex-col modern-select" style="width: 200px;">
            <option value="">全部监测点</option>
            <!-- EX系列简化选项：EX1 → EX1-2, EX2 → EX1-3, 以此类推（只显示有数据的） -->
            <option 
              v-for="exName in availableEXPoints" 
              :key="exName" 
              :value="exName"
            >
              {{ exName }} ({{ getEXDeviceName(exName) }})
            </option>
            <!-- 其他测点：显示设备名称（只显示有数据的） -->
            <option 
              v-for="point in pointList.filter(p => !p.point_code.match(/^EX1-\d+-位移mm$/))" 
              :key="point.id" 
              :value="point.id"
            >
              {{ point.device_info?.device_name || point.point_code }}
            </option>
          </select>
          <select v-model="filters.status" class="group_3 flex-col modern-select" style="width: 150px;">
            <option value="">全部状态</option>
            <option value="normal">正常</option>
            <option value="warning">预警</option>
            <option value="alarm">告警</option>
          </select>
        </template>
        
        <!-- 用户信息筛选 -->
        <template v-if="currentDataType === 'user'">
          <input 
            type="text" 
            class="group_3 flex-col modern-input" 
            v-model="filters.username" 
            placeholder="搜索用户名"
            style="width: 200px;"
          />
          <select v-model="filters.role" class="group_3 flex-col modern-select" style="width: 150px;">
            <option value="">全部角色</option>
            <option value="admin">管理员</option>
            <option value="monitor">监测员</option>
            <option value="viewer">查看者</option>
          </select>
        </template>
        
        <div class="group_5 flex-row">
          <div class="block_1 flex-col" :class="{ active: sortOrder === 'asc' }" @click="sortOrder = 'asc'"></div>
          <span class="text_2">升序</span>
          <div class="block_2 flex-col" :class="{ active: sortOrder === 'desc' }" @click="sortOrder = 'desc'"></div>
          <span class="text_3">降序</span>
        </div>
        <div class="text-wrapper_1 flex-col" @click="applyFilters">
          <span class="text_4">确定</span>
        </div>
        <div class="text-wrapper_1 flex-col" @click="addData">
          <span class="text_4">+增加数据</span>
        </div>
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
            <!-- 监测数据表格 -->
            <table v-if="currentDataType === 'monitor'" class="data-table">
              <thead>
                <tr>
                  <th style="width: 50px;">
                    <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
                  </th>
                  <th>监测点</th>
                  <th>监测时间</th>
                  <th>倒垂线-上下</th>
                  <th>倒垂线-左右</th>
                  <th>引张线-上下</th>
                  <th>静力水准-沉降</th>
                  <th>上游水位</th>
                  <th>下游水位</th>
                  <th>状态</th>
                  <th>监测人</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="12" style="text-align: center; padding: 20px;">加载中...</td>
                </tr>
                <tr v-else-if="errorMessage">
                  <td colspan="12" style="text-align: center; padding: 20px; color: #f56c6c;">{{ errorMessage }}</td>
                </tr>
                <tr v-else-if="paginatedData.length === 0">
                  <td colspan="12" style="text-align: center; padding: 20px;">暂无数据</td>
                </tr>
                <tr v-else v-for="item in paginatedData" :key="item.id" :class="{ selected: selectedIds.includes(item.id) }">
                  <td>
                    <input type="checkbox" :value="item.id" v-model="selectedIds" />
                  </td>
                  <td>{{ item.pointName }}</td>
                  <td>{{ item.monitor_time }}</td>
                  <td>{{ item.inverted_plumb_up_down !== null ? item.inverted_plumb_up_down.toFixed(2) : '-' }}</td>
                  <td>{{ item.inverted_plumb_left_right !== null ? item.inverted_plumb_left_right.toFixed(2) : '-' }}</td>
                  <td>{{ item.tension_wire_up_down !== null ? item.tension_wire_up_down.toFixed(2) : '-' }}</td>
                  <td>{{ item.hydrostatic_leveling_settlement !== null ? item.hydrostatic_leveling_settlement.toFixed(2) : '-' }}</td>
                  <td>{{ item.water_level_upstream !== null ? item.water_level_upstream.toFixed(2) : '-' }}</td>
                  <td>{{ item.water_level_downstream !== null ? item.water_level_downstream.toFixed(2) : '-' }}</td>
                  <td>
                    <span :class="['status-badge', getStatusClass(item.status)]">{{ getStatusText(item.status) }}</span>
                  </td>
                  <td>{{ item.monitor_person || '-' }}</td>
                  <td>
                    <button class="action-btn" @click="viewDetail(item)">详情</button>
                    <button class="action-btn" @click="editItem(item)">编辑</button>
                    <button class="action-btn delete" @click="deleteItem(item)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <!-- 用户信息表格 -->
            <table v-else-if="currentDataType === 'user'" class="data-table">
              <thead>
                <tr>
                  <th style="width: 50px;">
                    <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
                  </th>
                  <th>用户名</th>
                  <th>角色</th>
                  <th>电话</th>
                  <th>部门</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="7" style="text-align: center; padding: 20px;">加载中...</td>
                </tr>
                <tr v-else-if="errorMessage">
                  <td colspan="7" style="text-align: center; padding: 20px; color: #f56c6c;">{{ errorMessage }}</td>
                </tr>
                <tr v-else-if="paginatedData.length === 0">
                  <td colspan="7" style="text-align: center; padding: 20px;">暂无数据</td>
                </tr>
                <tr v-else v-for="item in paginatedData" :key="item.id" :class="{ selected: selectedIds.includes(item.id) }">
                  <td>
                    <input type="checkbox" :value="item.id" v-model="selectedIds" />
                  </td>
                  <td>{{ item.username }}</td>
                  <td>{{ getRoleText(item.role) }}</td>
                  <td>{{ item.phone || '-' }}</td>
                  <td>{{ item.department || '-' }}</td>
                  <td>{{ formatDateTime(item.create_time) }}</td>
                  <td>
                    <button class="action-btn" @click="viewDetail(item)">详情</button>
                    <button class="action-btn" @click="editItem(item)">编辑</button>
                    <button class="action-btn delete" @click="deleteItem(item)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
            
          </div>
          
          <!-- 底部分页控件 -->
          <div class="section_2 flex-row">
            <div class="pagination-center">
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
            </div>
            <div class="text-wrapper_15 flex-col" @click="exportData">
              <span class="text_19">导出</span>
            </div>
          </div>
        </div>
        
        <!-- 右侧边栏 -->
        <div class="box_5 flex-col">
          <!-- 图表区域 -->
          <div class="chart-container">
            <div ref="chartRef" class="chart-wrapper"></div>
          </div>
          
          <!-- 右下角图片 -->
          <div class="image-container">
            <img
              class="image_1"
              src="/images/FigmaDDSSlicePNGf41f4dea0dfa8bd566685f1150ea9a25.png"
              alt="Character"
            />
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
    
    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="detailDialogTitle"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentDetailItem" class="detail-content">
        <!-- 监测数据详情 -->
        <template v-if="currentDataType === 'monitor'">
          <div class="detail-row">
            <span class="detail-label">监测点：</span>
            <span class="detail-value">{{ currentDetailItem.pointName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">监测时间：</span>
            <span class="detail-value">{{ currentDetailItem.monitor_time }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">倒垂线-上下：</span>
            <span class="detail-value">{{ currentDetailItem.inverted_plumb_up_down !== null ? currentDetailItem.inverted_plumb_up_down.toFixed(2) + ' mm' : '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">倒垂线-左右：</span>
            <span class="detail-value">{{ currentDetailItem.inverted_plumb_left_right !== null ? currentDetailItem.inverted_plumb_left_right.toFixed(2) + ' mm' : '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">引张线-上下：</span>
            <span class="detail-value">{{ currentDetailItem.tension_wire_up_down !== null ? currentDetailItem.tension_wire_up_down.toFixed(2) + ' mm' : '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">静力水准-沉降：</span>
            <span class="detail-value">{{ currentDetailItem.hydrostatic_leveling_settlement !== null ? currentDetailItem.hydrostatic_leveling_settlement.toFixed(2) + ' mm' : '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">上游水位：</span>
            <span class="detail-value">{{ currentDetailItem.water_level_upstream !== null ? currentDetailItem.water_level_upstream.toFixed(2) + ' m' : '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">下游水位：</span>
            <span class="detail-value">{{ currentDetailItem.water_level_downstream !== null ? currentDetailItem.water_level_downstream.toFixed(2) + ' m' : '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">状态：</span>
            <span :class="['status-badge', getStatusClass(currentDetailItem.status)]">{{ getStatusText(currentDetailItem.status) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">监测人：</span>
            <span class="detail-value">{{ currentDetailItem.monitor_person || '-' }}</span>
          </div>
          <div class="detail-row" v-if="currentDetailItem.remark">
            <span class="detail-label">备注：</span>
            <span class="detail-value">{{ currentDetailItem.remark }}</span>
          </div>
        </template>
        
        <!-- 用户信息详情 -->
        <template v-else-if="currentDataType === 'user'">
          <div class="detail-row">
            <span class="detail-label">用户名：</span>
            <span class="detail-value">{{ currentDetailItem.username }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">角色：</span>
            <span class="detail-value">{{ getRoleText(currentDetailItem.role) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">电话：</span>
            <span class="detail-value">{{ currentDetailItem.phone || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">部门：</span>
            <span class="detail-value">{{ currentDetailItem.department || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">创建时间：</span>
            <span class="detail-value">{{ formatDateTime(currentDetailItem.create_time) }}</span>
          </div>
        </template>
        
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑/新增弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editDialogTitle"
      width="60%"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="150px" :rules="editFormRules" ref="editFormRef">
        <!-- 监测数据表单 -->
        <template v-if="currentDataType === 'monitor'">
          <el-form-item label="监测点" prop="point">
            <el-select v-model="editForm.point" placeholder="请选择监测点" style="width: 100%;" @change="onPointChange">
              <el-option
                v-for="point in pointList"
                :key="point.id"
                :label="point.device_info?.device_name || point.point_code"
                :value="point.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="监测时间" prop="monitor_time">
            <el-date-picker
              v-model="editForm.monitor_time"
              type="datetime"
              placeholder="选择监测时间"
              style="width: 100%;"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
            />
          </el-form-item>
          <!-- 根据设备类型动态显示字段 -->
          <el-form-item 
            v-if="shouldShowField('inverted_plumb_up_down')" 
            label="倒垂线-上下(mm)">
            <el-input-number v-model="editForm.inverted_plumb_up_down" :precision="2" style="width: 100%;" />
          </el-form-item>
          <el-form-item 
            v-if="shouldShowField('inverted_plumb_left_right')" 
            label="倒垂线-左右(mm)">
            <el-input-number v-model="editForm.inverted_plumb_left_right" :precision="2" style="width: 100%;" />
          </el-form-item>
          <el-form-item 
            v-if="shouldShowField('tension_wire_up_down')" 
            label="引张线-上下(mm)">
            <el-input-number v-model="editForm.tension_wire_up_down" :precision="2" style="width: 100%;" />
          </el-form-item>
          <el-form-item 
            v-if="shouldShowField('hydrostatic_leveling_settlement')" 
            label="静力水准-沉降(mm)">
            <el-input-number v-model="editForm.hydrostatic_leveling_settlement" :precision="2" style="width: 100%;" />
          </el-form-item>
          <el-form-item 
            v-if="shouldShowField('water_level_upstream')" 
            label="上游水位(m)">
            <el-input-number v-model="editForm.water_level_upstream" :precision="2" style="width: 100%;" />
          </el-form-item>
          <el-form-item 
            v-if="shouldShowField('water_level_downstream')" 
            label="下游水位(m)">
            <el-input-number v-model="editForm.water_level_downstream" :precision="2" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="监测人">
            <el-input v-model="editForm.monitor_person" placeholder="请输入监测人姓名" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="editForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
          </el-form-item>
        </template>
        
        <!-- 用户信息表单 -->
        <template v-else-if="currentDataType === 'user'">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="editForm.username" placeholder="请输入用户名" :disabled="isEditMode" />
          </el-form-item>
          <el-form-item label="密码" prop="password" v-if="!isEditMode">
            <el-input v-model="editForm.password" type="password" placeholder="请输入密码" />
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="editForm.role" placeholder="请选择角色" style="width: 100%;">
              <el-option label="管理员" value="admin" />
              <el-option label="监测员" value="monitor" />
              <el-option label="查看者" value="viewer" />
            </el-select>
          </el-form-item>
          <el-form-item label="电话">
            <el-input v-model="editForm.phone" placeholder="请输入电话" />
          </el-form-item>
          <el-form-item label="部门">
            <el-input v-model="editForm.department" placeholder="请输入部门" />
          </el-form-item>
        </template>
        
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getMonitorDataList, 
  createMonitorData, 
  updateMonitorData, 
  deleteMonitorData 
} from '@/api/monitoring'
import { 
  getUserProfileList, 
  createUserProfile, 
  updateUserProfile, 
  deleteUserProfile 
} from '@/api/users'
import { register } from '@/api/auth'
import { 
  getPoints,
  getPointsWithData
} from '@/api/waterStructures'
import { isAuthenticated, getCurrentUser } from '@/utils/auth'

const emit = defineEmits(['switch-to-scene'])

// 数据类型
const dataTypes = [
  { label: '监测数据', value: 'monitor' },
  { label: '用户信息', value: 'user' }
]
const currentDataType = ref('monitor')

// 数据
const tableData = ref([])
const loading = ref(false)
const errorMessage = ref('')
const pointList = ref([])

// 后端分页信息
const totalItems = ref(0)
const currentPage = ref(1)
const pageSize = ref(15) // 固定分页大小为15

// 筛选和排序
const filters = ref({
  startDate: '',
  endDate: '',
  pointId: '',
  status: '',
  username: '',
  role: ''
})
const sortOrder = ref('desc')
const collectionMethod = ref('auto')

// 选择
const selectedIds = ref([])
const selectAll = ref(false)

// 弹窗
const detailDialogVisible = ref(false)
const detailDialogTitle = ref('详情')
const currentDetailItem = ref(null)
const editDialogVisible = ref(false)
const editDialogTitle = ref('新增')
const isEditMode = ref(false)
const editForm = ref({})
const editFormRef = ref(null)

// 图表相关
const chartRef = ref(null)
let chartInstance = null

// 表单验证规则
const editFormRules = computed(() => {
  if (currentDataType.value === 'monitor') {
    return {
      point: [{ required: true, message: '请选择监测点', trigger: 'change' }],
      monitor_time: [{ required: true, message: '请选择监测时间', trigger: 'change' }]
    }
  } else if (currentDataType.value === 'user') {
    return {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: isEditMode.value ? [] : [{ required: true, message: '请输入密码', trigger: 'blur' }],
      role: [{ required: true, message: '请选择角色', trigger: 'change' }]
    }
  }
  return {}
})

const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

// 计算有数据的EX测点列表
const availableEXPoints = computed(() => {
  const available = []
  for (let i = 1; i <= 20; i++) {
    const exName = `EX${i}`
    if (hasEXPointData(exName)) {
      available.push(exName)
    }
  }
  return available
})

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

// 获取当前选中监测点的设备类型
const currentPointDeviceType = computed(() => {
  if (!editForm.value.point) return null
  const point = pointList.value.find(p => p.id === editForm.value.point)
  return point?.device_info?.device_type || null
})

// 判断是否应该显示某个字段
function shouldShowField(fieldName) {
  if (!currentPointDeviceType.value) {
    // 如果没有选择监测点，显示所有字段（新增时）
    return true
  }
  
  // 字段与设备类型的映射关系
  const fieldMapping = {
    'inverted_plumb_up_down': 'inverted_plumb_up_down',
    'inverted_plumb_left_right': 'inverted_plumb_left_right',
    'tension_wire_up_down': 'tension_wire_up_down',
    'hydrostatic_leveling_settlement': 'hydrostatic_leveling',
    'water_level_upstream': 'water_level_upstream',
    'water_level_downstream': 'water_level_downstream'
  }
  
  const expectedDeviceType = fieldMapping[fieldName]
  return currentPointDeviceType.value === expectedDeviceType
}

// 监测点选择变化时的处理
function onPointChange(pointId) {
  if (!pointId) return
  
  const point = pointList.value.find(p => p.id === pointId)
  if (!point) return
  
  const deviceType = point.device_info?.device_type
  
  // 根据设备类型清空不相关的字段
  if (deviceType !== 'inverted_plumb_up_down') {
    editForm.value.inverted_plumb_up_down = null
  }
  if (deviceType !== 'inverted_plumb_left_right') {
    editForm.value.inverted_plumb_left_right = null
  }
  if (deviceType !== 'tension_wire_up_down') {
    editForm.value.tension_wire_up_down = null
  }
  if (deviceType !== 'hydrostatic_leveling') {
    editForm.value.hydrostatic_leveling_settlement = null
  }
  if (deviceType !== 'water_level_upstream') {
    editForm.value.water_level_upstream = null
  }
  if (deviceType !== 'water_level_downstream') {
    editForm.value.water_level_downstream = null
  }
}

// 切换数据类型
function switchDataType(type) {
  currentDataType.value = type
  currentPage.value = 1
  selectedIds.value = []
  selectAll.value = false
  // 重置筛选条件
  filters.value = {
    startDate: '',
    endDate: '',
    pointId: '',
    status: '',
    username: '',
    role: ''
  }
  loadData()
}

// 加载监测点列表（只加载有监测数据的测点）
async function loadPointList() {
  try {
    // 只获取有监测数据的测点
    const response = await getPointsWithData()
    pointList.value = response.data.results || response.data || []
    console.log(`加载了 ${pointList.value.length} 个有数据的测点`)
  } catch (error) {
    console.error('加载监测点列表失败:', error)
    // 如果新接口失败，回退到获取所有测点
    try {
      const fallbackResponse = await getPoints()
      pointList.value = fallbackResponse.data.results || fallbackResponse.data || []
    } catch (fallbackError) {
      console.error('回退加载测点列表也失败:', fallbackError)
    }
  }
}

// EX测点映射函数：EX1 → point_code EX1-2-位移mm, EX2 → point_code EX1-3-位移mm, 以此类推
function mapEXPointToPointCode(exName) {
  // 匹配 EX1, EX2, EX3 等格式
  const match = exName.match(/^EX(\d+)$/i)
  if (match) {
    const num = parseInt(match[1])
    // EX1 → EX1-2-位移mm, EX2 → EX1-3-位移mm, EX3 → EX1-4-位移mm, ...
    return `EX1-${num + 1}-位移mm`
  }
  return exName // 如果不匹配，返回原值
}

// 根据简化的EX名称找到对应的测点ID（通过point_code查找）
function findPointIdByEXName(exName) {
  const targetPointCode = mapEXPointToPointCode(exName)
  // 根据point_code查找测点
  const point = pointList.value.find(p => p.point_code === targetPointCode)
  return point ? point.id : null
}

// 获取EX对应的设备名称
function getEXDeviceName(exName) {
  const pointId = findPointIdByEXName(exName)
  if (pointId) {
    const point = pointList.value.find(p => p.id === pointId)
    return point?.device_info?.device_name || mapEXPointToPointCode(exName)
  }
  // 如果找不到，尝试根据设备名称映射
  const match = exName.match(/^EX(\d+)$/i)
  if (match) {
    const num = parseInt(match[1])
    return `EX1-${num + 1}`
  }
  return exName
}

// 检查EX测点是否有数据
function hasEXPointData(exName) {
  const pointId = findPointIdByEXName(exName)
  return pointId !== null && pointList.value.some(p => p.id === pointId)
}

// 加载数据
async function loadData() {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    let response
    
    if (currentDataType.value === 'monitor') {
      // 监测数据
      if (filters.value.startDate) {
        params.start_time = filters.value.startDate + ' 00:00:00'
      }
      if (filters.value.endDate) {
        params.end_time = filters.value.endDate + ' 23:59:59'
      }
      if (filters.value.pointId && filters.value.pointId !== '') {
        // 如果pointId是字符串且匹配EX格式（如"EX1", "EX2"），进行映射
        let pointId = filters.value.pointId
        if (typeof pointId === 'string' && /^EX\d+$/i.test(pointId)) {
          const mappedId = findPointIdByEXName(pointId)
          if (mappedId) {
            pointId = mappedId
            console.log(`映射 ${filters.value.pointId} → point_code ${mapEXPointToPointCode(filters.value.pointId)} (ID: ${mappedId})`)
          } else {
            console.warn(`未找到 ${filters.value.pointId} 对应的测点: point_code ${mapEXPointToPointCode(filters.value.pointId)}`)
            // 如果找不到映射，不传递point参数
            pointId = null
          }
        }
        // 只有当pointId有效时才添加到参数中
        if (pointId && pointId !== '') {
          params.point = pointId
        }
      }
      if (filters.value.status && filters.value.status !== '') {
        params.status = filters.value.status
      }
      
      console.log('筛选参数:', params)
      
      response = await getMonitorDataList(params)
      console.log('API响应:', response.data)
      
      const results = response.data.results || response.data || []
      console.log(`获取到 ${results.length} 条数据`)
      
      tableData.value = results.map(item => ({
        ...item,
        // 使用设备名称作为测点显示名称
        pointName: item.point_info?.device_info?.device_name || item.point_info?.point_code || `监测点${item.point}`
      }))
      totalItems.value = response.data.count || results.length
      
      console.log('筛选后的数据:', tableData.value.length, '条')
    } else if (currentDataType.value === 'user') {
      // 用户信息
      if (filters.value.username) {
        params.search = filters.value.username
      }
      if (filters.value.role) {
        params.role = filters.value.role
      }
      
      response = await getUserProfileList(params)
      const results = response.data.results || response.data || []
      tableData.value = results.map(item => ({
        ...item,
        username: item.user?.username || item.username || '-'
      }))
      totalItems.value = response.data.count || results.length
    }
    
    console.log('加载数据成功，共', totalItems.value, '条')
  } catch (error) {
    console.error('加载数据失败:', error)
    errorMessage.value = error.response?.data?.detail || '加载数据失败，请稍后重试'
    tableData.value = []
  } finally {
    loading.value = false
  }
}

// 工具函数
function getStatusClass(status) {
  const map = {
    normal: 'normal',
    warning: 'warning',
    alarm: 'abnormal'
  }
  return map[status] || 'normal'
}

function getStatusText(status) {
  const map = {
    normal: '正常',
    warning: '预警',
    alarm: '告警'
  }
  return map[status] || '正常'
}

function getRoleText(role) {
  const map = {
    admin: '管理员',
    monitor: '监测员',
    viewer: '查看者'
  }
  return map[role] || role
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').substring(0, 19)
}

// 全选/取消全选
function toggleSelectAll() {
  if (selectAll.value) {
    selectedIds.value = paginatedData.value.map(item => item.id)
  } else {
    selectedIds.value = []
  }
}

// 方法
function applyFilters() {
  currentPage.value = 1
  loadData()
}

function applyCollectionMethod() {
  console.log('应用采集方式:', collectionMethod.value)
  ElMessage.info('采集方式功能待实现')
}

function addData() {
  isEditMode.value = false
  editDialogTitle.value = '新增' + dataTypes.find(t => t.value === currentDataType.value)?.label
  editForm.value = {}
  
  // 根据数据类型初始化表单
  if (currentDataType.value === 'monitor') {
    const currentUser = getCurrentUser()
    editForm.value = {
      point: null,
      monitor_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
      inverted_plumb_up_down: null,
      inverted_plumb_left_right: null,
      tension_wire_up_down: null,
      hydrostatic_leveling_settlement: null,
      water_level_upstream: null,
      water_level_downstream: null,
      monitor_person: currentUser?.username || '',
      remark: ''
    }
  } else if (currentDataType.value === 'user') {
    editForm.value = {
      username: '',
      password: '',
      role: 'viewer',
      phone: '',
      department: ''
    }
  }
  
  editDialogVisible.value = true
}

function editItem(item) {
  isEditMode.value = true
  editDialogTitle.value = '编辑' + dataTypes.find(t => t.value === currentDataType.value)?.label
  
  // 深拷贝数据
  editForm.value = JSON.parse(JSON.stringify(item))
  
  // 处理时间格式
  if (currentDataType.value === 'monitor' && editForm.value.monitor_time) {
    editForm.value.monitor_time = editForm.value.monitor_time.replace(' ', 'T')
  }
  
  // 监测数据：根据监测点的设备类型清空不相关的字段
  if (currentDataType.value === 'monitor' && item.point_info?.device_info?.device_type) {
    const deviceType = item.point_info.device_info.device_type
    // 清空不属于该设备类型的字段
    if (deviceType !== 'inverted_plumb_up_down') {
      editForm.value.inverted_plumb_up_down = null
    }
    if (deviceType !== 'inverted_plumb_left_right') {
      editForm.value.inverted_plumb_left_right = null
    }
    if (deviceType !== 'tension_wire_up_down') {
      editForm.value.tension_wire_up_down = null
    }
    if (deviceType !== 'hydrostatic_leveling') {
      editForm.value.hydrostatic_leveling_settlement = null
    }
    if (deviceType !== 'water_level_upstream') {
      editForm.value.water_level_upstream = null
    }
    if (deviceType !== 'water_level_downstream') {
      editForm.value.water_level_downstream = null
    }
  }
  
  // 用户信息需要特殊处理
  if (currentDataType.value === 'user') {
    editForm.value.username = item.username || item.user?.username
  }
  
  editDialogVisible.value = true
}

async function saveEdit() {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    
    let response
    const data = { ...editForm.value }
    
    if (currentDataType.value === 'monitor') {
      // 根据监测点的设备类型，只保留相关的字段
      const point = pointList.value.find(p => p.id === data.point)
      const deviceType = point?.device_info?.device_type
      
      if (deviceType) {
        // 清空不属于该设备类型的字段
        if (deviceType !== 'inverted_plumb_up_down') {
          data.inverted_plumb_up_down = null
        }
        if (deviceType !== 'inverted_plumb_left_right') {
          data.inverted_plumb_left_right = null
        }
        if (deviceType !== 'tension_wire_up_down') {
          data.tension_wire_up_down = null
        }
        if (deviceType !== 'hydrostatic_leveling') {
          data.hydrostatic_leveling_settlement = null
        }
        if (deviceType !== 'water_level_upstream') {
          data.water_level_upstream = null
        }
        if (deviceType !== 'water_level_downstream') {
          data.water_level_downstream = null
        }
      }
      // 处理时间格式
      if (data.monitor_time) {
        data.monitor_time = data.monitor_time.replace('T', ' ')
      }
      
      if (isEditMode.value) {
        response = await updateMonitorData(data.id, data)
      } else {
        response = await createMonitorData(data)
      }
    } else if (currentDataType.value === 'user') {
      // 用户信息需要先创建User，再创建UserProfile
      if (isEditMode.value) {
        // 更新时，只更新UserProfile，不更新User基础信息
        const profileData = {
          role: data.role,
          phone: data.phone,
          department: data.department
        }
        response = await updateUserProfile(data.id, profileData)
      } else {
        // 新增时，先调用注册接口创建User（会自动创建UserProfile）
        if (!data.password) {
          ElMessage.error('请输入密码')
          return
        }
        const registerResponse = await register(data.username, data.password)
        if (registerResponse.data.success) {
          // 注册成功后会自动创建UserProfile，但需要更新角色等信息
          const userId = registerResponse.data.user.id
          // 查找刚创建的用户档案并更新
          const profileResponse = await getUserProfileList({ user: userId })
          const profiles = profileResponse.data.results || profileResponse.data || []
          if (profiles.length > 0) {
            const profileId = profiles[0].id
            await updateUserProfile(profileId, {
              role: data.role,
              phone: data.phone,
              department: data.department
            })
          }
          response = registerResponse
        } else {
          throw new Error(registerResponse.data.message || '注册失败')
        }
      }
    }
    
    ElMessage.success(isEditMode.value ? '更新成功' : '创建成功')
    editDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('保存失败:', error)
    if (error.response?.data) {
      const detail = error.response.data.detail || error.response.data
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } else {
      ElMessage.error('保存失败，请稍后重试')
    }
  }
}

function viewDetail(item) {
  currentDetailItem.value = item
  detailDialogTitle.value = dataTypes.find(t => t.value === currentDataType.value)?.label + '详情'
  detailDialogVisible.value = true
}

async function deleteItem(item) {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条数据吗？\n${currentDataType.value === 'monitor' ? `测点：${item.pointName}\n时间：${item.monitor_time}` : 
        `用户名：${item.username}`}`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (currentDataType.value === 'monitor') {
      await deleteMonitorData(item.id)
    } else if (currentDataType.value === 'user') {
      await deleteUserProfile(item.id)
    }
    
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败：' + (error.response?.data?.detail || '未知错误'))
    }
  }
}

async function deleteData() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的数据')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条数据吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 批量删除
    for (const id of selectedIds.value) {
      try {
        if (currentDataType.value === 'monitor') {
          await deleteMonitorData(id)
        } else if (currentDataType.value === 'user') {
          await deleteUserProfile(id)
        }
      } catch (error) {
        console.error(`删除ID ${id} 失败:`, error)
      }
    }
    
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    selectAll.value = false
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

function exportData() {
  // 导出数据为CSV
  const headers = []
  const rows = []
  
  if (currentDataType.value === 'monitor') {
    headers.push(['监测点', '监测时间', '倒垂线-上下', '倒垂线-左右', '引张线-上下', '静力水准-沉降', '上游水位', '下游水位', '状态', '监测人'])
    paginatedData.value.forEach(item => {
      rows.push([
        item.pointName,
        item.monitor_time,
        item.inverted_plumb_up_down !== null ? item.inverted_plumb_up_down.toFixed(2) : '-',
        item.inverted_plumb_left_right !== null ? item.inverted_plumb_left_right.toFixed(2) : '-',
        item.tension_wire_up_down !== null ? item.tension_wire_up_down.toFixed(2) : '-',
        item.hydrostatic_leveling_settlement !== null ? item.hydrostatic_leveling_settlement.toFixed(2) : '-',
        item.water_level_upstream !== null ? item.water_level_upstream.toFixed(2) : '-',
        item.water_level_downstream !== null ? item.water_level_downstream.toFixed(2) : '-',
        getStatusText(item.status),
        item.monitor_person || '-'
      ])
    })
  } else if (currentDataType.value === 'user') {
    headers.push(['用户名', '角色', '电话', '部门', '创建时间'])
    paginatedData.value.forEach(item => {
      rows.push([
        item.username,
        getRoleText(item.role),
        item.phone || '-',
        item.department || '-',
        formatDateTime(item.create_time)
      ])
    })
  }
  
  // 生成CSV内容
  const csvContent = [
    headers[0].join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')
  
  // 添加BOM以支持中文
  const BOM = '\uFEFF'
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${dataTypes.find(t => t.value === currentDataType.value)?.label}_${new Date().getTime()}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('导出成功')
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

// 分页大小已固定，不再需要监听变化

// 监听选择变化
watch(selectedIds, (newVal) => {
  selectAll.value = newVal.length === paginatedData.value.length && paginatedData.value.length > 0
})

// 初始化图表
function initChart() {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表数据
function updateChart() {
  if (!chartInstance) return
  
  if (currentDataType.value === 'monitor') {
    // 监测数据图表：显示水位趋势
    const dates = paginatedData.value.map(item => {
      const date = new Date(item.monitor_time)
      return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes()}`
    })
    
    const upstreamData = paginatedData.value.map(item => item.water_level_upstream).filter(v => v !== null && v !== undefined)
    const downstreamData = paginatedData.value.map(item => item.water_level_downstream).filter(v => v !== null && v !== undefined)
    
    // 如果有水位数据，显示水位趋势
    if (upstreamData.length > 0 || downstreamData.length > 0) {
      const option = {
        title: {
          text: '水位监测趋势',
          left: 'center',
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['上游水位', '下游水位'],
          bottom: 0
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '20%'
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: { fontSize: 10, rotate: 45 }
        },
        yAxis: {
          type: 'value',
          name: '水位(m)',
          axisLabel: { fontSize: 10 }
        },
        series: [
          {
            name: '上游水位',
            type: 'line',
            data: paginatedData.value.map(item => item.water_level_upstream),
            smooth: true,
            itemStyle: { color: '#5470c6' }
          },
          {
            name: '下游水位',
            type: 'line',
            data: paginatedData.value.map(item => item.water_level_downstream),
            smooth: true,
            itemStyle: { color: '#91cc75' }
          }
        ]
      }
      chartInstance.setOption(option)
    } else {
      // 如果没有水位数据，显示其他监测数据（位移、沉降等）
      const hasData = paginatedData.value.some(item => 
        item.inverted_plumb_up_down !== null || 
        item.inverted_plumb_left_right !== null ||
        item.tension_wire_up_down !== null ||
        item.hydrostatic_leveling_settlement !== null
      )
      
      if (hasData) {
        const dates = paginatedData.value.map(item => {
          const date = new Date(item.monitor_time)
          return `${date.getMonth() + 1}/${date.getDate()}`
        })
        
        const series = []
        const legendData = []
        
        if (paginatedData.value.some(item => item.inverted_plumb_up_down !== null)) {
          series.push({
            name: '倒垂线-上下',
            type: 'bar',
            data: paginatedData.value.map(item => item.inverted_plumb_up_down)
          })
          legendData.push('倒垂线-上下')
        }
        if (paginatedData.value.some(item => item.inverted_plumb_left_right !== null)) {
          series.push({
            name: '倒垂线-左右',
            type: 'bar',
            data: paginatedData.value.map(item => item.inverted_plumb_left_right)
          })
          legendData.push('倒垂线-左右')
        }
        if (paginatedData.value.some(item => item.tension_wire_up_down !== null)) {
          series.push({
            name: '引张线-上下',
            type: 'bar',
            data: paginatedData.value.map(item => item.tension_wire_up_down)
          })
          legendData.push('引张线-上下')
        }
        if (paginatedData.value.some(item => item.hydrostatic_leveling_settlement !== null)) {
          series.push({
            name: '静力水准-沉降',
            type: 'bar',
            data: paginatedData.value.map(item => item.hydrostatic_leveling_settlement)
          })
          legendData.push('静力水准-沉降')
        }
        
        const option = {
          title: {
            text: '监测数据统计',
            left: 'center',
            textStyle: { fontSize: 14, fontWeight: 'bold' }
          },
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: legendData,
            bottom: 0
          },
          grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '20%'
          },
          xAxis: {
            type: 'category',
            data: dates,
            axisLabel: { fontSize: 10, rotate: 45 }
          },
          yAxis: {
            type: 'value',
            name: '数值(mm)',
            axisLabel: { fontSize: 10 }
          },
          series: series
        }
        chartInstance.setOption(option)
      } else {
        // 没有数据时显示空状态
        chartInstance.setOption({
          title: {
            text: '暂无数据',
            left: 'center',
            top: 'center',
            textStyle: { fontSize: 14, color: '#999' }
          }
        })
      }
    }
  } else if (currentDataType.value === 'user') {
    // 用户数据图表：显示角色分布
    const roleCount = {
      admin: 0,
      monitor: 0,
      viewer: 0
    }
    
    paginatedData.value.forEach(item => {
      if (item.role && roleCount[item.role] !== undefined) {
        roleCount[item.role]++
      }
    })
    
    const option = {
      title: {
        text: '用户角色分布',
        left: 'center',
        textStyle: { fontSize: 14, fontWeight: 'bold' }
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        data: ['管理员', '监测员', '查看者'],
        bottom: 0
      },
      series: [
        {
          type: 'pie',
          radius: '60%',
          center: ['50%', '45%'],
          data: [
            { value: roleCount.admin, name: '管理员' },
            { value: roleCount.monitor, name: '监测员' },
            { value: roleCount.viewer, name: '查看者' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    chartInstance.setOption(option)
  }
}

// 监听数据变化，更新图表
watch([paginatedData, currentDataType], () => {
  nextTick(() => {
    updateChart()
  })
})

// 组件挂载时检查登录状态并加载数据
onMounted(() => {
  if (!isAuthenticated()) {
    console.warn('未登录，无法访问数据库界面')
    emit('switch-to-scene')
    return
  }
  
  loadPointList()
  loadData()
  
  // 初始化图表
  nextTick(() => {
    initChart()
  })
})
</script>

<style scoped lang="css" src="./DatabaseView.css"></style>

<style scoped>
.data-type-selector {
  display: flex;
  gap: 10px;
  margin-right: 20px;
}

.type-btn {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 1);
  border: 1px solid rgba(200, 200, 200, 1);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.type-btn:hover {
  background: rgba(240, 248, 255, 1);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.type-btn.active {
  background: linear-gradient(135deg, rgba(222, 239, 251, 1) 0%, rgba(200, 220, 240, 1) 100%);
  border-color: rgba(180, 200, 220, 1);
  font-weight: 600;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.type-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.data-table tbody tr.selected {
  background: rgba(240, 248, 255, 1);
}

.status-badge.warning {
  background: #FFA500;
  color: #000000;
}

.detail-content {
  padding: 20px;
}

.detail-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.detail-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.detail-row {
  display: flex;
  margin-bottom: 15px;
  font-size: 14px;
}

.detail-label {
  width: 200px;
  font-weight: 500;
  color: #666;
}

.detail-value {
  flex: 1;
  color: #000;
}
</style>
