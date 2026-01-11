<template>
  <div id="cesiumContainer"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import * as Cesium from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'

let viewer = null
let tileset = null

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

  // 设置初始视图（北京）
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 15000000),
    orientation: {
      heading: 0,
      pitch: Cesium.Math.toRadians(-90),
      roll: 0
    }
  });

  // 加载 3D Tiles（assetId: 4339409）
  try {
    const tileset = viewer.scene.primitives.add(
      await Cesium.Cesium3DTileset.fromIonAssetId(4339409)
    );
    await tileset.readyPromise;
    // 自动飞到模型区域
    viewer.zoomTo(tileset);
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
</style>
