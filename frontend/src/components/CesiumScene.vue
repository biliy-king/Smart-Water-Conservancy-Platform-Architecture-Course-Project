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

// ====== 蒙版热区系统配置 ======
// 蒙版模式配置
const maskConfig = {
  enabled: false, // 是否启用蒙版模式
  debugMode: false, // 调试模式：显示热区边界
  totalSegments: 11, // 总段数：0-10，共11段
  maskEntities: [], // 存储所有蒙版热区实体
  segmentBounds: [] // 每个坝段的边界定义（世界坐标，格式：[[lon, lat, height], ...]）
};

// ====== 坝段坐标配置 ======
// 在这里填写你收集到的11个坝段的坐标
// 格式：每个坝段是一个数组，包含该坝段多边形的所有顶点坐标
// 坐标格式：[经度, 纬度, 高度(米)]
const DAM_SEGMENT_BOUNDS = [
  // 坝段 1 - 在这里填写你收集的第一个坝段的坐标
[
  [
    111.17001236917547,
    30.779504266712912,
    369.2842459462626
  ],
  [
    111.17021169945275,
    30.78017845134495,
    378.62551687288163
  ],
  [
    111.17030766173623,
    30.78032666977605,
    374.6889016357971
  ],
  [
    111.16997510054627,
    30.779453716632243,
    373.2496895349435
  ],
  [
    111.17107670576118,
    30.77913685653775,
    272.77259955700805
  ],
  [
    111.17103781996423,
    30.779812178468518,
    247.1659558147235
  ],
  [
    111.17326423398401,
    30.781588362311552,
    328.2081467023148
  ],
  [
    111.17335909124736,
    30.780397140032136,
    257.4144287410021
  ]
],
  
  // 坝段 2 - 在这里填写你收集的第二个坝段的坐标
[
  [
    111.1700880337252,
    30.779459908304045,
    352.0670333694621
  ],
  [
    111.17000152377128,
    30.778855854259593,
    327.4333049102834
  ],
  [
    111.17051670441161,
    30.778728291970392,
    314.293423076755
  ],
  [
    111.1708086125266,
    30.779248409765895,
    244.1703121457487
  ],
  [
    111.17061982486165,
    30.779418315571437,
    279.03353950973093
  ],
  [
    111.17031219918772,
    30.778798182157846,
    315.4071786660563
  ],
  [
    111.17265368618297,
    30.779266715092504,
    145.7037893001117
  ],
  [
    111.17269171229114,
    30.780232253367206,
    226.74072026462386
  ]
],
  
  // 坝段 3 - 在这里填写你收集的第三个坝段的坐标
[
  [
    111.17044018373564,
    30.777533218034577,
    188.8303692683544
  ],
  [
    111.1698678874437,
    30.777480398186277,
    264.47172724013967
  ],
  [
    111.16956956570121,
    30.778113000673102,
    482.88682061400317
  ],
  [
    111.16983767669645,
    30.778718988461918,
    482.9364243171147
  ],
  [
    111.16941383578441,
    30.77815991003847,
    483.7106876676841
  ],
  [
    111.1700563780006,
    30.778680493239367,
    439.35768996365886
  ],
  [
    111.17197367631564,
    30.77883853626387,
    194.65156679065828
  ],
  [
    111.17220746581701,
    30.77903202680515,
    178.68359811898694
  ]
],
// 坝段 4 - 在这里填写你收集的第四个坝段的坐标
[
  [
    111.17032070514001,
    30.77738253273332,
    192.90587252387797
  ],
  [
    111.16982974720024,
    30.77796233065352,
    343.56845425028456
  ],
  [
    111.16952685472174,
    30.77755434623121,
    362.73855364978243
  ],
  [
    111.16956829667085,
    30.77715916307652,
    315.4284660561508
  ],
  [
    111.16934143023154,
    30.7779598762176,
    483.6555673017373
  ],
  [
    111.16960296270734,
    30.778487194774865,
    483.54392957418605
  ],
  [
    111.16990654086646,
    30.779223115227325,
    483.7007490825225
  ],
  [
    111.1702702126877,
    30.7799337357574,
    483.4463830042477
  ]
],
// 坝段 5 - 在这里填写你收集的第五个坝段的坐标
[
  [
    111.17032070514001,
    30.77738253273332,
    192.90587252387797
  ],
  [
    111.16982974720024,
    30.77796233065352,
    343.56845425028456
  ],
  [
    111.16952685472174,
    30.77755434623121,
    362.73855364978243
  ],
  [
    111.16956829667085,
    30.77715916307652,
    315.4284660561508
  ],
  [
    111.16934143023154,
    30.7779598762176,
    483.6555673017373
  ],
  [
    111.16960296270734,
    30.778487194774865,
    483.54392957418605
  ],
  [
    111.16990654086646,
    30.779223115227325,
    483.7007490825225
  ],
  [
    111.1702702126877,
    30.7799337357574,
    483.4463830042477
  ]
],
// 坝段 6 - 在这里填写你收集的第六个坝段的坐标
[
  [
    111.16932111433263,
    30.780201704569894,
    360.66062318036234
  ],
  [
    111.16909823171807,
    30.77967830153175,
    380.99005478974715
  ],
  [
    111.16972491184653,
    30.779289081122343,
    484.8501838979363
  ],
  [
    111.1696030953395,
    30.77988223907017,
    512.2697979207707
  ],
  [
    111.16988494600056,
    30.779340120655696,
    484.16949766013727
  ],
  [
    111.16996004109953,
    30.779842062067768,
    517.3236981655247
  ],
  [
    111.16856989533835,
    30.777706081683984,
    486.94254330295945
  ],
  [
    111.16866219171943,
    30.776937787848997,
    484.8786391241878
  ]
],
// 坝段 7 - 在这里填写你收集的第七个坝段的坐标
[
  [
    111.16740532431214,
    30.774851733622942,
    442.73540749784894
  ],
  [
    111.16082712309276,
    30.77883261882431,
    39.20477347798067
  ],
  [
    111.16091989788193,
    30.77764999298904,
    74.3738029304647
  ],
  [
    111.16714432577328,
    30.77445015881626,
    486.68793226295696
  ],
  [
    111.16234665464455,
    30.780366589326196,
    39.32949365324676
  ],
  [
    111.16237146437906,
    30.78160424859138,
    39.277224818972016
  ],
  [
    111.16876522030185,
    30.78113350537757,
    172.51055533302417
  ],
  [
    111.16857329272713,
    30.781375611697925,
    201.47708055560102
  ]
],
// 坝段 8 - 在这里填写你收集的第八个坝段的坐标
[
  [
    111.16621721733165,
    30.772200989534177,
    481.8086213768657
  ],
  [
    111.16674090046631,
    30.773284704469933,
    430.3096740728344
  ],
  [
    111.16396491104534,
    30.77512031426115,
    313.1883907430809
  ],
  [
    111.16439573695591,
    30.775328246878555,
    287.3817375562986
  ],
  [
    111.16417523601328,
    30.775404712787743,
    291.40039984468035
  ],
  [
    111.16413160065326,
    30.77459073600922,
    335.6191731683368
  ],
  [
    111.16795281329642,
    30.77848704699561,
    39.203591529355386
  ],
  [
    111.1684101331598,
    30.778736034749972,
    160.96585643970278
  ]
],
// 坝段 9 - 在这里填写你收集的第九个坝段的坐标
[
  [
    111.16667399782507,
    30.778530884777524,
    39.31836139950626
  ],
  [
    111.16597777569311,
    30.780231514915492,
    59.7008954773248
  ],
  [
    111.16644148797093,
    30.7783077119839,
    39.093951356031724
  ],
  [
    111.1660474125307,
    30.77949918968594,
    39.212308234093044
  ],
  [
    111.16529285486035,
    30.778868634636357,
    39.31941804949036
  ],
  [
    111.16740407477948,
    30.779061478020086,
    39.294159814875016
  ],
  [
    111.168372747005,
    30.778959234694586,
    39.31453908013205
  ],
  [
    111.16772852024482,
    30.777851331932325,
    39.20970632836639
  ]
],
// 坝段 10 - 在这里填写你收集的第十个坝段的坐标
[
  [
    111.16611164179854,
    30.772449104050164,
    487.4484700727728
  ],
  [
    111.164296106524,
    30.78159172647131,
    132.4143339782431
  ],
  [
    111.16364492807398,
    30.781773819256784,
    142.56179501249088
  ],
  [
    111.1638650252355,
    30.7800391346784,
    39.53039439876928
  ],
  [
    111.1631239101169,
    30.780230091917204,
    49.948255703896166
  ],
  [
    111.16589382667075,
    30.77961504847768,
    39.062671201288055
  ]
]

];

