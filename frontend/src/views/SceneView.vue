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

        <!-- 监测状态总览 -->
        <div class="monitoring-status">
          <div class="status-title">当前监测状态</div>
          <div class="status-content">
            <div class="status-item warning">
              <div class="status-icon">⚠️</div>
              <div class="status-info">
                <div class="status-label">预警</div>
                <div class="status-count">{{ warningCount }}</div>
              </div>
            </div>
            <div class="status-item alarm">
              <div class="status-icon">🚨</div>
              <div class="status-info">
                <div class="status-label">告警</div>
                <div class="status-count">{{ alarmCount }}</div>
              </div>
            </div>
            <div class="status-item normal">
              <div class="status-icon">✅</div>
              <div class="status-info">
                <div class="status-label">正常</div>
                <div class="status-count">{{ normalCount }}</div>
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
            <!-- 水位折线图 -->
            <div class="chart-container">
              <WaterLevelChart />
            </div>
            <!-- 倒垂线-上下游位移 -->
            <div class="chart-container">
              <MaxMinChart 
                title="倒垂线-上下游位移" 
                field-name="inverted_plumb_up_down"
                unit="mm"
              />
            </div>
            <!-- 倒垂线-左右岸位移 -->
            <div class="chart-container">
              <MaxMinChart 
                title="倒垂线-左右岸位移" 
                field-name="inverted_plumb_left_right"
                unit="mm"
              />
            </div>
            <!-- 静力水准沉降 -->
            <div class="chart-container">
              <MaxMinChart 
                title="静力水准沉降" 
                field-name="hydrostatic_leveling_settlement"
                unit="mm"
              />
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
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import CesiumScene from '@/components/CesiumScene.vue'
import ViewSwitchPanel from '@/components/ViewSwitchPanel.vue'
import EffectPanel from '@/components/EffectPanel.vue'
import SensorPanel from '@/components/SensorPanel.vue'
import SensorDetailModal from '@/components/SensorDetailModal.vue'
import WaterLevelChart from '@/components/charts/WaterLevelChart_new.vue'
import MaxMinChart from '@/components/charts/MaxMinChart.vue'
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

// 监测状态数据
const warningCount = ref(0)
const alarmCount = ref(0)
const normalCount = ref(0)

let timeInterval = null
let monitoringInterval = null

