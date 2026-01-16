<template>
  <div class="page flex-col">
    <!-- 顶部导航栏 -->
    <div class="box_1 flex-row">
      <span class="text_1">{{ currentTime }}</span>
      <img
        class="image_1"
        src="/images/FigmaDDSSlicePNG440bb7ea1afcaab61d12ba4fe112e4af.png"
        alt="Logo"
      />
      <span class="text_2">数字化大坝监测可视化系统</span>
      <img
        class="image_2"
        src="/images/FigmaDDSSlicePNG8b836aa3a170ae20cb243c3ae0b91c60.png"
        alt="Decoration"
      />
      <img
        class="image_3"
        src="/images/FigmaDDSSlicePNGe5d552036766d5152518ed0eb573dfa2.png"
        alt="Avatar"
      />
      <div class="text-wrapper_1 flex-col" @click="handleAuthClick">
        <span class="text_3">{{ isLoggedIn ? '退出' : '登录/注册' }}</span>
      </div>
    </div>

    <div class="box_2 flex-col">
      <!-- Cesium三维场景 - 占据整个区域，显示大坝模型 -->
      <main class="screen-main screen-cesium-full">
        <CesiumScene ref="cesiumSceneRef" />
      </main>
      
      <!-- 左侧菜单 - 浮在 Cesium 场景之上 -->
      <div class="section_2 flex-col justify-between">
        <div class="text-wrapper_2 flex-col">
          <span class="paragraph_1">数字监控大屏</span>
        </div>
        <div class="text-wrapper_3 flex-col" @click="$emit('switch-to-database')">
          <span class="paragraph_2">数据库界面</span>
        </div>
      </div>
      
      <!-- 左侧概述框 -->
      <div class="section_3 flex-col">
        <!-- 大坝基础信息 -->
        <div class="section-header">
          <div class="text-wrapper_7 flex-row"><span class="text_7">{{ damInfo.name || '加载中...' }}</span></div>
          <div class="text-wrapper_8 flex-row"><span class="text_8">概述：</span></div>
        </div>

        <div class="overview-content">
          <div v-if="damInfo.id" class="overview-item">
            <span class="overview-label">工程等级：</span>
            <span class="overview-value">{{ damInfo.level || '-' }}</span>
          </div>
          <div v-if="damInfo.completion_time" class="overview-item">
            <span class="overview-label">建成时间：</span>
            <span class="overview-value">{{ damInfo.completion_time }}</span>
          </div>
          <div v-if="damInfo.create_time" class="overview-item">
            <span class="overview-label">录入时间：</span>
            <span class="overview-value">{{ formatDateTime(damInfo.create_time) }}</span>
          </div>
        </div>

        <!-- 仪器运行状态总览 -->
        <div class="monitoring-status" :key="`status-${normalCount}-${warningCount}-${alarmCount}`">
          <div class="status-title">
            仪器运行状态
            <span v-if="totalPointsCount > 0" class="status-total">（共 {{ totalPointsCount }} 个仪器）</span>
          </div>
          <div class="status-content">
            <div class="status-item normal">
              <div class="status-icon">✅</div>
              <div class="status-info">
                <div class="status-label">正常运行</div>
                <div class="status-count" :key="`normal-${normalCount}`" v-text="normalCount"></div>
              </div>
            </div>
            <div class="status-item warning">
              <div class="status-icon">⏸️</div>
              <div class="status-info">
                <div class="status-label">停用</div>
                <div class="status-count" :key="`warning-${warningCount}`" v-text="warningCount"></div>
              </div>
            </div>
            <div class="status-item alarm">
              <div class="status-icon">🔴</div>
              <div class="status-info">
                <div class="status-label">设备故障</div>
                <div class="status-count" :key="`alarm-${alarmCount}`" v-text="alarmCount"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 底部控制按钮 -->
      <div class="section_4 flex-row">
        <div class="text-wrapper_4 flex-col" @click="showEffectPanel = !showEffectPanel">
          <span class="text_4">效果设置</span>
        </div>
        <div class="text-wrapper_5 flex-col" @click="showViewPanel = !showViewPanel">
          <span class="text_5">视角切换</span>
        </div>
        <div class="box_3 flex-col" @click="showPopupImage = !showPopupImage">
          <img
            class="label_1"
            referrerpolicy="no-referrer"
            src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG3b086c1c5325ce6f851400e353ee79e6.png"
            alt="Label"
          />
        </div>
        <div class="text-wrapper_6 flex-col" @click="showSensorPanel = !showSensorPanel">
          <span class="text_6">测点切换</span>
        </div>
      </div>
      <!-- 底部控制面板（效果设置、视角切换、测点切换） -->
      <div class="bottom-panels">
        <!-- 效果设置面板 -->
        <div class="bottom-panel effect-panel-container" v-if="showEffectPanel">
          <EffectPanel @effect-changed="handleEffectChange" />
        </div>
        <!-- 视角切换面板 -->
        <div class="bottom-panel view-panel-container" v-if="showViewPanel">
          <ViewSwitchPanel @switch-view="handleViewSwitch" />
        </div>
        <!-- 测点切换面板 -->
        <div class="bottom-panel sensor-panel-container" v-show="showSensorPanel">
          <SensorPanel ref="sensorPanelRef" @select-sensor="handleSensorSelect" />
        </div>
      </div>
      <!-- 弹出的图片 -->
      <transition name="bounce-popup">
        <div class="popup-image-container" v-if="showPopupImage" @click="showPopupImage = false">
          <img
            class="popup-image"
            referrerpolicy="no-referrer"
            src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG390c4140626680b672c1c1eef8944edf.png"
            alt="Popup"
          />
        </div>
      </transition>
      
      <!-- 右下角兔子组件 -->
      <div class="rabbit-container" :class="{ active: showVisualizationPanel }" @click="toggleVisualizationPanel">
        <div class="text-wrapper_9 flex-col">
          <span class="text_9">可视化</span>
        </div>
        <img
          class="rabbit-image"
          referrerpolicy="no-referrer"
          src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG802be2cc7db6899de194f09e5d4e2669.png"
          alt="Rabbit"
        />
      </div>
      
      <!-- 可视化栏目（从下方滑出，跟随兔子） -->
      <transition name="slide-up-smooth">
        <div class="visualization-panel" v-if="showVisualizationPanel">
          <div class="visualization-content">
            <!-- 水位折线图（双折线水位监测） -->
            <div class="chart-container">
              <UpstreamDownstreamWaterLevelChart title="水位监测" />
            </div>
            <!-- 倒垂线-上下游位移（趋势折线图） -->
            <div class="chart-container">
              <DownstreamDisplacementTrendChart title="倒垂线-上下游位移" />
            </div>
            <!-- 倒垂线-左右岸位移（堆叠柱状图） -->
            <div class="chart-container">
              <LeftRightDisplacementComparisonChart title="倒垂线-左右岸位移" />
            </div>
            <!-- 静力水准沉降（面积图） -->
            <div class="chart-container">
              <StaticLevelSettlementAreaChart title="静力水准沉降" />
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 传感器详情弹窗 -->
      <SensorDetailModal 
        v-if="showSensorModal"
        :sensor-name="selectedSensorName"
        :status="selectedSensorStatus"
        :point-id="selectedPointId"
        @close="showSensorModal = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch, getCurrentInstance } from 'vue'