// 是否自动应用蒙版配置（如果 DAM_SEGMENT_BOUNDS 有数据）
const AUTO_APPLY_MASK_CONFIG = false; // 设置为 false，关闭蒙版功能

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
      console.warn('恢复测点悬停效果失败:', e);
    }
  }
  
  // 点击选择和高亮（优先检测测点，然后检测蒙版热区）
  handler.setInputAction((click) => {
    // 调整鼠标坐标以考虑 PageScaler 的缩放
    const adjustedPosition = getScaledPosition(click.position, viewer.canvas);
    console.log('点击事件触发，原始位置:', click.position, '调整后位置:', adjustedPosition);
    
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
          console.log(`✅ 点击测点: ${sensorName}`);
          
          // 飞行到测点位置
          flyToSensor(sensorName, () => {
            // 飞行完成后触发回调，显示弹窗
            if (onSensorClickCallback) {
              onSensorClickCallback(sensorName);
            }
          });
          
          return;
        } else {
          console.warn(`⚠️ 点击的测点 ${sensorName} 不在 sensorEntities 中`);
          console.log('当前 sensorEntities 中的测点:', Array.from(sensorEntities.keys()));
        }
      }
    }
    
    // 如果没点击到测点，尝试使用 drillPick（穿透拾取）
    const drillPickResults = viewer.scene.drillPick(adjustedPosition || click.position);
    console.log('drillPick 结果数量:', drillPickResults.length);
    
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
          console.log(`✅ 通过 drillPick 检测到测点: ${sensorName}`);
          
          flyToSensor(sensorName, () => {
            // 飞行完成后触发回调，显示弹窗
            if (onSensorClickCallback) {
              onSensorClickCallback(sensorName);
            }
          });
          
          return;
        }
      }
    }
    
    // 如果还是没找到，尝试通过实体名称查找
    if (Cesium.defined(pickedObject)) {
      const entityName = pickedObject.id?.name || pickedObject.primitive?.id?.name;
      if (entityName && sensorEntities.has(entityName)) {
        const sensorName = entityName;
        console.log(`✅ 通过实体名称检测到测点: ${sensorName}`);
        
        flyToSensor(sensorName, () => {
          if (onSensorClickCallback) {
            onSensorClickCallback(sensorName);
          }
        });
        
        return;
      }
    }
    
    // ====== 检测蒙版热区 ======
    if (maskConfig.enabled && maskConfig.maskEntities.length > 0) {
      const pickedObject = viewer.scene.pick(adjustedPosition || click.position);
      
      // 检查是否点击到了蒙版热区
      if (Cesium.defined(pickedObject) && pickedObject.id) {
        const entity = pickedObject.id;
        
        // 检查是否是蒙版热区实体
        if (maskConfig.maskEntities.includes(entity) && entity.segmentIndex !== undefined) {
          const segmentIndex = entity.segmentIndex;
          console.log(`点击蒙版热区：坝段 ${segmentIndex}`);
          
          // 高亮对应的坝段（通过名称高亮）
          if (segmentIndex >= 0 && segmentIndex < maskConfig.totalSegments) {
            highlightFeaturesByName(`segment_${segmentIndex + 1}`);
            selectedSegmentId.value = `segment_${segmentIndex}`;
            return;
          }
        }
      }
      
      // 如果启用了蒙版但没点击到热区，尝试使用 drillPick
      const drillPickResults = viewer.scene.drillPick(adjustedPosition || click.position);
      for (const result of drillPickResults) {
        if (result.id && maskConfig.maskEntities.includes(result.id)) {
          const entity = result.id;
          if (entity.segmentIndex !== undefined) {
            const segmentIndex = entity.segmentIndex;
            console.log(`通过 drillPick 检测到蒙版热区：坝段 ${segmentIndex}`);
            if (segmentIndex >= 0 && segmentIndex < maskConfig.totalSegments) {
              highlightFeaturesByName(`segment_${segmentIndex + 1}`);
              selectedSegmentId.value = `segment_${segmentIndex}`;
              return;
            }
          }
        }
      }
    }
    
    // ====== 回退方案：使用原有的基于 feature 属性的方法 ======
    
    // 先尝试使用 pick
    let pickedFeature = viewer.scene.pick(adjustedPosition || click.position);
    console.log('pick 结果:', pickedFeature);
    
    // 如果 pick 失败，尝试使用 drillPick 获取所有对象
    if (!Cesium.defined(pickedFeature)) {
      console.log('pick 未选中对象，尝试使用 drillPick...');
      const drillPickResults = viewer.scene.drillPick(adjustedPosition || click.position);
      console.log('drillPick 结果数量:', drillPickResults.length);
      
      // 在 drillPick 结果中查找 Cesium3DTileFeature
      for (const result of drillPickResults) {
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
      console.log('抗锯齿:', enabled ? '开启' : '关闭')
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
      console.log('光效:', enabled ? '开启' : '关闭')
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
      console.log('阴影:', enabled ? '开启' : '关闭')
      break
      
    default:
      console.warn('未知的效果类型:', effectKey)
  }
  
  // 请求重新渲染
  viewer.scene.requestRender()
}


