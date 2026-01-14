/**
 * 大坝分段蒙版热区使用示例
 * 
 * 在 SceneView.vue 或其他父组件中使用
 */

// ====== 示例1：手动配置11个坝段的边界坐标 ======

// 假设大坝沿经度方向分布，从 111.15 到 111.26（11段，每段约0.01度）
function setupMaskWithManualBounds(cesiumSceneRef) {
  const segmentBounds = [];
  
  // 定义大坝的整体范围
  const startLon = 111.15;  // 起始经度
  const endLon = 111.26;    // 结束经度
  const lat1 = 30.80;       // 上边界纬度
  const lat2 = 30.79;       // 下边界纬度
  const height = 50;        // 高度（米）
  
  // 计算每段的宽度
  const segmentWidth = (endLon - startLon) / 11;
  
  // 为每个坝段生成边界坐标
  for (let i = 0; i < 11; i++) {
    const segmentStartLon = startLon + i * segmentWidth;
    const segmentEndLon = startLon + (i + 1) * segmentWidth;
    
    // 每个坝段是一个矩形（4个顶点）
    segmentBounds.push([
      [segmentStartLon, lat1, height],  // 左上
      [segmentEndLon, lat1, height],      // 右上
      [segmentEndLon, lat2, height],      // 右下
      [segmentStartLon, lat2, height]    // 左下
    ]);
  }
  
  // 应用配置
  cesiumSceneRef.value.setMaskConfig({
    enabled: true,
    debugMode: true,  // 开启调试模式，显示红色热区边界
    totalSegments: 11,
    segmentBounds: segmentBounds
  });
  
  console.log('蒙版热区配置完成，共11个坝段');
}

// ====== 示例2：使用自动生成（基于几何划分法） ======

function setupMaskWithAutoGeneration(cesiumSceneRef) {
  // 先确保模型边界已计算
  cesiumSceneRef.value.calculateModelBounds();
  
  // 自动生成蒙版热区
  cesiumSceneRef.value.setMaskConfig({
    enabled: true,
    debugMode: true,  // 开启调试模式查看生成的热区
    totalSegments: 11
    // 不提供 segmentBounds，会自动调用 createMaskEntitiesAuto()
  });
  
  console.log('自动生成蒙版热区完成');
}

// ====== 示例3：从实际点击获取坐标 ======

// 在浏览器控制台中运行此函数，然后点击模型上的点
function enableCoordinatePicker(viewer) {
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  const coordinates = [];
  
  handler.setInputAction((click) => {
    const position = viewer.scene.pickPosition(click.position);
    if (Cesium.defined(position)) {
      const cartographic = Cesium.Cartographic.fromCartesian(position);
      const lon = Cesium.Math.toDegrees(cartographic.longitude);
      const lat = Cesium.Math.toDegrees(cartographic.latitude);
      const height = cartographic.height;
      
      coordinates.push([lon, lat, height]);
      
      console.log(`已记录坐标 ${coordinates.length}: [${lon.toFixed(6)}, ${lat.toFixed(6)}, ${height.toFixed(2)}]`);
      console.log('当前所有坐标:', coordinates);
      
      // 如果收集了4个点（一个矩形的4个角），可以复制这个数组用于配置
      if (coordinates.length === 4) {
        console.log('可以复制以下数组用于坝段配置:');
        console.log(JSON.stringify([coordinates], null, 2));
      }
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
  
  console.log('坐标拾取器已启用，点击模型上的点来记录坐标');
  console.log('提示：点击4个点可以形成一个矩形（一个坝段的边界）');
  
  return handler; // 返回 handler，可以调用 handler.destroy() 来停止
}

// ====== 示例4：切换调试模式 ======

function toggleDebugMode(cesiumSceneRef, enabled) {
  cesiumSceneRef.value.setMaskConfig({
    debugMode: enabled
  });
  
  if (enabled) {
    console.log('调试模式已开启：热区显示为红色半透明');
  } else {
    console.log('调试模式已关闭：热区完全透明');
  }
}

// ====== 示例5：清除所有蒙版 ======

function clearAllMasks(cesiumSceneRef) {
  cesiumSceneRef.value.clearMaskEntities();
  console.log('已清除所有蒙版热区');
}

// ====== 示例6：完整的工作流程 ======

/**
 * 完整的工作流程示例
 * 1. 先使用自动生成查看大致位置
 * 2. 开启调试模式查看热区
 * 3. 如果位置不对，使用坐标拾取器获取精确坐标
 * 4. 手动配置精确的边界
 */
function completeWorkflow(cesiumSceneRef, viewer) {
  console.log('=== 步骤1：自动生成蒙版热区 ===');
  setupMaskWithAutoGeneration(cesiumSceneRef);
  
  console.log('=== 步骤2：查看热区位置（红色半透明区域）===');
  console.log('如果位置不对，继续步骤3');
  
  console.log('=== 步骤3：使用坐标拾取器获取精确坐标 ===');
  const handler = enableCoordinatePicker(viewer);
  
  console.log('=== 步骤4：手动配置精确边界 ===');
  console.log('收集完所有坐标后，调用 setupMaskWithManualBounds(cesiumSceneRef)');
  
  // 5秒后自动停止坐标拾取器（可选）
  setTimeout(() => {
    handler.destroy();
    console.log('坐标拾取器已自动停止');
  }, 300000); // 5分钟
}

// ====== 导出供其他文件使用 ======

export {
  setupMaskWithManualBounds,
  setupMaskWithAutoGeneration,
  enableCoordinatePicker,
  toggleDebugMode,
  clearAllMasks,
  completeWorkflow
};