import CesiumScene from '@/components/CesiumScene.vue'
import ViewSwitchPanel from '@/components/ViewSwitchPanel.vue'
import EffectPanel from '@/components/EffectPanel.vue'
import SensorPanel from '@/components/SensorPanel.vue'
import SensorDetailModal from '@/components/SensorDetailModal.vue'
import UpstreamDownstreamWaterLevelChart from '@/components/charts/UpstreamDownstreamWaterLevelChart.vue'
import DownstreamDisplacementTrendChart from '@/components/charts/DownstreamDisplacementTrendChart.vue'
import LeftRightDisplacementComparisonChart from '@/components/charts/LeftRightDisplacementComparisonChart.vue'
import StaticLevelSettlementAreaChart from '@/components/charts/StaticLevelSettlementAreaChart.vue'
import { getStructures, getPoints } from '@/api/waterStructures'
import { getMonitorDataList } from '@/api/monitoring'
import { isAuthenticated } from '@/utils/auth'
import { useAuth } from '@/store/auth'
import { getSensorCode } from '@/utils/sensorMapping'




const emit = defineEmits(['show-login', 'switch-to-database', 'logout'])

// 获取登录状态
const { isLoggedIn } = useAuth()

const currentTime = ref('2026/1/15 10:00:00 星期四')
const showViewPanel = ref(false)
const showEffectPanel = ref(false)
const showSensorPanel = ref(false)
const sensorPanelRef = ref(null)
const showPopupImage = ref(false)
const showVisualizationPanel = ref(false)
const showSensorModal = ref(false)
const selectedSensorName = ref('传感器EX1')
const selectedSensorStatus = ref('normal')
const selectedPointId = ref(null) // 添加 pointId 用于加载测点详情
const cesiumSceneRef = ref(null)

