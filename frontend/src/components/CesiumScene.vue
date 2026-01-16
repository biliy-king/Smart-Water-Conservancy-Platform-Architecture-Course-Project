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
import { ref, onMounted, inject, computed } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

// 获取 PageScaler 的缩放比例
const pageScale = inject('pageScale', ref(1));

// 计算缩放后的坐标转换函数
// 由于 PageScaler 使用 transform: scale() 和 transformOrigin: center center
// 需要将屏幕坐标转换为 canvas 内的实际坐标
function getScaledPosition(originalPosition, canvas) {
  if (!canvas || !pageScale.value || pageScale.value === 1) {
    return originalPosition;
  }
  
  const scale = pageScale.value;
  const designWidth = 2560;
  const designHeight = 1400;
  
  // 计算缩放中心（屏幕中心，因为 transformOrigin 是 center center）
  const screenCenterX = window.innerWidth / 2;
  const screenCenterY = window.innerHeight / 2;
  
  // 将鼠标坐标转换为相对于缩放中心的偏移
  const relativeX = originalPosition.x - screenCenterX;
  const relativeY = originalPosition.y - screenCenterY;
  
  // 应用反向缩放，得到在设计尺寸坐标系中相对于中心的偏移
  const designOffsetX = relativeX / scale;
  const designOffsetY = relativeY / scale;
  
  // 转换为 canvas 坐标（canvas 坐标系从左上角 (0,0) 开始）
  // canvas 的实际尺寸是 designWidth x designHeight
  let canvasX = designWidth / 2 + designOffsetX;
  let canvasY = designHeight / 2 + designOffsetY;
  
  // ====== 手动偏移调整区域 ======
  // 如果鼠标位置有偏移，在这里添加偏移量进行调整
  // 正值向右/向下偏移，负值向左/向上偏移
  const offsetX = 120;// 水平偏移（像素）
  const offsetY = -50; // 垂直偏移（像素）
  
  canvasX += offsetX;
  canvasY += offsetY;
  // ====== 手动偏移调整区域结束 ======
  
  return new Cesium.Cartesian2(canvasX, canvasY);
}

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

// ====== 水面流动材质（WaterFlowMaterialProperty）集成开始 ======
// 用于河道水面的流动动画效果
Cesium.Material.WaterFlowType = 'WaterFlow';
Cesium.Material.WaterFlowSource = `
czm_material czm_getMaterial(czm_materialInput materialInput)
{
    czm_material material = czm_getDefaultMaterial(materialInput);
    vec2 st = materialInput.st;
    
    // 流动效果：沿X轴（横向）移动纹理坐标
    // speed 控制流动速度，direction 控制流动方向（1.0 为正向，-1.0 为反向）
    // 使用 fract 函数实现循环流动
    float flowTime = time * speed * direction;
    vec2 flowSt = vec2(fract(st.s * repeat.x - flowTime), fract(st.t * repeat.y));
    
    // 采样纹理
    vec4 colorImage = texture(image, flowSt);
    
    // 混合颜色和纹理，创建水效果
    material.diffuse = mix(color.rgb, colorImage.rgb * 1.2, 0.8); // 稍微提亮纹理
    material.alpha = color.a * (0.6 + colorImage.a * 0.4); // 保持透明度
    
    return material;
}
`;

if (!Cesium.Material._materialCache._materials[Cesium.Material.WaterFlowType]) {
  Cesium.Material._materialCache.addMaterial(Cesium.Material.WaterFlowType, {
    fabric: {
      type: Cesium.Material.WaterFlowType,
      uniforms: {
        color: new Cesium.Color(0.2, 0.5, 1.0, 0.7), // 水的颜色（蓝色）
        image: Cesium.Material.DefaultImageId,
        time: 0,
        speed: 0.5, // 流动速度（0-1之间，值越大流动越快）
        direction: 1.0, // 流动方向（1.0 为正向，-1.0 为反向）
        repeat: new Cesium.Cartesian2(15.0, 1.0) // 纹理重复次数
      },
      source: Cesium.Material.WaterFlowSource
    },
    translucent: function () {
      return true;
    }
  });
}