// 加载大坝信息
async function loadDamInfo() {
  try {
    const response = await getStructures({ page_size: 1 })
    if (response.data.results && response.data.results.length > 0) {
      damInfo.value = response.data.results[0]
      console.log('加载大坝信息成功:', damInfo.value)
      
      // TODO: 可以根据大坝的cesium坐标调整Cesium场景的视角
      // if (damInfo.value.cesium_center_x && damInfo.value.cesium_center_y && cesiumSceneRef.value) {
      //   // 调整相机位置
      // }
    } else {
      console.warn('没有找到大坝信息')
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

// 加载监测统计数据（从数据库读取监测点状态）
async function loadMonitoringStatistics() {
  try {
    // 获取所有监测点
    const response = await getPoints({
      page_size: 1000
    })

    if (response.data.results && response.data.results.length > 0) {
      const points = response.data.results

      // 统计各状态数量
      let warning = 0
      let alarm = 0
      let normal = 0

      points.forEach(point => {
        if (point.current_status === 'warning') {
          warning++
        } else if (point.current_status === 'alarm') {
          alarm++
        } else if (point.current_status === 'normal') {
          normal++
        }
      })

      warningCount.value = warning
      alarmCount.value = alarm
      normalCount.value = normal

      console.log('监测点状态统计加载成功:', { warning, alarm, normal })
    } else {
      console.warn('没有找到监测点数据')
      // 使用模拟数据
      warningCount.value = 2
      alarmCount.value = 1
      normalCount.value = 15
    }
  } catch (error) {
    console.error('加载监测点状态统计失败:', error)
    // 如果API调用失败，使用模拟数据
    warningCount.value = 2
    alarmCount.value = 1
    normalCount.value = 15
  }
}

onMounted(() => {
  // 检查登录状态，如果未登录则触发登录事件
  if (!isAuthenticated()) {
    console.warn('未登录，无法访问大屏')
    emit('show-login')
    return
  }
  
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadDamInfo()

  // 加载监测统计数据
  loadMonitoringStatistics()

  // 设置定时刷新监测数据（每30秒刷新一次）
  monitoringInterval = setInterval(() => {
    loadMonitoringStatistics()
  }, 30000)
  
  // 监听SensorPanel的sensors数组，当它不为空时，设置Cesium点击回调
  watch(() => sensorPanelRef.value?.sensors, (sensors) => {
    if (sensors && sensors.length > 0 && cesiumSceneRef.value && cesiumSceneRef.value.setOnSensorClick) {
      cesiumSceneRef.value.setOnSensorClick((sensorName) => {
        console.log('Cesium 场景中点击测点:', sensorName)
        // 处理测点点击，显示弹窗
        handleSensorClickFromCesium(sensorName)
      })
      console.log('✅ 测点点击回调已设置')
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
  
  console.log('═══════════════════════════════════════════════════════')
  console.log('📍 坐标拾取工具已就绪')
  console.log('═══════════════════════════════════════════════════════')
  console.log('')
  console.log('📖 使用方法：')
  console.log('   1. 调用 window.startCoordinatePicker() 开始拾取')
  console.log('   2. 点击模型上的点，会在控制台输出坐标')
  console.log('   3. 点击4个点形成一个矩形（或更多点形成不规则多边形）')
  console.log('   4. 复制输出的坐标数组，用于配置坝段边界')
  console.log('   5. 调用 window.stopCoordinatePicker() 停止拾取')
  console.log('')
  console.log('💡 提示：')
  console.log('   - 可以画不规则多边形（至少3个顶点）')
  console.log('   - 每个坝段需要定义一个多边形边界')
  console.log('   - 坐标格式：[经度, 纬度, 高度(米)]')
  console.log('')
  console.log('═══════════════════════════════════════════════════════')
}

let coordinatePickerHandler = null
let currentSegmentCoordinates = []

/**
 * 开始坐标拾取
 */
function startCoordinatePicker() {
  if (!cesiumSceneRef.value) {
    console.error('❌ CesiumScene 组件未加载')
    return null
  }

  // 检查 Cesium 是否可用
  const Cesium = window.Cesium
  if (!Cesium) {
    console.error('❌ Cesium 未加载，请等待页面完全加载后再试')
    console.log('💡 提示：请刷新页面，或等待几秒后重试')
    return null
  }

  // 通过 getViewer 方法获取 viewer
  const viewer = cesiumSceneRef.value.getViewer?.()
  
  if (!viewer) {
    console.error('❌ 无法获取 viewer，请确保页面已加载且模型已初始化')
    console.log('💡 提示：请等待页面完全加载后再试，或刷新页面')
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
      console.log(`📍 坝段 ${segmentIndex} - 已记录坐标 ${coordinates.length}: [${lon.toFixed(6)}, ${lat.toFixed(6)}, ${height.toFixed(2)}]`)
      
      // 每收集完一个坝段的坐标，输出
      if (coordinates.length >= 3) {
        console.log(`\n✅ 坝段 ${segmentIndex} 的坐标数组（至少3个点，可以继续点击添加更多点）：`)
        console.log(JSON.stringify(coordinates, null, 2))
        console.log('\n💡 提示：继续点击可以添加更多点，或按 Enter 键完成当前坝段')
      }
    } else {
      console.warn('⚠️ 未拾取到坐标，请点击模型表面')
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
  
  // 按 Enter 键完成当前坝段，开始下一个
  const keyHandler = (e) => {
    if (e.key === 'Enter' && coordinates.length >= 3) {
      console.log(`\n🎯 坝段 ${segmentIndex} 完成！坐标数组：`)
      console.log(JSON.stringify(coordinates, null, 2))
      console.log(`\n继续点击模型为坝段 ${segmentIndex + 1} 拾取坐标...`)
      coordinates = []
      segmentIndex++
    }
  }
  
  document.addEventListener('keydown', keyHandler)
  
  // 保存到全局变量
  coordinatePickerHandler = handler
  window.coordinatePickerHandler = handler
  window.coordinatePickerKeyHandler = keyHandler
  
  console.log('✅ 坐标拾取器已启动')
  console.log('📝 点击模型上的点来记录坐标')
  console.log('⌨️  按 Enter 键完成当前坝段，开始下一个坝段')
  console.log('🛑 调用 window.stopCoordinatePicker() 停止拾取')
  
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
    console.log('✅ 坐标拾取器已停止')
  } else if (window.coordinatePickerHandler) {
    window.coordinatePickerHandler.destroy()
    window.coordinatePickerHandler = null
    console.log('✅ 坐标拾取器已停止')
  } else {
    console.warn('⚠️ 没有活动的坐标拾取器')
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
  
  console.log('测点选择:', sensorName, '→ pointId:', pointId)
  
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
  console.log('Cesium点击测点:', sensorName)

  // 从SensorPanel获取测点信息
  if (sensorPanelRef.value && sensorPanelRef.value.sensors) {
    const sensors = sensorPanelRef.value.sensors
    // 优先用 code 匹配
    const pointCode = getSensorCode(sensorName)
    let sensorData = sensors.find(s => s.code === pointCode)
    // 如果没找到，再用 name 匹配
    if (!sensorData) {
      sensorData = sensors.find(s => s.name === sensorName)
    }
    if (sensorData) {
      console.log('Cesium点击测点:', sensorName, '→ 找到测点数据:', sensorData)
      // 调用handleSensorSelect函数，复用现有逻辑
      handleSensorSelect(sensorData)
      return
    } else {
      console.warn('Cesium点击未找到测点:', sensorName)
    }
  } else {
    console.warn('sensorPanelRef未初始化')
  }

  // 如果找不到测点数据，设置默认值并显示弹窗
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
      console.error('❌ CesiumScene 组件未加载')
      return
    }
    
    if (!segmentBounds || !Array.isArray(segmentBounds) || segmentBounds.length === 0) {
      console.error('❌ 请提供 segmentBounds 数组')
      console.log('格式示例：')
      console.log(`
const segmentBounds = [
  // 坝段 0
  [[111.15, 30.80, 50], [111.16, 30.80, 50], [111.16, 30.79, 50], [111.15, 30.79, 50]],
  // 坝段 1
  [[111.16, 30.80, 50], [111.17, 30.80, 50], [111.17, 30.79, 50], [111.16, 30.79, 50]],
  // ... 继续定义其他9个坝段
];
      `)
      return
    }
    
    cesiumSceneRef.value.setMaskConfig({
      enabled: true,
      debugMode: debugMode,
      totalSegments: segmentBounds.length,
      segmentBounds: segmentBounds
    })
    
    console.log(`✅ 已配置 ${segmentBounds.length} 个坝段的蒙版热区`)
    if (debugMode) {
      console.log('💡 调试模式已开启，热区显示为红色。配置完成后可设置 debugMode: false')
    }
  }
}
</script>

<style scoped src="./SceneView.css"></style>