// 大坝信息
const damInfo = ref({})

// 仪器运行状态数据
const warningCount = ref(0) // 停用数量
const alarmCount = ref(0) // 故障数量
const normalCount = ref(0) // 正常运行数量
const totalPointsCount = ref(0) // 总仪器数

let timeInterval = null
let monitoringInterval = null

// 加载大坝信息
async function loadDamInfo() {
  try {
    const response = await getStructures({ page_size: 1 })
    if (response.data.results && response.data.results.length > 0) {
      damInfo.value = response.data.results[0]
      
      // TODO: 可以根据大坝的cesium坐标调整Cesium场景的视角
      // if (damInfo.value.cesium_center_x && damInfo.value.cesium_center_y && cesiumSceneRef.value) {
      //   // 调整相机位置
      // }
    }
  } catch (error) {
    console.error('加载大坝信息失败:', error)
  }
}

// 格式化日期时间
function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return '-'
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// EX1-10 测点设备名称列表（前端定义的映射，与 SensorPanel 和 CesiumScene 保持一致）
const EX_SENSOR_NAMES = ['EX1', 'EX2', 'EX3', 'EX4', 'EX5', 'EX6', 'EX7', 'EX8', 'EX9', 'EX10']

// 加载监测统计数据（直接使用 SensorPanel 的 sensors 数据，确保完全一致）
async function loadMonitoringStatistics() {
  try {
    // 直接使用 SensorPanel 的 sensors 数据，确保与测点切换面板完全一致
    const sensors = sensorPanelRef.value?.sensors || []
    
    if (sensors.length === 0) {
      // 如果 SensorPanel 还没加载，等待一下再重试
      setTimeout(() => {
        loadMonitoringStatistics()
      }, 500)
      return
    }
    
    // 统计设备运行状态（device_status）
    let running = 0
    let stopped = 0
    let faulty = 0

    sensors.forEach(sensor => {
      // 使用 SensorPanel 中保存的 deviceStatus
      const deviceStatus = sensor.deviceStatus || 'running'
      
      if (deviceStatus === 'running') {
        running++
      } else if (deviceStatus === 'stopped') {
        stopped++
      } else if (deviceStatus === 'faulty') {
        faulty++
      } else {
        // 未知状态，默认当作 running
        running++
      }
    })

    // 固定为10个仪器
    totalPointsCount.value = EX_SENSOR_NAMES.length
    
    normalCount.value = running
    warningCount.value = stopped
    alarmCount.value = faulty
    
    // 延迟检查 DOM 中的值
    setTimeout(() => {
      const normalCountEl = document.querySelector('.status-item.normal .status-count')
      const warningCountEl = document.querySelector('.status-item.warning .status-count')
      const alarmCountEl = document.querySelector('.status-item.alarm .status-count')
      const normalElText = normalCountEl?.textContent?.trim()
      const warningElText = warningCountEl?.textContent?.trim()
      const alarmElText = alarmCountEl?.textContent?.trim()
      
      // 如果不匹配，手动更新 DOM（临时方案）
      if (normalElText !== String(normalCount.value) && normalCountEl) {
        normalCountEl.textContent = normalCount.value
      }
      if (warningElText !== String(warningCount.value) && warningCountEl) {
        warningCountEl.textContent = warningCount.value
      }
      if (alarmElText !== String(alarmCount.value) && alarmCountEl) {
        alarmCountEl.textContent = alarmCount.value
      }
    }, 200)
    
    return // 直接返回，不再执行后面的代码
  } catch (error) {
    console.error('从 SensorPanel 加载数据失败，使用备用方案:', error)
    // 如果出错，继续使用原来的方法
  }
  
  // 备用方案：直接从 API 获取数据（如果 SensorPanel 不可用）
  try {
    // 获取所有监测点
    const response = await getPoints({
      page_size: 1000
    })

    if (response.data.results && response.data.results.length > 0) {
      const allPoints = response.data.results
      
      // 使用与 SensorPanel 完全相同的映射逻辑
      // 建立映射：EX1对应EX1-2-位移mm，EX2对应EX1-3-位移mm，以此类推
      const pointMap = new Map()
      
      allPoints.forEach(point => {
        // 使用多种可能的字段名来获取测点名称（与 SensorPanel 一致）
        const sensorName = point.point_code || 
                         point.name || 
                         point.device_info?.device_name ||
                         point.device_name

        if (sensorName) {
          const code = sensorName.toUpperCase().trim()
          // 直接使用测点名称作为key
          pointMap.set(code, point)

          // 建立EX映射：EX1-2-位移mm → EX1, EX1-3-位移mm → EX2, EX1-4-位移mm → EX3, ...
          // 这与 SensorPanel 中的映射规则完全一致
          const match = code.match(/^EX1-(\d+)-位移MM$/i)
          if (match) {
            const deviceNum = parseInt(match[1])
            // EX1-2-位移mm → EX1, EX1-3-位移mm → EX2, EX1-4-位移mm → EX3, ...
            // deviceNum从2开始，对应EX1；deviceNum=3对应EX2，所以公式是：EX(deviceNum-1)
            if (deviceNum >= 2 && deviceNum <= 11) {
              const exName = `EX${deviceNum - 1}`
              if (EX_SENSOR_NAMES.includes(exName) && !pointMap.has(exName)) {
                pointMap.set(exName, point)
              }
            }
          }
        }
      })
      
      // 只使用前端定义的10个测点
      const exPoints = EX_SENSOR_NAMES.map(name => pointMap.get(name)).filter(Boolean)
      
      // 先重置所有值，确保响应式更新
      totalPointsCount.value = EX_SENSOR_NAMES.length // 固定为10个
      normalCount.value = 0
      warningCount.value = 0
      alarmCount.value = 0

      // 统计设备运行状态（device_status）
      let running = 0
      let stopped = 0
      let faulty = 0

      exPoints.forEach(point => {
        // 统计设备运行状态（device_status）
        const deviceStatus = point.device_info?.device_status || 'running'
        
        if (deviceStatus === 'running') {
          running++
        } else if (deviceStatus === 'stopped') {
          stopped++
        } else if (deviceStatus === 'faulty') {
          faulty++
        } else {
          // 未知状态，默认当作 running
          running++
        }
      })

      // 对于没有找到后端数据的测点，默认状态为 running
      const foundCount = exPoints.length
      if (foundCount < EX_SENSOR_NAMES.length) {
        running += (EX_SENSOR_NAMES.length - foundCount)
      }

      // 正常运行 = running, 停用 = stopped, 故障 = faulty
      normalCount.value = running
      warningCount.value = stopped
      alarmCount.value = faulty
      
      // 延迟检查 DOM 中的值
      setTimeout(() => {
        const normalCountEl = document.querySelector('.status-item.normal .status-count')
        const warningCountEl = document.querySelector('.status-item.warning .status-count')
        const alarmCountEl = document.querySelector('.status-item.alarm .status-count')
        const normalElText = normalCountEl?.textContent?.trim()
        const warningElText = warningCountEl?.textContent?.trim()
        const alarmElText = alarmCountEl?.textContent?.trim()
        
        // 如果不匹配，尝试手动更新 DOM（临时方案）
        if (normalElText !== String(normalCount.value) && normalCountEl) {
          normalCountEl.textContent = normalCount.value
        }
        if (warningElText !== String(warningCount.value) && warningCountEl) {
          warningCountEl.textContent = warningCount.value
        }
        if (alarmElText !== String(alarmCount.value) && alarmCountEl) {
          alarmCountEl.textContent = alarmCount.value
        }
      }, 200)
    } else {
      // 即使没有后端数据，也显示10个仪器（默认都是正常运行）
      totalPointsCount.value = EX_SENSOR_NAMES.length
      normalCount.value = EX_SENSOR_NAMES.length
      warningCount.value = 0
      alarmCount.value = 0
    }
  } catch (error) {
    console.error('加载仪器运行状态统计失败:', error)
    // 即使出错，也显示10个仪器（默认都是正常运行）
    totalPointsCount.value = EX_SENSOR_NAMES.length
    normalCount.value = EX_SENSOR_NAMES.length
    warningCount.value = 0
    alarmCount.value = 0
  }
}