// ====== 蒙版热区系统实现 ======

/**
 * 清除所有蒙版热区
 */
function clearMaskEntities() {
  if (!viewer) return;
  
  maskConfig.maskEntities.forEach(entity => {
    viewer.entities.remove(entity);
  });
  maskConfig.maskEntities = [];
  console.log('已清除所有蒙版热区');
}

/**
 * 根据手动配置创建蒙版热区
 * @param {Array} boundsConfig - 边界配置数组，每个元素是一个坝段的边界坐标
 * 格式：[
 *   [[lon1, lat1, height1], [lon2, lat2, height2], ...], // 坝段0
 *   [[lon1, lat1, height1], [lon2, lat2, height2], ...], // 坝段1
 *   ...
 * ]
 */
function createMaskEntitiesFromConfig(boundsConfig) {
  if (!viewer || !boundsConfig || boundsConfig.length === 0) {
    console.warn('无法创建蒙版热区：配置为空');
    return;
  }

  // 清除旧的蒙版
  clearMaskEntities();

  // 为每个坝段创建热区
  boundsConfig.forEach((bounds, segmentIndex) => {
    if (!bounds || bounds.length < 3) {
      console.warn(`坝段 ${segmentIndex} 的边界配置无效，跳过`);
      return;
    }

    // 创建不可见的多边形作为热区
    const entity = viewer.entities.add({
      name: `dam_segment_${segmentIndex}`,
      polygon: {
        hierarchy: Cesium.Cartesian3.fromDegreesArrayHeights(
          bounds.flatMap(coord => [coord[0], coord[1], coord[2] || 0])
        ),
        material: maskConfig.debugMode 
          ? Cesium.Color.RED.withAlpha(0.3) // 调试模式：显示红色半透明
          : Cesium.Color.TRANSPARENT, // 正常模式：完全透明
        outline: maskConfig.debugMode, // 调试模式：显示轮廓
        outlineColor: maskConfig.debugMode ? Cesium.Color.RED : Cesium.Color.TRANSPARENT,
        height: 0,
        extrudedHeight: 0,
        perPositionHeight: true, // 使用每个坐标点的高度
        // 设置拾取优先级，确保蒙版可以被点击
        classificationType: Cesium.ClassificationType.BOTH
      },
      // 存储分段索引，用于点击时识别
      segmentIndex: segmentIndex
    });

    maskConfig.maskEntities.push(entity);
    console.log(`创建坝段 ${segmentIndex} 的蒙版热区，包含 ${bounds.length} 个顶点`);
  });

  console.log(`成功创建 ${maskConfig.maskEntities.length} 个蒙版热区`);
}