// WaterFlowMaterialProperty 实现
function WaterFlowMaterialProperty(options) {
  this._definitionChanged = new Cesium.Event();
  this.color = options.color || new Cesium.Color(0.2, 0.5, 1.0, 0.7);
  this.speed = options.speed || 0.5; // 流动速度
  this.direction = options.direction || 1.0; // 流动方向（1.0 正向，-1.0 反向）
  this.repeat = options.repeat || new Cesium.Cartesian2(15.0, 1.0); // 纹理重复
  this.waterImage = options.waterImage || Cesium.Material.DefaultImageId;
  this.duration = options.duration || 10000; // 循环周期（毫秒），默认10秒
  this._startTime = Date.now();
}

WaterFlowMaterialProperty.prototype.getType = function () {
  return 'WaterFlow';
};

Object.defineProperties(WaterFlowMaterialProperty.prototype, {
  definitionChanged: {
    get: function () {
      return this._definitionChanged;
    }
  }
});

WaterFlowMaterialProperty.prototype.getValue = function (time, result) {
  if (!result) {
    result = {};
  }
  result.color = this.color;
  result.image = this.waterImage;
  result.speed = this.speed;
  result.direction = this.direction;
  result.repeat = this.repeat;
  
  // 使用简单的循环时间，不依赖 Cesium 时间系统
  // 计算从开始时间到现在的经过时间，然后取模实现循环
  const elapsed = Date.now() - this._startTime;
  result.time = (elapsed % this.duration) / 1000.0; // 转换为秒，并循环
  
  return result;
};

WaterFlowMaterialProperty.prototype.equals = function (other) {
  return this === other;
};
// ====== 水面流动材质集成结束 ======

let viewer = null;
let tileset = null;
const selectedSegmentId = ref(null);
let lastHighlightedFeatures = []; // 改为数组，支持多个feature高亮
let highlightedFeaturesMap = new Map(); // 存储高亮的feature及其原始颜色
let pendingHighlightNames = null; // 存储待高亮的节点名称（用于延迟高亮）

// 针对绿色坝体，使用橙色高亮（与绿色对比明显）
const highlightColor = Cesium.Color.ORANGE.withAlpha(0.85);
const normalColor = Cesium.Color.WHITE;

// ====== 测点配置 ======
// 测点坐标配置（EX1-10，共10个测点，前端写死）
const SENSOR_POINTS = {
  // EX1-10 测点坐标
  EX1: [111.17105840592149, 30.7837179337107, 498.1831078469948],
  EX2: [111.17031740592149, 30.781953337107, 498.1831078469948],
  EX3: [111.16977640592149, 30.7807899337107, 498.1831078469948],
  EX4: [111.16933540592149, 30.7797259337107, 498.1831078469948],
  EX5: [111.16864440592149, 30.77841202900185, 498.1831078469948],
  EX6: [111.16811640592149, 30.7771289337107, 498.1831078469948],
  EX7: [111.16768840592149, 30.77604583841955, 498.1831078469948],
  EX8: [111.16708540592149, 30.7749127431284, 498.1831078469948],
  EX9: [111.16661140592149, 30.77363764783725, 498.1831078469948],
  EX10: [111.16596640592149, 30.7722205525461, 498.1831078469948]
}

