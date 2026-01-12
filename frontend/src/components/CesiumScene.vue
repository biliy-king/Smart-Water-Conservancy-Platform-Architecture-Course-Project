<template>
  <div id="cesiumContainer"></div>
    <!-- 在这里添加按钮组 -->
  <div class="view-controls">
    <button @click="switchView('panoramaView')">全景图</button>
    <button @click="switchView('frontendView')">正视图</button>
    <button @click="switchView('reservoirView')">水库视角</button>
    <button @click="switchView('earthView')">地球视角</button>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import * as Cesium from 'cesium' // 导入 Cesium
import 'cesium/Build/Cesium/Widgets/widgets.css'

let viewer = null
let tileset = null

// 视角配置对象（扩展：支持动画时长duration与可选roll）
// 注：保持原有heading/pitch/range不变，新增字段可选调优
const viewConfigs = {
  // 全景图（俯视）
  panoramaView: {
  heading: 30,        // 旋转方向：0是正北，90是正东
  pitch: -90,        // 俯视角度：0是平视，-90是垂直向下看（上帝视角）
  range: 7000,       // 距离目标多远：数值越大离得越远
  duration: 1.5,     // 动画时间：几秒钟飞过去
  roll: 0            // 画面倾斜：0是正的，一般不动它
},
  // 正视图（斜俯看）
  frontendView: { heading: -75, pitch: -30, range:3000, duration: 1.5, roll: 0 },
  // 水库视角（从另一侧斜俯）
  reservoirView: { heading: 120, pitch: -20, range: 3000, duration: 1.5, roll: 0 },
  // 地球视角（拉远一些）
  earthView: { heading: 30, pitch: -90, range: 15000000, duration: 4, roll: 0 }
};

// 视角切换函数
function switchView(viewName) {
  if (!tileset || !viewer) return;
  const config = viewConfigs[viewName];
  if (!config) return;

  const offset = new Cesium.HeadingPitchRange(
    Cesium.Math.toRadians(config.heading),
    Cesium.Math.toRadians(config.pitch),
    config.range
  );

  // 优先使用平滑动画切换（flyToBoundingSphere），否则退回zoomTo
  if (typeof config.duration === 'number') {
    viewer.camera.flyToBoundingSphere(tileset.boundingSphere, {
      offset,
      duration: config.duration
    });
  } else {
    viewer.zoomTo(tileset, offset, true);
  }
}
onMounted(async () => {
  // 设置 Cesium Ion token，确保 3D Tiles 能正常加载
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxMTQ0YmFjOC00Y2FkLTRhYmYtODE3OS02ZjUzZTFhZjdmNzAiLCJpZCI6MzY4NjA1LCJpYXQiOjE3NjgxMTMwMTN9.LZFnwANyd7o3LPJzEx31hzPHU7P4fznLO3DHbWhXAG8';
  // 设置 Cesium 基础路径
  window.CESIUM_BASE_URL = '/Cesium-1.136/Build/Cesium/';

  // 创建 Viewer，使用 ArcGIS 影像底图，无需 token
  viewer = new Cesium.Viewer('cesiumContainer', {
    animation: false,
    baseLayerPicker: true,
    fullscreenButton: true,
    homeButton: true,
    sceneModePicker: true,
    timeline: false,
    navigationHelpButton: false,
    imageryProvider: new Cesium.ArcGisMapServerImageryProvider({
      url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
    })
  });

  // ========== 添加三维地形（让地图从平面变成立体） ==========
  viewer.terrainProvider = await Cesium.CesiumTerrainProvider.fromUrl(
    await Cesium.IonResource.fromAssetId(1),  // Cesium Ion全球地形（免费）
    { requestVertexNormals: true }
  );

  // 开启地形深度检测（让3D模型贴合地形）
  viewer.scene.globe.depthTestAgainstTerrain = true;

  // 设置初始视图（北京）
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 15000000),
    orientation: {
      heading: 0,
      pitch: Cesium.Math.toRadians(-90),
      roll: 0
    }
  });

  // 加载 3D Tiles（assetId: 4341246）
  try {
    const tilesetLoaded = viewer.scene.primitives.add(
      await Cesium.Cesium3DTileset.fromIonAssetId(4341246)
    );
    await tilesetLoaded.readyPromise;
    tileset = tilesetLoaded;  // 保存到全局变量

    // 初始化默认视角（与视角按钮一致，这里选“正视视角”）
    switchView('frontendView');
    addTilesetInteraction();
  } catch (error) {
    console.error('❌ 加载 3D Tiles 失败:', error);
  }
});

function addTilesetInteraction() {
  if (!tileset) return;
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  handler.setInputAction((click) => {
    const pickedFeature = viewer.scene.pick(click.position);
    if (Cesium.defined(pickedFeature) && pickedFeature.primitive === tileset) {
      const feature = pickedFeature.getProperty('feature');
      console.log('点击了模型:', feature);
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
}
</script>

<style scoped>
#cesiumContainer {
  width: 100%;
  height: 100vh;
}
/* 视角按钮按钮样式 */
.view-controls {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 12px;
  z-index: 1000;
}

.view-controls button {
  padding: 10px 15px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.view-controls button:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.05);
}
</style>