onMounted(() => {
  // 检查登录状态，如果未登录则触发登录事件
  if (!isAuthenticated()) {
    emit('show-login')
    return
  }
  
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadDamInfo()

  // 加载监测统计数据
  loadMonitoringStatistics()

  // 设置定时刷新监测数据（每10秒刷新一次，确保状态更新及时显示）
  monitoringInterval = setInterval(() => {
    loadMonitoringStatistics()
  }, 10000) // 从30秒改为10秒
  
  // 设置Cesium点击回调的函数
  function setupSensorClickCallback() {
    if (cesiumSceneRef.value && cesiumSceneRef.value.setOnSensorClick) {
      cesiumSceneRef.value.setOnSensorClick((sensorName) => {
        // 处理测点点击，显示弹窗
        handleSensorClickFromCesium(sensorName)
      })
      return true
    } else {
      return false
    }
  }
  
  // 立即尝试设置回调（不依赖sensors）
  nextTick(() => {
    // 延迟一点确保CesiumScene已经初始化
    setTimeout(() => {
      setupSensorClickCallback()
    }, 1000)
  })
  
  // 监听SensorPanel的sensors数组和cesiumSceneRef的变化
  watch([() => sensorPanelRef.value?.sensors, () => cesiumSceneRef.value], () => {
    // 当sensors加载完成或cesiumSceneRef可用时，确保回调已设置
    if (sensorPanelRef.value?.sensors && sensorPanelRef.value.sensors.length > 0) {
      setupSensorClickCallback()
    } else if (cesiumSceneRef.value) {
      setupSensorClickCallback()
    }
  }, { immediate: true })
  
  // 初始化坐标拾取工具（供手动配置使用）
  nextTick(() => {
    setTimeout(() => {
      initCoordinatePicker()
    }, 3000) // 等待3秒，确保模型加载完成
  })
})