// 存储测点实体
let sensorEntities = new Map(); // key: 测点名称（如 'EX1'），value: Entity对象

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
  let hoveredSensorEntity = null; // 悬停的测点实体
  let hoveredSensorOriginalPoint = null; // 悬停测点的原始点样式
  
  handler.setInputAction((movement) => {
    // 调整鼠标坐标以考虑 PageScaler 的缩放
    const adjustedPosition = getScaledPosition(movement.endPosition, viewer.canvas);
    const pickedObject = viewer.scene.pick(adjustedPosition);
    
    // ====== 优先检测测点实体悬停 ======
    let isHoveringSensor = false;
    
    if (Cesium.defined(pickedObject) && pickedObject.id) {
      const entity = pickedObject.id;
      
      // 检查是否是测点实体
      if (entity.sensorName && sensorEntities.has(entity.sensorName)) {
        isHoveringSensor = true;
        
        // 如果之前悬停的不是这个测点，清除之前的悬停效果
        if (hoveredSensorEntity && hoveredSensorEntity !== entity) {
          restoreSensorHover(hoveredSensorEntity, hoveredSensorOriginalPoint);
        }
        
        // 如果当前没有悬停效果，保存原始样式并应用悬停效果
        if (hoveredSensorEntity !== entity) {
          hoveredSensorEntity = entity;
          hoveredSensorOriginalPoint = {
            pixelSize: entity.point.pixelSize.getValue(),
            color: entity.point.color.getValue(),
            outlineColor: entity.point.outlineColor.getValue(),
            outlineWidth: entity.point.outlineWidth.getValue()
          };
          
          // 应用悬停效果：增大、改变颜色
          entity.point.pixelSize = 30; // 增大
          entity.point.color = Cesium.Color.CYAN; // 青色
          entity.point.outlineColor = Cesium.Color.WHITE; // 白色边框
          entity.point.outlineWidth = 4; // 更粗的边框
          
          // 改变标签颜色
          if (entity.label) {
            entity.label.fillColor = Cesium.Color.CYAN;
            entity.label.font = '20pt bold sans-serif';
          }
          
          // 改变鼠标样式
          viewer.canvas.style.cursor = 'pointer';
        }
      }
    }
    
    // 如果没有悬停测点，清除测点悬停效果
    if (!isHoveringSensor && hoveredSensorEntity) {
      restoreSensorHover(hoveredSensorEntity, hoveredSensorOriginalPoint);
      hoveredSensorEntity = null;
      hoveredSensorOriginalPoint = null;
      viewer.canvas.style.cursor = 'default';
    }
    
    // ====== 清除之前的 tileset feature 悬停高亮 ======
    if (hoveredFeature && !hoveredFeature.content.isDestroyed()) {
      hoveredFeature.color = hoveredOriginalColor;
      hoveredFeature = null;
      hoveredOriginalColor = null;
    }
    
    // ====== 如果悬停到tileset的feature上（且没有悬停测点） ======
    if (!isHoveringSensor && Cesium.defined(pickedObject) && pickedObject.primitive === tileset) {
      const pickedFeature = pickedObject;
      
      if (pickedFeature instanceof Cesium.Cesium3DTileFeature) {
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
    }
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
  
  // 恢复测点悬停效果的辅助函数
  function restoreSensorHover(entity, originalStyle) {
    if (!entity || !originalStyle) return;
    
    try {
      entity.point.pixelSize = originalStyle.pixelSize;
      entity.point.color = originalStyle.color;
      entity.point.outlineColor = originalStyle.outlineColor;
      entity.point.outlineWidth = originalStyle.outlineWidth;
      
      // 恢复标签样式
      if (entity.label) {
        entity.label.fillColor = Cesium.Color.YELLOW;
        entity.label.font = '18pt bold sans-serif';
      }
    } catch (e) {
      // 恢复失败，忽略
    }
  }
  
  // 点击选择和高亮（优先检测测点）
  handler.setInputAction((click) => {
    // 调整鼠标坐标以考虑 PageScaler 的缩放
    const adjustedPosition = getScaledPosition(click.position, viewer.canvas);
    
    // ====== 优先检测测点 ======
    const pickedObject = viewer.scene.pick(adjustedPosition);
    
    if (Cesium.defined(pickedObject)) {
      let entity = null;
      
      // 检查是否是 Entity（测点实体）
      if (pickedObject.id && pickedObject.id.sensorName) {
        entity = pickedObject.id;
      } else if (pickedObject.primitive && pickedObject.primitive.id && pickedObject.primitive.id.sensorName) {
        entity = pickedObject.primitive.id;
      }
      
      if (entity && entity.sensorName) {
        const sensorName = entity.sensorName;
        // 检查测点是否存在
        if (sensorEntities.has(sensorName)) {
          // 立即触发回调，显示弹窗（不等待飞行完成）
          if (onSensorClickCallback) {
            onSensorClickCallback(sensorName);
          }
          
          // 飞行到测点位置（可选，不影响弹窗显示）
          flyToSensor(sensorName);
          
          return;
        }
      }
    }
    
    // 如果没点击到测点，尝试使用 drillPick（穿透拾取）
    const drillPickResults = viewer.scene.drillPick(adjustedPosition || click.position);
    
    for (const result of drillPickResults) {
      let entity = null;
      
      // 检查不同可能的实体位置
      if (result.id && result.id.sensorName) {
        entity = result.id;
      } else if (result.primitive && result.primitive.id && result.primitive.id.sensorName) {
        entity = result.primitive.id;
      }
      
      if (entity && entity.sensorName) {
        const sensorName = entity.sensorName;
        if (sensorEntities.has(sensorName)) {
          // 立即触发回调，显示弹窗（不等待飞行完成）
          if (onSensorClickCallback) {
            onSensorClickCallback(sensorName);
          }
          
          // 飞行到测点位置（可选，不影响弹窗显示）
          flyToSensor(sensorName);
          
          return;
        }
      }
    }
    
    // 如果还是没找到，尝试通过实体名称查找
    if (Cesium.defined(pickedObject)) {
      const entityName = pickedObject.id?.name || pickedObject.primitive?.id?.name;
      if (entityName && sensorEntities.has(entityName)) {
        const sensorName = entityName;
        // 立即触发回调，显示弹窗（不等待飞行完成）
        if (onSensorClickCallback) {
          onSensorClickCallback(sensorName);
        }
        
        // 飞行到测点位置（可选，不影响弹窗显示）
        flyToSensor(sensorName);
        
            return;
      }
    }
    
    // ====== 回退方案：使用原有的基于 feature 属性的方法 ======
    
    // 先尝试使用 pick
    let pickedFeature = viewer.scene.pick(adjustedPosition || click.position);
    
    // 如果 pick 失败，尝试使用 drillPick 获取所有对象
    if (!Cesium.defined(pickedFeature)) {
      const drillPickResults = viewer.scene.drillPick(adjustedPosition || click.position);
      
      // 在 drillPick 结果中查找 Cesium3DTileFeature
      for (const result of drillPickResults) {
        if (result.object instanceof Cesium.Cesium3DTileFeature && result.object.primitive === tileset) {
          pickedFeature = result.object;
          break;
        }
      }
    }
    
    if (!Cesium.defined(pickedFeature)) {
      clearHighlight();
      return;
    }
    
    if (!(pickedFeature instanceof Cesium.Cesium3DTileFeature)) {
      clearHighlight();
      return;
    }
    
    if (pickedFeature.primitive !== tileset) {
      clearHighlight();
      return;
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

    // 提取节点模式并高亮所有匹配的节点
    if (featureName) {
      const nodePattern = extractNodePattern(featureName);
      if (nodePattern) {
        // 匹配到已知节点模式，高亮所有同类型节点
        highlightFeaturesByName(nodePattern);
        selectedSegmentId.value = nodePattern;
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

/**
 * 设置场景效果
 * @param {string} effectKey - 效果键名: 'antiAliasing', 'lighting', 'shadows'
 * @param {boolean} enabled - 是否启用
 */
function setEffect(effectKey, enabled) {
  if (!viewer) return
  
  switch (effectKey) {
    case 'antiAliasing':
      // 控制FXAA抗锯齿
      viewer.scene.postProcessStages.fxaa.enabled = enabled
      break
      
    case 'lighting':
      // 控制场景光照
      viewer.scene.globe.enableLighting = enabled
      // 同时控制3D Tiles的光照
      if (tileset) {
        tileset.lightingModel = enabled 
          ? Cesium.LightingModel.PBR 
          : Cesium.LightingModel.UNLIT
      }
      break
      
    case 'shadows':
      // 控制阴影
      viewer.shadows = enabled
      // 控制地球阴影
      viewer.scene.globe.shadows = enabled 
        ? Cesium.ShadowMode.RECEIVE_ONLY 
        : Cesium.ShadowMode.DISABLED
      // 控制3D Tiles阴影
      if (tileset) {
        tileset.shadows = enabled 
          ? Cesium.ShadowMode.ENABLED 
          : Cesium.ShadowMode.DISABLED
      }
      break
      
    default:
      break
  }
  
  // 请求重新渲染
  viewer.scene.requestRender()
}


// ====== 测点相关功能 ======

/**
 * 创建测点实体
 * 优先从数据库获取坐标，如果数据库中没有则使用手动配置的坐标
 */
async function createSensorEntities() {
  if (!viewer) {
    return false;
  }
  
  try {
    // 清除旧的测点实体
    sensorEntities.forEach((entity) => {
      try {
        viewer.entities.remove(entity);
      } catch (e) {
        // 移除失败，忽略
      }
    });
    sensorEntities.clear();
    
    // 前端写死，直接使用 SENSOR_POINTS 配置的坐标
    // 为每个测点创建实体
    const sensorNames = Object.keys(SENSOR_POINTS);
    
    for (const sensorName of sensorNames) {
      const coords = SENSOR_POINTS[sensorName];
      
      if (!coords || coords.length !== 3) {
        console.error(`❌ 测点 ${sensorName} 坐标格式错误:`, coords);
        continue;
      }
      
      const [lon, lat, height] = coords;
      
      try {
        // 创建测点实体（使用点或模型）
        const entity = viewer.entities.add({
          name: sensorName, // 实体名称，用于识别
          position: Cesium.Cartesian3.fromDegrees(lon, lat, height),
          point: {
            pixelSize: 20, // 增大点的大小，更明显
            color: Cesium.Color.RED, // 改为红色，更醒目
            outlineColor: Cesium.Color.YELLOW, // 黄色边框
            outlineWidth: 3, // 增大边框宽度
            heightReference: Cesium.HeightReference.NONE, // 使用绝对高度，不要贴地
            disableDepthTestDistance: Number.POSITIVE_INFINITY, // 始终显示在最前面
            scaleByDistance: new Cesium.NearFarScalar(1.5e2, 2.0, 8.0e6, 0.5) // 根据距离缩放，近距离时更大
          },
          label: {
            text: sensorName,
            font: '18pt bold sans-serif', // 增大字体，加粗
            fillColor: Cesium.Color.YELLOW, // 黄色文字，更醒目
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 3, // 增大边框
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            pixelOffset: new Cesium.Cartesian2(0, -40), // 调整位置
            disableDepthTestDistance: Number.POSITIVE_INFINITY,
            scaleByDistance: new Cesium.NearFarScalar(1.5e2, 1.5, 8.0e6, 0.5) // 标签也根据距离缩放
          },
          // 存储测点信息（重要：用于点击和悬停识别）
          sensorName: sensorName,
          sensorType: sensorName.startsWith('EX') ? 'EX' : 'IP',
          // 添加 description 以便在 InfoBox 中显示（如果需要）
          description: `测点 ${sensorName}`
        });
        
        sensorEntities.set(sensorName, entity);
      } catch (error) {
        console.error(`❌ 创建测点 ${sensorName} 失败:`, error);
      }
    }
    
    const createdCount = sensorEntities.size;
    const expectedCount = sensorNames.length;
    
    return createdCount === expectedCount;
  } catch (error) {
    console.error('❌ 创建测点实体时发生错误:', error);
    return false;
  }
}

// 测点点击回调函数（由父组件设置）
let onSensorClickCallback = null;

/**
 * 设置测点点击回调
 * @param {Function} callback - 回调函数，参数为 sensorName
 */
function setOnSensorClick(callback) {
  onSensorClickCallback = callback;
}

/**
 * 飞行到指定测点
 * @param {string} sensorName - 测点名称（如 'EX1', 'IP1'）
 * @param {Function} onComplete - 飞行完成后的回调函数
 */
async function flyToSensor(sensorName, onComplete) {
  if (!viewer) {
    // 尝试等待 viewer 初始化
    setTimeout(() => {
      if (viewer) {
        flyToSensor(sensorName, onComplete);
      }
    }, 500);
    return;
  }
  
  // 先飞到大坝视角，确保定位准确
  await new Promise((resolve) => {
    if (!tileset) {
      resolve();
      return;
    }
    
    const damViewConfig = viewConfigs['damView'] || viewConfigs['frontendView'];
    const offset = new Cesium.HeadingPitchRange(
      Cesium.Math.toRadians(damViewConfig.heading),
      Cesium.Math.toRadians(damViewConfig.pitch),
      damViewConfig.range
    );
    
    // 使用 flyToBoundingSphere 飞行到大坝视角
    viewer.camera.flyToBoundingSphere(tileset.boundingSphere, {
      offset,
      duration: damViewConfig.duration || 1.0,
      complete: () => {
        // 等待一小段时间，确保视角稳定
        setTimeout(resolve, 200);
      }
    });
  });
  
  // 如果测点不存在，立即尝试创建
  if (!sensorEntities.has(sensorName)) {
    // 立即尝试创建测点实体（异步创建）
    const success = await createSensorEntities();
    
    if (!success) {
      return;
    }
    
    // 再次检查
    if (!sensorEntities.has(sensorName)) {
      // 如果配置中存在但创建失败，尝试单独创建这个测点
      if (SENSOR_POINTS[sensorName]) {
        const coords = SENSOR_POINTS[sensorName];
        
        if (coords && coords.length === 3) {
          try {
            const [lon, lat, height] = coords;
            const entity = viewer.entities.add({
              name: sensorName,
              position: Cesium.Cartesian3.fromDegrees(lon, lat, height),
              point: {
                pixelSize: 20,
                color: Cesium.Color.RED,
                outlineColor: Cesium.Color.YELLOW,
                outlineWidth: 3,
                heightReference: Cesium.HeightReference.NONE,
                disableDepthTestDistance: Number.POSITIVE_INFINITY,
                scaleByDistance: new Cesium.NearFarScalar(1.5e2, 2.0, 8.0e6, 0.5)
              },
              label: {
                text: sensorName,
                font: '18pt bold sans-serif',
                fillColor: Cesium.Color.YELLOW,
                outlineColor: Cesium.Color.BLACK,
                outlineWidth: 3,
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                pixelOffset: new Cesium.Cartesian2(0, -40),
                disableDepthTestDistance: Number.POSITIVE_INFINITY,
                scaleByDistance: new Cesium.NearFarScalar(1.5e2, 1.5, 8.0e6, 0.5)
              },
              sensorName: sensorName,
              sensorType: sensorName.startsWith('EX') ? 'EX' : 'IP'
            });
            sensorEntities.set(sensorName, entity);
          } catch (error) {
            return;
          }
        } else {
          return;
        }
      } else {
        return;
      }
    }
  }
  
  const entity = sensorEntities.get(sensorName);
  const position = entity.position.getValue();
  
  // 飞行到测点位置，使用合适的观察距离和角度
  // 由于先回到大坝视角，现在使用固定的大坝视角朝向计算偏移
  const damViewConfig = viewConfigs['damView'] || viewConfigs['frontendView'];
  const damHeading = damViewConfig.heading; // 度（约-75度，东北方向）
  const headingRad = Cesium.Math.toRadians(damHeading);
  
  // 使用基于大坝视角的固定偏移方向
  // 创建一个朝向东北方向的偏移向量（基于大坝视角的朝向）
  // 转换到测点的局部坐标系
  const cartographic = Cesium.Cartographic.fromCartesian(position);
  
  // 使用 East-North-Up 坐标系来计算偏移
  // 在测点位置创建 ENU 坐标系
  const transform = Cesium.Transforms.eastNorthUpToFixedFrame(position);
  
  // 在 ENU 坐标系中定义偏移（前方150米，高度50米）
  // 前方 = 北方向，右侧 = 东方向
  const localOffset = new Cesium.Cartesian3(
    -150 * Math.sin(headingRad), // 东向偏移
    -150 * Math.cos(headingRad), // 北向偏移（前方）
    50 // 高度偏移50米
  );
  
  // 将局部偏移转换为世界坐标
  const offset = Cesium.Matrix4.multiplyByPointAsVector(
    transform,
    localOffset,
    new Cesium.Cartesian3()
  );
  
  const destination = Cesium.Cartesian3.add(position, offset, new Cesium.Cartesian3());
  
  // 飞行到测点位置
  viewer.camera.flyTo({
    destination: destination,
    orientation: {
      heading: headingRad, // 使用大坝视角的朝向
      pitch: Cesium.Math.toRadians(-30), // 向下30度角
      roll: 0.0
    },
    duration: 1.5, // 飞行时间1.5秒
    complete: () => {
      if (onComplete) {
        onComplete();
      }
    }
  });
}

/**
 * 获取测点信息（供弹窗使用）
 * @param {string} sensorName - 测点名称
 * @returns {Object|null} 测点信息
 */
function getSensorInfo(sensorName) {
  if (!sensorEntities.has(sensorName)) {
    return null;
  }
  
  const entity = sensorEntities.get(sensorName);
  const position = entity.position.getValue();
  const cartographic = Cesium.Cartographic.fromCartesian(position);
  
  return {
    name: sensorName,
    type: entity.sensorType,
    position: {
      lon: Cesium.Math.toDegrees(cartographic.longitude),
      lat: Cesium.Math.toDegrees(cartographic.latitude),
      height: cartographic.height
    },
    entity: entity
  };
}

/**
 * 获取所有测点实体（用于调试和外部访问）
 */
function getSensorEntities() {
  return sensorEntities;
}

/**
 * 获取测点坐标（用于调试）
 */
function getSensorCoordinates(sensorName) {
  if (!sensorEntities.has(sensorName)) {
    return null;
  }
  
  const entity = sensorEntities.get(sensorName);
  const position = entity.position.getValue(viewer.clock.currentTime);
  const cartographic = Cesium.Cartographic.fromCartesian(position);
  
  return {
    longitude: Cesium.Math.toDegrees(cartographic.longitude),
    latitude: Cesium.Math.toDegrees(cartographic.latitude),
    height: cartographic.height
  };
}

/**
 * 更新测点坐标（用于调试和调整）
 */
function updateSensorCoordinates(sensorName, lon, lat, height) {
  if (!sensorEntities.has(sensorName)) {
    console.error(`测点 ${sensorName} 不存在，无法更新坐标`);
    return false;
  }
  
  const entity = sensorEntities.get(sensorName);
  entity.position = Cesium.Cartesian3.fromDegrees(lon, lat, height);
  
  // 同时更新配置中的坐标
  if (SENSOR_POINTS[sensorName]) {
    SENSOR_POINTS[sensorName] = [lon, lat, height];
  }
  
  return true;
}

/**
 * 打印所有测点的当前坐标（用于调试）
 */
function printAllSensorCoordinates() {
  // 静默模式：不输出到控制台
}

// 暴露方法供父组件调用
defineExpose({
  switchView,
  highlightSegment,
  highlightFeaturesByName,
  clearHighlight,
  setEffect,
  // 测点相关 API
  createSensorEntities,
  flyToSensor,
  getSensorInfo,
  setOnSensorClick,
  getSensorEntities,
  // 测点坐标调试工具
  getSensorCoordinates,
  updateSensorCoordinates,
  printAllSensorCoordinates,
  // 暴露 viewer 供外部使用（如坐标拾取工具）
  getViewer: () => viewer
})

onMounted(async () => {
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxMTQ0YmFjOC00Y2FkLTRhYmYtODE3OS02ZjUzZTFhZjdmNzAiLCJpZCI6MzY4NjA1LCJpYXQiOjE3NjgxMTMwMTN9.LZFnwANyd7o3LPJzEx31hzPHU7P4fznLO3DHbWhXAG8';
  window.CESIUM_BASE_URL = '/Cesium-1.136/Build/Cesium/';
  
  // 将 Cesium 暴露到全局，方便在控制台使用
  if (typeof window !== 'undefined') {
    window.Cesium = Cesium;
  }

  viewer = new Cesium.Viewer('cesiumContainer', {
    animation: false,
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

  // 初始化效果设置（默认全部开启）
  viewer.scene.postProcessStages.fxaa.enabled = true
  viewer.scene.globe.enableLighting = true
  viewer.shadows = true
  viewer.scene.globe.shadows = Cesium.ShadowMode.RECEIVE_ONLY

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
      await Cesium.Cesium3DTileset.fromIonAssetId(4344905)
    );
    await tilesetLoaded.readyPromise;
    tileset = tilesetLoaded;
    
    // 应用默认效果设置到tileset
    tileset.lightingModel = Cesium.LightingModel.PBR
    tileset.shadows = Cesium.ShadowMode.ENABLED

    // 等待tileset完全加载后再进行交互设置
    // 当tileset加载新tiles时，重新检查并高亮待高亮的节点
    tileset.loadProgress.addEventListener((numberOfPendingRequests, numberOfTilesProcessing) => {
      if (numberOfPendingRequests === 0 && numberOfTilesProcessing === 0) {
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
    
    // ====== 创建测点实体 ======
    // 延迟创建，确保 viewer 完全初始化
    // 使用多次尝试，确保创建成功
    let retryCount = 0;
    const maxRetries = 10; // 增加重试次数
    
    async function tryCreateSensorEntities() {
      if (!viewer) {
        if (retryCount < maxRetries) {
          retryCount++;
          setTimeout(tryCreateSensorEntities, 200 * retryCount);
        }
        return;
      }
      
      if (retryCount >= maxRetries) {
        return;
      }
      
      retryCount++;
      const success = await createSensorEntities().catch(() => false);
      
      if (!success && retryCount < maxRetries) {
        setTimeout(tryCreateSensorEntities, 300 * retryCount);
      }
    }
    
    // 立即尝试一次，如果失败再延迟重试
    tryCreateSensorEntities();
    
    // ====== 添加水流水面（Polygon） ======
    const absImgUrl = window.location.origin + '/images/water.png';
    
    // ====== 定义河道边界坐标 ======
    // 格式：[[经度, 纬度, 高度], [经度, 纬度, 高度], ...]
    // 注意：坐标需要形成一个闭合的多边形（Cesium会自动闭合）
    // 坐标顺序：从右边界起点开始，沿右边界到终点，然后从左边界终点回到起点
    const waterSurfaceCoordinates = [
      // 右边界（从起点到终点）
      [111.1611255078, 30.7998018654, 50],  // 右边界起点
      [111.1510577916, 30.7872068707, 50],
      [111.1505675495, 30.7841582229, 50],
      [111.1540927102, 30.7822404905, 50],
      [111.1606321499, 30.7813647036, 50],
      [111.1709943142, 30.7787375102, 50],
      [111.1814807708, 30.7759647859, 50],
      [111.1935162126, 30.7758822443, 50],
      [111.1977279944, 30.7764112219, 50],
      [111.2018328346, 30.7762496808, 50],  // 右边界终点
      // 左边界（从终点回到起点）
      [111.2018338377, 30.7717919762, 50],  // 左边界终点
      [111.1856378511, 30.7718442219, 50],
      [111.1583704357, 30.7777563493, 50],
      [111.150312945, 30.7790038358, 50],
      [111.1473183744, 30.779301379, 50],
      [111.147525973, 30.7806464044, 50],
      [111.1463396643, 30.7828613008, 50],
      [111.1457964188, 30.7847975111, 50],
      [111.1456768505, 30.7853284603, 50],
      [111.1472209502, 30.788344879, 50],
      [111.1517674375, 30.7945010218, 50],
      [111.1572328195, 30.800563853, 50],
      [111.1613832981, 30.8048071874, 50]   // 左边界起点（回到起点，形成闭合）
    ];
    
    // ====== 创建水流水面材质（带流动动画效果） ======
    // 使用自定义的 WaterFlowMaterialProperty 实现流动效果
    const waterMaterial = new WaterFlowMaterialProperty({
      waterImage: absImgUrl,
      color: new Cesium.Color(0.2, 0.5, 1.0, 0.7), // 水的颜色（蓝色，带透明度）
      speed: 0.3, // 流动速度（0-1之间，值越大流动越快，建议 0.2-0.5）
      direction: 1.0, // 流动方向（1.0 为正向流动，-1.0 为反向流动）
      repeat: new Cesium.Cartesian2(15.0, 1.0), // 纹理重复次数（横向15次，纵向1次）
      duration: 10000 // 循环周期（毫秒），10秒一个循环，实现无缝循环播放
    });
    
    // 创建水面Polygon
    viewer.entities.add({
      name: '河道水面',
      polygon: {
        hierarchy: Cesium.Cartesian3.fromDegreesArrayHeights(
          waterSurfaceCoordinates.flatMap(coord => [coord[0], coord[1], coord[2]])
        ),
        material: waterMaterial,
        perPositionHeight: true, // 使用每个坐标点的高度
        extrudedHeight: 0, // 不拉伸，只是表面
        outline: false, // 不显示轮廓线
        closeTop: true,
        closeBottom: false,
        // 确保水面在模型上方显示
        heightReference: Cesium.HeightReference.NONE
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
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
}
/* 视角按钮按钮样式 - 隐藏，因为现在使用右侧面板 */
.view-controls {
  display: none;
}
</style>