/**
 * 设置蒙版配置（供外部调用）
 * @param {Object} config - 配置对象
 * @param {boolean} config.enabled - 是否启用蒙版模式
 * @param {boolean} config.debugMode - 是否显示热区边界（调试用）
 * @param {Array} config.segmentBounds - 手动定义的坝段边界坐标数组
 * @param {number} config.totalSegments - 总段数（默认11）
 */
function setMaskConfig(config) {
  if (config.enabled !== undefined) {
    maskConfig.enabled = config.enabled;
    console.log(`蒙版模式: ${config.enabled ? '启用' : '禁用'}`);
  }
  
  if (config.debugMode !== undefined) {
    maskConfig.debugMode = config.debugMode;
    console.log(`蒙版调试模式: ${config.debugMode ? '开启' : '关闭'}`);
    
    // 更新现有热区的显示状态
    maskConfig.maskEntities.forEach(entity => {
      if (entity.polygon) {
        entity.polygon.material = maskConfig.debugMode 
          ? Cesium.Color.RED.withAlpha(0.3)
          : Cesium.Color.TRANSPARENT;
        entity.polygon.outline = maskConfig.debugMode;
        entity.polygon.outlineColor = maskConfig.debugMode 
          ? Cesium.Color.RED 
          : Cesium.Color.TRANSPARENT;
      }
    });
    viewer.scene.requestRender();
  }
  
  if (config.totalSegments !== undefined) {
    maskConfig.totalSegments = config.totalSegments;
    console.log(`蒙版总段数设置为: ${maskConfig.totalSegments}`);
  }
  
  if (config.segmentBounds && config.segmentBounds.length > 0) {
    maskConfig.segmentBounds = config.segmentBounds;
    createMaskEntitiesFromConfig(config.segmentBounds);
  } else if (config.enabled && maskConfig.maskEntities.length === 0) {
    console.warn('未提供手动配置，无法创建蒙版热区。请提供 segmentBounds 配置。');
  }
}