/**
 * 初始化坐标拾取工具
 * 在控制台提供坐标拾取功能，方便手动配置坝段边界
 */
function initCoordinatePicker() {
  if (typeof window === 'undefined') return
}

let coordinatePickerHandler = null
let currentSegmentCoordinates = []

/**
 * 开始坐标拾取
 */
function startCoordinatePicker() {
  if (!cesiumSceneRef.value) {
    return null
  }

  // 检查 Cesium 是否可用
  const Cesium = window.Cesium
  if (!Cesium) {
    return null
  }

  // 通过 getViewer 方法获取 viewer
  const viewer = cesiumSceneRef.value.getViewer?.()
  
  if (!viewer) {
    return null
  }

  // 如果已有活动的拾取器，先停止
  if (coordinatePickerHandler) {
    coordinatePickerHandler.destroy()
  }
  if (window.coordinatePickerHandler) {
    window.coordinatePickerHandler.destroy()
  }

  // 开始坐标拾取
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  let coordinates = []
  let segmentIndex = 0
  
  handler.setInputAction((click) => {
    const position = viewer.scene.pickPosition(click.position)
    if (Cesium.defined(position)) {
      const cartographic = Cesium.Cartographic.fromCartesian(position)
      const lon = Cesium.Math.toDegrees(cartographic.longitude)
      const lat = Cesium.Math.toDegrees(cartographic.latitude)
      const height = cartographic.height
      
      coordinates.push([lon, lat, height])
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
  
  // 按 Enter 键完成当前坝段，开始下一个
  const keyHandler = (e) => {
    if (e.key === 'Enter' && coordinates.length >= 3) {
      coordinates = []
      segmentIndex++
    }
  }
  
  document.addEventListener('keydown', keyHandler)
  
  // 保存到全局变量
  coordinatePickerHandler = handler
  window.coordinatePickerHandler = handler
  window.coordinatePickerKeyHandler = keyHandler
  
  return handler
}

/**
 * 停止坐标拾取
 */
function stopCoordinatePicker() {
  // 移除键盘事件监听
  if (window.coordinatePickerKeyHandler) {
    document.removeEventListener('keydown', window.coordinatePickerKeyHandler)
    window.coordinatePickerKeyHandler = null
  }
  
  // 销毁事件处理器
  if (coordinatePickerHandler) {
    coordinatePickerHandler.destroy()
    coordinatePickerHandler = null
  } else if (window.coordinatePickerHandler) {
    window.coordinatePickerHandler.destroy()
    window.coordinatePickerHandler = null
  }
}

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  if (monitoringInterval) {
    clearInterval(monitoringInterval)
  }
})

function updateTime() {
  const now = new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  const weekday = weekdays[now.getDay()]
  currentTime.value = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}${weekday}`
}

function handleViewSwitch(viewName) {
  // 通过 ref 调用 CesiumScene 的视角切换方法
  if (cesiumSceneRef.value && cesiumSceneRef.value.switchView) {
    cesiumSceneRef.value.switchView(viewName)
  }
}

// 处理从 UI 面板选择的测点
function handleSensorSelect(sensor) {

  
  // 获取测点名称（用于飞行定位）
  const sensorName = sensor.name
  
  // 获取测点的数据库ID（用于显示详情）
  // 优先级：pointId > rawData.id > detail.id > id（如果id是数字）
  let pointId = sensor.pointId || sensor.rawData?.id || sensor.detail?.id || sensor.id
  
  // 如果 pointId 是字符串且不是纯数字，尝试转换为数字或设为 null
  if (typeof pointId === 'string') {
    if (/^\d+$/.test(pointId)) {
      // 纯数字字符串，转换为数字
      pointId = parseInt(pointId, 10)
    } else {
      // 不是数字字符串（可能是测点名称），设为 null
      pointId = null
    }
  }
  
  // 如果 pointId 不是数字，设为 null
  if (typeof pointId !== 'number' || isNaN(pointId)) {
    pointId = null
  }
  
  // 设置选中的测点信息
  selectedSensorName.value = sensorName
  selectedSensorStatus.value = sensor.status
  selectedPointId.value = pointId
  
  // 飞行到测点位置
  if (cesiumSceneRef.value && cesiumSceneRef.value.flyToSensor) {
    cesiumSceneRef.value.flyToSensor(sensorName, () => {
      // 飞行完成后显示弹窗
      showSensorModal.value = true
    })
  } else {
    // 如果无法飞行，直接显示弹窗
    showSensorModal.value = true
  }
}

// 处理从 Cesium 场景中点击的测点
function handleSensorClickFromCesium(sensorName) {
  // 从SensorPanel获取测点信息
  const sensors = sensorPanelRef.value?.sensors
  
  if (sensors && Array.isArray(sensors) && sensors.length > 0) {
    // 直接通过 name 或 id 匹配（因为传感器数据结构中没有 code 字段）
    let sensorData = sensors.find(s => s.name === sensorName || s.id === sensorName)
    
    // 如果没找到，尝试通过 pointCode 匹配（EX1 -> EX1-2-位移mm）
    if (!sensorData) {
      const pointCode = getSensorCode(sensorName)
      if (pointCode) {
        // 在 rawData 中查找 point_code 匹配的
        sensorData = sensors.find(s => {
          const code = s.rawData?.point_code || s.rawData?.name
          return code && code.toUpperCase().includes(pointCode.toUpperCase())
        })
      }
    }
    
    if (sensorData) {
      // 调用handleSensorSelect函数，复用现有逻辑
      handleSensorSelect(sensorData)
      return
    }
  } else {
    // 如果 SensorPanel 还未加载完成，等待一下再重试
    if (!sensorPanelRef.value?.sensors) {
      setTimeout(() => {
        handleSensorClickFromCesium(sensorName)
      }, 500)
      return
    }
  }

  // 如果找不到测点数据，设置默认值并显示弹窗（但不会显示详细信息）
  selectedSensorName.value = sensorName
  selectedSensorStatus.value = 'normal'
  selectedPointId.value = null
  showSensorModal.value = true
}

function handleEffectChange(effect) {
  // 通过 ref 调用 CesiumScene 的效果控制方法
  if (cesiumSceneRef.value && cesiumSceneRef.value.setEffect) {
    cesiumSceneRef.value.setEffect(effect.key, effect.enabled)
  }
}

function toggleVisualizationPanel() {
  showVisualizationPanel.value = !showVisualizationPanel.value
}

// 处理认证按钮点击
function handleAuthClick() {
  if (isLoggedIn.value) {
    // 已登录，触发退出登录
    emit('logout')
  } else {
    // 未登录，触发登录
    emit('show-login')
  }
}

/**
 * 手动触发蒙版热区生成（供调试使用）
 * 可以在浏览器控制台调用：window.setupMask()
 */
function setupMask() {
  setupMaskAutoGeneration()
}


// 将函数暴露到全局，方便在控制台调用
if (typeof window !== 'undefined') {
  window.cesiumSceneRef = () => cesiumSceneRef.value
  window.startCoordinatePicker = startCoordinatePicker
  window.stopCoordinatePicker = stopCoordinatePicker
  
  // 手动配置蒙版的快捷方法
  window.setupMask = (segmentBounds, debugMode = true) => {
    if (!cesiumSceneRef.value) {
      return
    }
    
    if (!segmentBounds || !Array.isArray(segmentBounds) || segmentBounds.length === 0) {
      return
    }
    
    cesiumSceneRef.value.setMaskConfig({
      enabled: true,
      debugMode: debugMode,
      totalSegments: segmentBounds.length,
      segmentBounds: segmentBounds
    })
  }
}
</script>

<style scoped src="./SceneView.css"></style>
