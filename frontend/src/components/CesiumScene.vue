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
import { ref, onMounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

// ====== 水流流动材质（PolylineTrailMaterialProperty）集成开始 ======
// 你只需准备一张水流线条PNG贴图（如 blue-trail.png），放在 public 目录下
// 并在下方填入你的水流路径坐标和贴图路径
// 兼容 Entity API：自定义 MaterialProperty
Cesium.Material.PolylineTrailType = 'PolylineTrail';
Cesium.Material.PolylineTrailSource = `
czm_material czm_getMaterial(czm_materialInput materialInput)
{
    czm_material material = czm_getDefaultMaterial(materialInput);
    vec2 st = materialInput.st;
    float t = fract(st.s - time);
    vec4 colorImage = texture(image, vec2(t, st.t));
    material.alpha = colorImage.a * color.a;
    material.diffuse = (colorImage.rgb + color.rgb) / 2.0;
    return material;
}
`;
if (!Cesium.Material._materialCache._materials[Cesium.Material.PolylineTrailType]) {
  Cesium.Material._materialCache.addMaterial(Cesium.Material.PolylineTrailType, {
    fabric: {
      type: Cesium.Material.PolylineTrailType,
      uniforms: {
        color: new Cesium.Color(1.0, 1.0, 1.0, 1.0),
        image: Cesium.Material.DefaultImageId,
        time: 0
      },
      source: Cesium.Material.PolylineTrailSource
    },
    translucent: function () {
      return true;
    }
  });
}

// PolylineTrailMaterialProperty 实现
function PolylineTrailMaterialProperty(options) {
  this._definitionChanged = new Cesium.Event();
  this.color = options.color || Cesium.Color.CYAN;
  this.duration = options.duration || 2000;
  this.trailImage = options.trailImage || Cesium.Material.DefaultImageId;
  this._time = Date.now();
}
PolylineTrailMaterialProperty.prototype.getType = function () {
  return 'PolylineTrail';
};

// 添加 definitionChanged 属性的 getter 方法
Object.defineProperties(PolylineTrailMaterialProperty.prototype, {
  definitionChanged: {
    get: function () {
      return this._definitionChanged;
    }
  }
});

PolylineTrailMaterialProperty.prototype.getValue = function (time, result) {
  if (!result) {
    result = {};
  }
  result.color = this.color || Cesium.Color.CYAN;
  result.image = this.trailImage;
  result.time = ((Date.now() - this._time) % this.duration) / this.duration;
  return result;
};
PolylineTrailMaterialProperty.prototype.equals = function (other) {
  return this === other;
};
// ====== 水流流动材质集成结束 ======

let viewer = null;
let tileset = null;
const selectedSegmentId = ref(null);
let lastHighlightedFeatures = []; // 改为数组，支持多个feature高亮
let highlightedFeaturesMap = new Map(); // 存储高亮的feature及其原始颜色
let pendingHighlightNames = null; // 存储待高亮的节点名称（用于延迟高亮）

// 针对绿色坝体，使用橙色高亮（与绿色对比明显）
const highlightColor = Cesium.Color.ORANGE.withAlpha(0.85);
const normalColor = Cesium.Color.WHITE;

// 清除所有高亮
function clearHighlight() {
  highlightedFeaturesMap.forEach((originalColor, feature) => {
    if (feature && !feature.content.isDestroyed()) {
      feature.color = originalColor;
    }
  });
  highlightedFeaturesMap.clear();
  lastHighlightedFeatures = [];
}

/**
 * 根据节点名称高亮feature
 * @param {string|string[]} nodeNames - 要高亮的节点名称，可以是单个字符串或字符串数组
 * 例如: highlightFeaturesByName('segment_1') 或 highlightFeaturesByName(['segment_1', 'wonderment'])
 * 支持的节点类型：segment_1-10, wonderment, IP/IP1-3, EX/EX1-10
 * 
 * 功能说明：
 * 1. 遍历tileset中的所有tiles和features
 * 2. 通过多种方式匹配节点名称（name属性、Name属性、NAME属性，或属性值包含目标名称）
 * 3. 高亮所有匹配的features，使用橙色高亮（针对绿色坝体优化）
 * 4. 支持同时高亮多个节点（如segment_1和wonderment）
 * 5. 保存待高亮的名称，在tileset加载新tiles时自动重新检查并高亮
 */
function highlightFeaturesByName(nodeNames) {
  if (!tileset || !viewer) return;
  
  // 将单个名称转换为数组
  const names = Array.isArray(nodeNames) ? nodeNames : [nodeNames];
  
  // 保存待高亮的名称，以便在tileset加载新tiles时重新检查
  pendingHighlightNames = names;
  
  // 执行高亮
  performHighlight(names);
}

// 实际执行高亮的内部函数
function performHighlight(names) {
  if (!tileset || !viewer || !names || names.length === 0) return;
  
  let highlightedCount = 0;
  
  // 遍历tileset的所有tiles来查找匹配的feature
  function processTile(tile) {
    if (!tile || tile.isDestroyed()) return;
    
    const content = tile.content;
    if (!content || content.isDestroyed()) return;
    
    // 检查是否有features
    if (content.featuresLength > 0) {
      for (let i = 0; i < content.featuresLength; i++) {
        const feature = content.getFeature(i);
        if (!feature) continue;
        
        // 如果已经高亮过，跳过
        if (highlightedFeaturesMap.has(feature)) continue;
        
        // 尝试通过多种方式获取节点名称
        let featureName = null;
        
        // 方法1: 通过getProperty获取name属性
        if (typeof feature.getProperty === 'function') {
          featureName = feature.getProperty('name') || 
                       feature.getProperty('Name') || 
                       feature.getProperty('NAME');
        }
        
        // 方法2: 通过feature的id或name属性
        if (!featureName && feature.name) {
          featureName = feature.name;
        }
        
        // 方法3: 检查所有属性，查找包含目标名称的属性
        if (!featureName && typeof feature.getPropertyNames === 'function') {
          const propNames = feature.getPropertyNames();
          for (const propName of propNames) {
            const propValue = feature.getProperty(propName);
            if (typeof propValue === 'string') {
              // 检查属性值是否包含目标节点名称
              for (const targetName of names) {
                if (propValue.toLowerCase().includes(targetName.toLowerCase())) {
                  featureName = propValue;
                  break;
                }
              }
              if (featureName) break;
            }
          }
        }
        
        // 如果找到匹配的节点名称，进行高亮
        if (featureName) {
          for (const targetName of names) {
            if (featureName.toLowerCase().includes(targetName.toLowerCase())) {
              // 保存原始颜色
              const originalColor = Cesium.Color.clone(feature.color);
              highlightedFeaturesMap.set(feature, originalColor);
              lastHighlightedFeatures.push(feature);
              
              // 设置高亮颜色
              feature.color = highlightColor;
              highlightedCount++;
              console.log(`高亮节点: ${featureName} (匹配: ${targetName})`);
              break;
            }
          }
        }
      }
    }
    
    // 递归处理子tiles
    const children = tile.children;
    if (children) {
      for (let i = 0; i < children.length; i++) {
        processTile(children[i]);
      }
    }
  }
  
  // 从根tile开始处理
  if (tileset.root) {
    processTile(tileset.root);
  }
  
  // 请求重新渲染
  viewer.scene.requestRender();
  
  if (highlightedCount > 0) {
    console.log(`本次高亮了 ${highlightedCount} 个匹配的feature，总计 ${lastHighlightedFeatures.length} 个`);
  }
}

/**
 * 提取节点名称模式（用于匹配）
 * 支持：segment_1-10, wonderment, IP/IP1-3, EX/EX1-10
 * @param {string} featureName - 节点的完整名称
 * @returns {string|null} - 匹配的节点模式名称，如果不匹配则返回null
 */
function extractNodePattern(featureName) {
  if (!featureName) return null;
  
  const lowerName = featureName.toLowerCase();
  
  // 匹配 segment_1 到 segment_10
  const segmentMatch = lowerName.match(/segment[_\s-]?(\d+)/i);
  if (segmentMatch) {
    const num = segmentMatch[1];
    if (parseInt(num) >= 1 && parseInt(num) <= 10) {
      return `segment_${num}`;
    }
  }
  
  // 匹配 wonderment
  if (lowerName.includes('wonderment')) {
    return 'wonderment';
  }
  
  // 匹配 IP, IP1, IP2, IP3
  const ipMatch = lowerName.match(/ip(\d+)?/i);
  if (ipMatch) {
    if (ipMatch[1]) {
      const num = parseInt(ipMatch[1]);
      if (num >= 1 && num <= 3) {
        return `IP${num}`;
      }
    } else {
      return 'IP';
    }
  }
  
  // 匹配 EX, EX1 到 EX10
  const exMatch = lowerName.match(/ex(\d+)?/i);
  if (exMatch) {
    if (exMatch[1]) {
      const num = parseInt(exMatch[1]);
      if (num >= 1 && num <= 10) {
        return `EX${num}`;
      }
    } else {
      return 'EX';
    }
  }
  
  return null;
}

// 高亮指定名称的节点（供外部调用）
function highlightSegment(segmentName) {
  highlightFeaturesByName(segmentName);
}

function addTilesetInteraction() {
  if (!tileset || !viewer) return;
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  
  // 鼠标悬停高亮
  let hoveredFeature = null;
  let hoveredOriginalColor = null;
  
  handler.setInputAction((movement) => {
    const pickedFeature = viewer.scene.pick(movement.endPosition);
    
    // 清除之前的悬停高亮
    if (hoveredFeature && !hoveredFeature.content.isDestroyed()) {
      hoveredFeature.color = hoveredOriginalColor;
      hoveredFeature = null;
      hoveredOriginalColor = null;
    }
    
    // 如果悬停到tileset的feature上
    if (Cesium.defined(pickedFeature) && pickedFeature instanceof Cesium.Cesium3DTileFeature && pickedFeature.primitive === tileset) {
      // 获取feature名称
      let featureName = null;
      if (typeof pickedFeature.getProperty === 'function') {
        featureName = pickedFeature.getProperty('name') || 
                     pickedFeature.getProperty('Name') || 
                     pickedFeature.getProperty('NAME');
      }
      if (!featureName && pickedFeature.name) {
        featureName = pickedFeature.name;
      }
      
      // 如果是支持的节点类型，进行悬停高亮
      if (featureName && extractNodePattern(featureName)) {
        hoveredFeature = pickedFeature;
        hoveredOriginalColor = Cesium.Color.clone(pickedFeature.color);
        // 使用稍微不同的颜色表示悬停（比点击高亮稍亮）
        pickedFeature.color = Cesium.Color.ORANGE.withAlpha(0.95);
        viewer.scene.requestRender();
      }
    }
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
  
  // 点击选择和高亮
  handler.setInputAction((click) => {
    console.log('点击事件触发，位置:', click.position);
    
    // 先尝试使用 pick
    let pickedFeature = viewer.scene.pick(click.position);
    console.log('pick 结果:', pickedFeature);
    
    // 如果 pick 失败，尝试使用 drillPick 获取所有对象
    if (!Cesium.defined(pickedFeature)) {
      console.log('pick 未选中对象，尝试使用 drillPick...');
      const drillPickResults = viewer.scene.drillPick(click.position);
      console.log('drillPick 结果数量:', drillPickResults.length);
      console.log('drillPick 结果:', drillPickResults);
      
      // 在 drillPick 结果中查找 Cesium3DTileFeature
      for (const result of drillPickResults) {
        console.log('drillPick 结果项:', result);
        console.log('结果对象:', result.object);
        console.log('结果类型:', result.object?.constructor?.name);
        
        if (result.object instanceof Cesium.Cesium3DTileFeature && result.object.primitive === tileset) {
          pickedFeature = result.object;
          console.log('在 drillPick 中找到 Cesium3DTileFeature:', pickedFeature);
          break;
        }
      }
    }
    
    if (!Cesium.defined(pickedFeature)) {
      console.log('点击空白处，未找到任何 feature，清除高亮');
      clearHighlight();
      return;
    }
    
    if (!(pickedFeature instanceof Cesium.Cesium3DTileFeature)) {
      console.log('点击的对象不是 Cesium3DTileFeature，类型:', pickedFeature.constructor?.name);
      clearHighlight();
      return;
    }
    
    if (pickedFeature.primitive !== tileset) {
      console.log('点击的对象不属于当前 tileset');
      clearHighlight();
      return;
    }

    // 尝试输出所有属性名和属性值（用于调试）
    if (typeof pickedFeature.getProperty === 'function' && typeof pickedFeature.getPropertyNames === 'function') {
      const propNames = pickedFeature.getPropertyNames();
      console.log('所有属性名:', propNames);
      propNames.forEach(name => {
        console.log(`属性 ${name}:`, pickedFeature.getProperty(name));
      });
    }

    // 获取feature名称
    let featureName = null;
    if (typeof pickedFeature.getProperty === 'function') {
      featureName = pickedFeature.getProperty('name') || 
                   pickedFeature.getProperty('Name') || 
                   pickedFeature.getProperty('NAME');
    }
    if (!featureName && pickedFeature.name) {
      featureName = pickedFeature.name;
    }
    
    console.log('点击的feature名称:', featureName);

    // 提取节点模式并高亮所有匹配的节点
    if (featureName) {
      const nodePattern = extractNodePattern(featureName);
      if (nodePattern) {
        // 匹配到已知节点模式，高亮所有同类型节点
        highlightFeaturesByName(nodePattern);
        selectedSegmentId.value = nodePattern;
        console.log(`高亮节点模式: ${nodePattern}`);
      } else {
        // 其他节点，只高亮当前点击的feature
        clearHighlight();
        const originalColor = Cesium.Color.clone(pickedFeature.color);
        highlightedFeaturesMap.set(pickedFeature, originalColor);
        lastHighlightedFeatures.push(pickedFeature);
        pickedFeature.color = highlightColor;
        viewer.scene.requestRender();
        selectedSegmentId.value = featureName;
      }
    } else {
      // 保留原有分段ID识别逻辑
      let segmentId = null;
      if (typeof pickedFeature.getProperty === 'function') {
        segmentId = pickedFeature.getProperty('segmentId');
      } else if (pickedFeature.name) {
        const match = pickedFeature.name.match(/\d+/);
        if (match) segmentId = match[0];
      } else if (pickedFeature.id) {
        const match = String(pickedFeature.id).match(/\d+/);
        if (match) segmentId = match[0];
      }

      if (segmentId) {
        selectedSegmentId.value = segmentId;
        console.log('点击坝段 segmentId:', segmentId);
      } else {
        console.warn('未能解析分段ID，请检查模型属性');
        console.log('pickedFeature:', pickedFeature);
      }
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
}

// 视角配置对象
const viewConfigs = {
  panoramaView: { heading: 30, pitch: -90, range: 7000, duration: 1.5, roll: 0 },
  frontendView: { heading: -75, pitch: -30, range: 3000, duration: 1.5, roll: 0 },
  reservoirView: { heading: 120, pitch: -20, range: 3000, duration: 1.5, roll: 0 },
  damView: { heading: -75, pitch: -30, range: 3000, duration: 1.5, roll: 0 }, // 与初始视角（frontendView）相同
  earthView: { heading: 30, pitch: -90, range: 15000000, duration: 4, roll: 0 }
};

function switchView(viewName) {
  if (!tileset || !viewer) return;
  const config = viewConfigs[viewName];
  if (!config) {
    console.warn(`视角配置不存在: ${viewName}`);
    return;
  }

  const offset = new Cesium.HeadingPitchRange(
    Cesium.Math.toRadians(config.heading),
    Cesium.Math.toRadians(config.pitch),
    config.range
  )
  if (typeof config.duration === 'number') {
    viewer.camera.flyToBoundingSphere(tileset.boundingSphere, {
      offset,
      duration: config.duration
    });
  } else {
    viewer.zoomTo(tileset, offset, true);
  }
}

// 暴露方法供父组件调用
defineExpose({
  switchView,
  highlightSegment,
  highlightFeaturesByName,
  clearHighlight
})

onMounted(async () => {
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxMTQ0YmFjOC00Y2FkLTRhYmYtODE3OS02ZjUzZTFhZjdmNzAiLCJpZCI6MzY4NjA1LCJpYXQiOjE3NjgxMTMwMTN9.LZFnwANyd7o3LPJzEx31hzPHU7P4fznLO3DHbWhXAG8';
  window.CESIUM_BASE_URL = '/Cesium-1.136/Build/Cesium/';

  viewer = new Cesium.Viewer('cesiumContainer', {
    animation: false,
    baseLayerPicker: true,
    fullscreenButton: true,
    homeButton: true,
    sceneModePicker: true,
    timeline: false,
    navigationHelpButton: false,
    infoBox: false, // 禁用默认的 InfoBox（避免显示偏移的绿色框）
    selectionIndicator: false, // 禁用默认的选择指示器（绿色框）
    imageryProvider: new Cesium.ArcGisMapServerImageryProvider({
      url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
    })
  });

  viewer.terrainProvider = await Cesium.CesiumTerrainProvider.fromUrl(
    await Cesium.IonResource.fromAssetId(1),
    { requestVertexNormals: true }
  );

  viewer.scene.globe.depthTestAgainstTerrain = true;

  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 15000000),
    orientation: {
      heading: 0,
      pitch: Cesium.Math.toRadians(-90),
      roll: 0
    }
  });

  try {
    const tilesetLoaded = viewer.scene.primitives.add(
      await Cesium.Cesium3DTileset.fromIonAssetId(4345573)
    );
    await tilesetLoaded.readyPromise;
    tileset = tilesetLoaded;
    
    // 调试：检查 tileset 是否有 feature
    console.log('Tileset 加载完成');
    console.log('Tileset root:', tileset.root);
    if (tileset.root && tileset.root.content) {
      console.log('Root content featuresLength:', tileset.root.content.featuresLength);
      console.log('Root content 类型:', tileset.root.content.constructor?.name);
      if (tileset.root.content.featuresLength > 0) {
        console.log('有 features，可以尝试获取第一个 feature');
        const firstFeature = tileset.root.content.getFeature(0);
        if (firstFeature) {
          console.log('第一个 feature:', firstFeature);
          if (typeof firstFeature.getPropertyNames === 'function') {
            const propNames = firstFeature.getPropertyNames();
            console.log('第一个 feature 的属性名:', propNames);
          }
        }
      } else {
        console.warn('⚠️ Tileset 没有 features！这可能是从 GLB 转换的问题。');
        console.log('建议：在 Blender 中为节点添加自定义属性，然后导出为 glTF 格式');
      }
    }

    // 等待tileset完全加载后再进行交互设置
    // 当tileset加载新tiles时，重新检查并高亮待高亮的节点
    tileset.loadProgress.addEventListener((numberOfPendingRequests, numberOfTilesProcessing) => {
      if (numberOfPendingRequests === 0 && numberOfTilesProcessing === 0) {
        console.log('Tileset加载完成，所有tiles已加载');
        // 如果有待高亮的节点名称，重新执行高亮（确保新加载的tiles也被高亮）
        if (pendingHighlightNames && pendingHighlightNames.length > 0) {
          performHighlight(pendingHighlightNames);
        }
      } else {
        // 在加载过程中，也尝试高亮已加载的tiles（增量高亮）
        if (pendingHighlightNames && pendingHighlightNames.length > 0) {
          performHighlight(pendingHighlightNames);
        }
      }
    });

    switchView('frontendView');
    addTilesetInteraction();
    // ====== 添加水流水面（Polygon） ======
    const absImgUrl = window.location.origin + '/images/water.png';
    
    // ====== 定义河道边界坐标（您可以替换为实际的河道边界坐标） ======
    // 格式：[[经度, 纬度, 高度], [经度, 纬度, 高度], ...]
    // 注意：坐标需要形成一个闭合的多边形（Cesium会自动闭合）
    // 这里先用中心路径的前两个点生成一个简单的测试水面（矩形）
    // 您需要提供完整的河道边界坐标来替换这个数组
    const waterSurfaceCoordinates = [
      [111.15, 30.80, 50],  // 起点左侧（示例坐标，请替换）
      [111.17, 30.80, 50],  // 第二点左侧（示例坐标，请替换）
      [111.15, 30.78, 50],  // 第二点右侧（示例坐标，请替换）
      [111.17, 30.78, 50]   // 起点右侧（示例坐标，请替换）
    ];
    
    // ====== 如果您有完整的河道边界坐标，请替换上面的 waterSurfaceCoordinates 数组 ======
    // 示例格式（弯弯曲曲的河道边界）：
    // const waterSurfaceCoordinates = [
    //   [111.1615, 30.8025, 50],  // 左边界起点
    //   [111.1613, 30.8023, 50],  // 左边界点
    //   [111.1600, 30.8010, 50],  // 左边界点
    //   [111.1582, 30.7991, 50],  // 左边界点
    //   [111.1580, 30.7990, 50],  // 左边界终点
    //   [111.1581, 30.7989, 50],  // 右边界终点
    //   [111.1583, 30.7991, 50],  // 右边界点
    //   [111.1601, 30.8011, 50],  // 右边界点
    //   [111.1614, 30.8024, 50],  // 右边界点
    //   [111.1616, 30.8026, 50]   // 右边界起点（与第一个点接近，形成闭合）
    // ];
    
    // ====== 创建水流水面材质 ======
    // 使用ImageMaterialProperty（Entity API推荐的方式）
    // 注意：Entity API暂时不支持自定义Material的动画，可以先使用静态纹理
    // 如需动画，后续可以考虑使用Primitive API或者更新纹理坐标
    const waterMaterial = new Cesium.ImageMaterialProperty({
      image: absImgUrl,
      repeat: new Cesium.Cartesian2(10.0, 1.0), // 横向重复10次，纵向1次（可根据需要调整）
      transparent: true,
      color: Cesium.Color.CYAN.withAlpha(0.8)
    });
    
    // 创建水面Polygon
    viewer.entities.add({
      name: '河道水面',
      polygon: {
        hierarchy: Cesium.Cartesian3.fromDegreesArrayHeights(
          waterSurfaceCoordinates.flatMap(coord => [coord[0], coord[1], coord[2]])
        ),
        material: waterMaterial,
        // 注意：当 perPositionHeight 为 true 时，不需要设置 height
        perPositionHeight: true, // 使用每个坐标点的高度
        extrudedHeight: 0, // 不拉伸
        outline: false, // 不显示轮廓线
        closeTop: true,
        closeBottom: false
      }
    });
    
    // TODO: 如需添加水流动画效果，可以考虑：
    // 1. 使用Primitive API替代Entity API（更灵活，支持自定义Material）
    // 2. 或者使用MaterialProperty的更新机制来实现动画
    
    // ====== 水流水面添加结束 ======
    // 注意：
    // 1. 请将 waterSurfaceCoordinates 替换为您的实际河道边界坐标
    // 2. 坐标格式：[经度, 纬度, 高度(米)]
    // 3. 坐标需要形成一个闭合的多边形
    // 4. 如需添加水流动画，可以使用自定义Material实现
    // 注意：如仍报错，请确保 /images/water.png 能被 <img src="http://localhost:5174/images/water.png"> 直接访问且为标准 PNG
    // 如果依然报错，可尝试用官方 PolylineGlowMaterialProperty 测试，排除自定义材质 bug
  } catch (error) {
    console.error('❌ 加载 3D Tiles 失败:', error);
  }
});
</script>


<style scoped>
#cesiumContainer {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}
/* 视角按钮按钮样式 - 隐藏，因为现在使用右侧面板 */
.view-controls {
  display: none;
}
</style>