// ====== 测点相关功能 ======

/**
 * 创建测点实体
 * 优先从数据库获取坐标，如果数据库中没有则使用手动配置的坐标
 */
async function createSensorEntities() {
  if (!viewer) {
    console.warn('⚠️ viewer 未初始化，无法创建测点实体');
    return false;
  }
  
  try {
    // 清除旧的测点实体
    sensorEntities.forEach((entity) => {
      try {
        viewer.entities.remove(entity);
      } catch (e) {
        console.warn('移除旧测点实体失败:', e);
      }
    });
    sensorEntities.clear();
    
    // 前端写死，直接使用 SENSOR_POINTS 配置的坐标
    // 为每个测点创建实体
    const sensorNames = Object.keys(SENSOR_POINTS);
    console.log(`📝 开始创建 ${sensorNames.length} 个测点实体（前端写死）...`);
    
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
        console.log(`✅ 创建测点实体: ${sensorName} 位置: [${lon.toFixed(6)}, ${lat.toFixed(6)}, ${height.toFixed(2)}]`);
      } catch (error) {
        console.error(`❌ 创建测点 ${sensorName} 失败:`, error);
      }
    }
    
    const createdCount = sensorEntities.size;
    const expectedCount = sensorNames.length;
    console.log(`✅ 已创建 ${createdCount}/${expectedCount} 个测点实体`);
    console.log('📋 测点列表:', Array.from(sensorEntities.keys()));
    
    if (createdCount !== expectedCount) {
      console.warn(`⚠️ 测点创建不完整！期望 ${expectedCount} 个，实际创建 ${createdCount} 个`);
    }
    
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
    console.error('❌ viewer 未初始化');
    // 尝试等待 viewer 初始化
    setTimeout(() => {
      if (viewer) {
        flyToSensor(sensorName, onComplete);
      } else {
        console.error('❌ viewer 初始化失败');
      }
    }, 500);
    return;
  }
  
  // 如果测点不存在，立即尝试创建
  if (!sensorEntities.has(sensorName)) {
    console.warn(`⚠️ 测点 ${sensorName} 不存在，立即创建...`);
    console.log('📋 当前已创建的测点:', Array.from(sensorEntities.keys()));
    console.log('📋 期望的测点列表:', Object.keys(SENSOR_POINTS));
    
    // 立即尝试创建测点实体（异步创建）
    const success = await createSensorEntities();
    
    if (!success) {
      console.error('❌ 创建测点实体失败');
      console.error('可能的原因：');
      console.error('  1. viewer 未正确初始化');
      console.error('  2. 测点坐标配置错误');
      console.error('  3. Cesium 库未加载完成');
      return;
    }
    
    // 再次检查
    if (!sensorEntities.has(sensorName)) {
      console.error(`❌ 创建后，测点 ${sensorName} 仍然不存在`);
      console.error('📋 已创建的测点:', Array.from(sensorEntities.keys()));
      console.error('📋 检查配置中是否包含该测点:', SENSOR_POINTS[sensorName] ? '✅ 存在' : '❌ 不存在');
      
      // 如果配置中存在但创建失败，尝试单独创建这个测点
      if (SENSOR_POINTS[sensorName]) {
        console.log('⚠️ 配置中存在该测点，但批量创建失败，尝试单独创建...');
        const coords = SENSOR_POINTS[sensorName];
        console.log('坐标:', coords);
        
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
            console.log(`✅ 单独创建测点 ${sensorName} 成功`);
          } catch (error) {
            console.error(`❌ 单独创建测点 ${sensorName} 失败:`, error);
            return;
          }
        } else {
          console.error('❌ 坐标格式错误');
          return;
        }
      } else {
        console.error('❌ 配置中不存在该测点');
        return;
      }
    } else {
      console.log(`✅ 创建成功，测点 ${sensorName} 现在存在`);
    }
  }
  
  const entity = sensorEntities.get(sensorName);
  const position = entity.position.getValue();
  
  // 飞行到测点位置，使用合适的观察距离和角度
  // 计算一个偏移位置（在测点前方约150米，高度约50米）
  const heading = viewer.camera.heading;
  const pitch = viewer.camera.pitch;
  
  // 创建一个从测点向前的偏移向量
  const offset = Cesium.Cartesian3.multiplyByScalar(
    Cesium.Cartesian3.normalize(
      Cesium.Cartesian3.subtract(
        viewer.camera.position,
        position,
        new Cesium.Cartesian3()
      ),
      new Cesium.Cartesian3()
    ),
    150, // 距离测点150米
    new Cesium.Cartesian3()
  );
  
  const destination = Cesium.Cartesian3.add(position, offset, new Cesium.Cartesian3());
  
  // 飞行到测点位置
  viewer.camera.flyTo({
    destination: destination,
    orientation: {
      heading: heading, // 保持当前朝向
      pitch: Cesium.Math.toRadians(-30), // 向下30度角
      roll: 0.0
    },
    duration: 2.0, // 飞行时间2秒
    complete: () => {
      if (onComplete) {
        onComplete();
      }
    }
  });
  
  console.log(`✈️ 飞行到测点: ${sensorName}`);
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
    console.warn(`测点 ${sensorName} 不存在`);
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
    console.log(`✅ 已更新测点 ${sensorName} 的坐标: [${lon}, ${lat}, ${height}]`);
    console.log('💡 提示：请将新坐标复制到代码中的 SENSOR_POINTS 配置中');
  }
  
  return true;
}

