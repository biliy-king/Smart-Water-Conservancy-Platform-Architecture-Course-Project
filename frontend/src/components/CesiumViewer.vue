<template>
  <div id="cesiumContainer"></div>
</template>

<script>
export default {
  name: 'CesiumViewer',
  data() {
    return {
      viewer: null,
      tileset: null
    };
  },
  async mounted() {
    await this.initCesium();
    await this.load3DTiles();
  },
  methods: {
    async initCesium() {
      // 初始化 Cesium
      if (typeof Cesium === 'undefined') {
        console.error('Cesium 未加载');
        return;
      }

      // 设置基础路径
      window.CESIUM_BASE_URL = '/Cesium-1.136/Build/Cesium/';

      // 设置 Cesium Ion 令牌
      Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1N2ZkNTE4Ny05ZjQ3LTQwYzMtYWY1Yy0zOThkMjk3OTQ4NjUiLCJpZCI6MzY4NjA1LCJpYXQiOjE3NjU0MjMzMjF9.mglp9vKY7f6NvixJe-z2F42sPNTR5-FJhXut2JgtNv4';

      // 创建 Viewer
      this.viewer = new Cesium.Viewer('cesiumContainer', {
        animation: false,
        baseLayerPicker: true,
        fullscreenButton: true,
        homeButton: true,
        sceneModePicker: true,
        timeline: false,
        navigationHelpButton: false,

        // 使用 ArcGIS 影像
        imageryProvider: new Cesium.ArcGisMapServerImageryProvider({
          url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
        }),

        // 地形
        //terrainProvider: Cesium.createWorldTerrain(),

        // 其他配置...
      });

      // 设置初始视图
      this.viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 15000000),
        orientation: {
          heading: 0,
          pitch: Cesium.Math.toRadians(-90),
          roll: 0
        }
      });

      console.log('✅ Cesium 初始化完成');
    },

    async load3DTiles() {
      if (!this.viewer) {
        console.error('Cesium Viewer 未初始化');
        return;
      }

      try {
        console.log('开始加载 3D Tiles...');


        // 加载你的 3D Tiles（assetId: 4326220）
        this.tileset = await Cesium.Cesium3DTileset.fromIonAssetId(4326220, {
          show: true,
          maximumScreenSpaceError: 2, // 控制细节级别
          maximumNumberOfLoadedTiles: 1000, // 性能控制
          dynamicScreenSpaceError: true,
          dynamicScreenSpaceErrorDensity: 0.00278,
          dynamicScreenSpaceErrorFactor: 4.0
        });

        // 添加到场景
        this.viewer.scene.primitives.add(this.tileset);

        // 等待 tileset 准备完成
        await this.tileset.readyPromise;

        // 自动定位到模型区域
        await this.viewer.zoomTo(this.tileset);

        console.log('✅ 3D Tiles 加载完成');

        // 可选：添加一些交互
        this.addTilesetInteraction();

      } catch (error) {
        console.error('❌ 加载 3D Tiles 失败:', error);
      }
    },

    addTilesetInteraction() {
      if (!this.tileset) return;

      // 监听点击事件
      const handler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);

      handler.setInputAction((click) => {
        const pickedFeature = this.viewer.scene.pick(click.position);
        if (Cesium.defined(pickedFeature) && pickedFeature.primitive === this.tileset) {
          const feature = pickedFeature.getProperty('feature');
          console.log('点击了模型:', feature);
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    }
  },

  beforeUnmount() {
    // 清理资源
    if (this.viewer) {
      this.viewer.destroy();
    }
  }
};
</script>

<style scoped>
#cesiumContainer {
  width: 100%;
  height: 100vh;
}
</style>