/**
 * 打印所有测点的当前坐标（用于调试）
 */
function printAllSensorCoordinates() {
  console.log('📋 所有测点的当前坐标：');
  console.log('const SENSOR_POINTS = {');
  
  Object.keys(SENSOR_POINTS).forEach(sensorName => {
    if (sensorEntities.has(sensorName)) {
      const coords = getSensorCoordinates(sensorName);
      if (coords) {
        console.log(`  ${sensorName}: [${coords.longitude.toFixed(10)}, ${coords.latitude.toFixed(10)}, ${coords.height.toFixed(2)}],`);
      }
    } else {
      const coords = SENSOR_POINTS[sensorName];
      console.log(`  ${sensorName}: [${coords[0]}, ${coords[1]}, ${coords[2]}], // ⚠️ 未创建`);
    }
  });
  
  console.log('};');
}

// 暴露方法供父组件调用
defineExpose({
  switchView,
  highlightSegment,
  highlightFeaturesByName,
  clearHighlight,
  setEffect,
  // 蒙版相关 API
  setMaskConfig,
  createMaskEntitiesFromConfig,
  clearMaskEntities,
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
    
    // ====== 创建测点实体 ======
    // 延迟创建，确保 viewer 完全初始化
    // 使用多次尝试，确保创建成功
    let retryCount = 0;
    const maxRetries = 10; // 增加重试次数
    
    async function tryCreateSensorEntities() {
      if (!viewer) {
        if (retryCount < maxRetries) {
          retryCount++;
          console.log(`⏳ viewer 未准备好，${200 * retryCount}ms 后重试 (${retryCount}/${maxRetries})...`);
          setTimeout(tryCreateSensorEntities, 200 * retryCount);
        } else {
          console.error('❌ viewer 初始化超时，无法创建测点实体');
        }
        return;
      }
      
      if (retryCount >= maxRetries) {
        console.error('❌ 多次尝试创建测点实体失败');
        return;
      }
      
      retryCount++;
      console.log(`🔄 尝试创建测点实体 (${retryCount}/${maxRetries})...`);
      const success = await createSensorEntities().catch(() => false);
      
      if (!success && retryCount < maxRetries) {
        console.log(`⏳ 测点实体创建失败，${300 * retryCount}ms 后重试...`);
        setTimeout(tryCreateSensorEntities, 300 * retryCount);
      } else if (success) {
        console.log('✅ 测点实体创建成功！');
        console.log('📋 所有测点:', Array.from(sensorEntities.keys()));
      } else {
        console.error('❌ 测点实体创建失败');
      }
    }
    
    // 立即尝试一次，如果失败再延迟重试
    tryCreateSensorEntities();
    
    // ====== 自动应用蒙版配置 ======
    // 如果配置了坐标数据且启用了自动应用，则在模型加载完成后自动创建蒙版热区
    if (AUTO_APPLY_MASK_CONFIG && DAM_SEGMENT_BOUNDS && DAM_SEGMENT_BOUNDS.length > 0) {
      // 等待一小段时间确保所有资源加载完成
      setTimeout(() => {
        setMaskConfig({
          enabled: true,
          debugMode: true, // 开启调试模式，显示红色热区（方便查看位置）
          totalSegments: DAM_SEGMENT_BOUNDS.length,
          segmentBounds: DAM_SEGMENT_BOUNDS
        });
        console.log(`✅ 已自动应用 ${DAM_SEGMENT_BOUNDS.length} 个坝段的蒙版热区配置`);
        console.log('💡 提示：如果热区位置准确，可以在代码中将 debugMode 设置为 false');
      }, 1000);
    }
    
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
    
    console.log('✅ 河道水面已创建，包含', waterSurfaceCoordinates.length, '个边界点');
    
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
