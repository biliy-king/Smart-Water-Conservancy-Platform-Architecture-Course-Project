# Smart-Water-Conservancy-Platform API 接口文档

本文档详细说明了智慧水利平台后端API的所有接口、字段定义和使用方法。

**基础URL**: `http://localhost:8000/api/`

**版本**: v1.1 (Phase 2 增强版)

**最后更新**: 2026-01-11

**认证方式**: JWT Bearer Token

---

## 📢 Phase 2 新增功能

- **P0 - 单点详情增强** ✅ 
  - 新增 `unit` (单位)、`current_value` (当前实时值)、`current_status` (当前状态)、`relevant_thresholds` (关联阈值)、`last_update_time` (最后更新时间)
  - 端点：`GET /api/water-structures/points/{id}/`

- **P1 - 数据统计分析** ✅ 
  - 新增 `/api/monitoring/statistics/` 聚合端点
  - 返回：总监测点数、状态分布、设备类型分布

- **P2 - 阈值管理API** ✅ 
  - 新增 `/api/water-structures/points/{id}/thresholds/` 双向接口
  - 支持：GET (查看) 和 PUT (修改) 告警阈值

---

## 目录

0. [JWT 认证快速开始](#0-jwt-认证快速开始)
1. [用户认证接口](#1-用户认证接口)
2. [大坝信息接口](#2-大坝信息接口)
3. [监测设备接口](#3-监测设备接口)
4. [监测点接口](#4-监测点接口)
   - 4.1 [列表接口](#41-获取监测点列表)
   - 4.2 [详情接口（增强版）](#42-获取单个监测点详情p0增强)
   - 4.3 [阈值管理接口](#43-监测点阈值管理p2)
5. [监测数据接口](#5-监测数据接口)
6. [数据统计接口](#6-数据统计接口p1增强)
7. [用户信息接口](#7-用户信息接口)
8. [权限说明](#8-权限说明)
9. [数据校验规则](#9-数据校验规则)
10. [通用说明](#10-通用说明)

---

## 0. JWT 认证快速开始

### 认证流程

本平台采用 **JWT Token** 认证机制，所有API（除登录/刷新外）都需要在请求头中携带有效的 Token。

**Token有效期**：
- **access token**: 1 小时（用于访问受保护接口）
- **refresh token**: 7 天（用于刷新 access token）

### 前端集成步骤

#### 第1步：用户登录获取Token
```bash
POST /api/users/login/
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "admin",
  "password": "password123"
}
```

**成功响应 (201 Created)**：
```json
{
  "success": true,
  "message": "登录成功",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

**失败响应 (401 Unauthorized)**：
```json
{
  "success": false,
  "message": "用户名或密码错误",
  "data": null
}
```

#### 第2步：保存Token到本地存储
```javascript
// 将返回的 tokens 保存到浏览器
localStorage.setItem('access_token', response.tokens.access);
localStorage.setItem('refresh_token', response.tokens.refresh);
localStorage.setItem('user', JSON.stringify(response.user));
```

#### 第3步：在请求头中携带Token
```javascript
// 所有API请求都需要在请求头中加入 Authorization
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json'
};

// 示例：获取大坝列表
fetch('/api/water-structures/structures/', {
  method: 'GET',
  headers: headers
});
```

#### 第4步：处理Token过期（401错误）
当 access token 过期时，API会返回 401，此时需要调用刷新接口：
```bash
POST /api/users/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**成功响应 (200 OK)**：
```json
{
  "success": true,
  "message": "Token刷新成功",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

更新本地Token后重新发送原请求。

### Axios 自动化示例

推荐使用Axios的拦截器自动处理Token刷新：

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器：自动添加Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理401并自动刷新Token
api.interceptors.response.use(
  response => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post('/api/users/refresh/', {
          refresh: refreshToken
        });
        
        // 更新Token
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        
        // 更新请求头
        originalRequest.headers['Authorization'] = `Bearer ${data.tokens.access}`;
        
        // 重新发送原请求
        return api(originalRequest);
      } catch (err) {
        // 刷新失败，跳转登录页
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

---

## 1. 用户认证接口

### 1.1 用户登录

- **接口**: `POST /api/users/login/`
- **说明**: 用户名和密码登录，获取JWT Token
- **认证**: 无（允许匿名）
- **Content-Type**: `application/json`

**请求体**:
```json
{
  "username": "admin",
  "password": "password123"
}
```

**响应 (201 Created)**:
```json
{
  "success": true,
  "message": "登录成功",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

**错误响应 (401 Unauthorized)**:
```json
{
  "success": false,
  "message": "用户名或密码错误",
  "data": null
}
```

### 1.2 刷新Token

- **接口**: `POST /api/users/refresh/`
- **说明**: 使用 refresh token 获取新的 access token
- **认证**: 无（允许匿名）
- **Content-Type**: `application/json`

**请求体**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**响应 (200 OK)**:
```json
{
  "success": true,
  "message": "Token刷新成功",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

**错误响应 (400 Bad Request)**:
```json
{
  "success": false,
  "message": "Refresh token已过期或无效",
  "data": null
}
```

### 1.3 获取当前用户信息

- **接口**: `GET /api/users/current/`
- **说明**: 获取登录用户的完整信息
- **认证**: ✅ 需要有效Token (Authorization: Bearer <token>)
- **Method**: GET

**请求头**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**响应 (200 OK)**:
```json
{
  "success": true,
  "message": "获取用户信息成功",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "department": "技术部",
    "phone": "13800000000"
  }
}
```

**错误响应 (401 Unauthorized)**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 2. 大坝信息接口

### 2.1 获取大坝列表
- **接口**: `GET /api/water-structures/structures/`
- **说明**: 获取所有大坝信息（按创建时间倒序）
- **分页参数**: 
  - `page`: 页码（可选，默认第1页）
  - `page_size`: 每页数量（默认10条）
- **响应**: 大坝列表（分页格式）

**字段说明**:

| 字段名 | 类型 | 必填 | 含义 |
|--------|------|------|------|
| id | Integer | 自动生成 | 大坝唯一标识符，系统自动分配 |
| name | String(100) | 是 | 大坝名称，如"芹山水电站大坝" |
| cesium_center_x | Float | 是 | Cesium大坝中心点X坐标（世界坐标系），用于定位大坝在三维场景中的位置，可使用经度转换值或虚拟坐标（如1000.0） |
| cesium_center_y | Float | 是 | Cesium大坝中心点Y坐标（世界坐标系），用于定位大坝在三维场景中的位置，可使用纬度转换值或虚拟坐标（如500.0） |
| cesium_center_z | Float | 是 | Cesium大坝中心点Z坐标（高程），表示大坝基座海拔高度，单位：米（如100.0） |
| cesium_heading | Float | 否 | Cesium大坝模型航向角（绕Z轴旋转），单位：度，0表示正北方向，默认0.0 |
| cesium_pitch | Float | 否 | Cesium大坝模型俯仰角（绕X轴旋转），单位：度，0表示水平方向，默认0.0 |
| cesium_roll | Float | 否 | Cesium大坝模型翻滚角（绕Y轴旋转），单位：度，0表示水平方向，默认0.0 |
| cesium_scale | Float | 否 | Cesium大坝模型缩放比例，1.0表示原始大小，可根据场景调整，默认1.0 |
| cesium_model_url | String(500) | 否 | Cesium大坝3D模型文件路径，如"/static/models/dam.glb"，前端Cesium加载模型时使用 |
| level | String(20) | 是 | 大坝工程等级，可选值：<br>• "1级" - 一级大坝（特等、大型工程）<br>• "2级" - 二级大坝（中型工程）<br>• "3级" - 三级大坝（小型工程）<br>默认为"2级" |
| completion_time | Date | 否 | 大坝建成时间，格式：YYYY-MM-DD |
| create_time | DateTime | 自动生成 | 系统录入时间，格式：YYYY-MM-DD HH:MM:SS |

**响应示例**:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "芹山水电站大坝",
      "cesium_center_x": 1000.0,
      "cesium_center_y": 500.0,
      "cesium_center_z": 100.0,
      "cesium_heading": 0.0,
      "cesium_pitch": 0.0,
      "cesium_roll": 0.0,
      "cesium_scale": 1.0,
      "cesium_model_url": "/static/models/dam.glb",
      "level": "2级",
      "completion_time": "2010-06-15",
      "create_time": "2026-01-06T08:00:00Z"
    }
  ]
}
```

### 2.2 获取单个大坝详情
- **接口**: `GET /api/water-structures/structures/{id}/`
- **说明**: 获取指定ID的大坝详细信息
- **路径参数**: 
  - `id`: 大坝ID（必填）
- **响应**: 单个大坝完整信息（字段同上）

### 2.3 创建新大坝
- **接口**: `POST /api/water-structures/structures/`
- **说明**: 新增大坝信息
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "name": "新大坝名称",
  "cesium_center_x": 1000.0,
  "cesium_center_y": 500.0,
  "cesium_center_z": 100.0,
  "cesium_heading": 0.0,
  "cesium_pitch": 0.0,
  "cesium_roll": 0.0,
  "cesium_scale": 1.0,
  "cesium_model_url": "/static/models/dam.glb",
  "level": "2级",
  "completion_time": "2010-06-15"
}
```
- **响应**: 返回创建的大坝完整信息（包含自动生成的id和create_time）

### 2.4 更新大坝信息
- **接口**: `PUT /api/water-structures/structures/{id}/`
- **说明**: 更新指定大坝的完整信息
- **路径参数**: `id` - 大坝ID
- **请求体**: 同创建接口（需提供所有必填字段）
- **响应**: 返回更新后的大坝完整信息

### 2.5 删除大坝
- **接口**: `DELETE /api/water-structures/structures/{id}/`
- **说明**: 删除指定大坝（同时会删除关联的所有设备、监测点和监测数据）
- **路径参数**: `id` - 大坝ID
- **响应**: `204 No Content`（删除成功）

---

## 3. 监测设备接口

### 2.1 获取监测设备列表
- **接口**: `GET /api/water-structures/devices/`
- **说明**: 获取所有监测设备（按设备名称排序）
- **查询参数**: 
  - `page`: 页码（可选，默认第1页）
  - `page_size`: 每页数量（默认10条）
  - `structure`: 所属大坝ID（可选，用于筛选特定大坝的设备）
  - `device_type`: 设备类型（可选，筛选特定类型的设备）
- **响应**: 设备列表（分页格式）

**字段说明**:

| 字段名 | 类型 | 必填 | 含义 |
|--------|------|------|------|
| id | Integer | 自动生成 | 监测设备唯一标识符 |
| structure | Integer | 是 | 所属大坝的ID，外键关联Structure表 |
| device_name | String(100) | 是 | 设备名称，用于标识具体设备，如"倒垂线传感器-坝顶1#" |
| device_type | String(50) | 是 | 设备类型及监测指标，可选值：<br>• "inverted_plumb_up_down" - 倒垂线-上下游位移监测<br>• "inverted_plumb_left_right" - 倒垂线-左右岸位移监测<br>• "tension_wire_up_down" - 引张线-上下游位移监测<br>• "hydrostatic_leveling" - 静力水准-沉降监测<br>• "water_level_upstream" - 水位传感器-上游水位监测<br>• "water_level_downstream" - 水位传感器-下游水位监测 |
| install_position | String(200) | 是 | 设备安装位置详细描述，如"大坝坝顶中部"、"上游坝前20米" |
| install_time | Date | 否 | 设备安装日期，格式：YYYY-MM-DD |
| device_status | String(20) | 是 | 设备运行状态，可选值：<br>• "running" - 正常运行<br>• "maintenance" - 维护中<br>• "fault" - 故障<br>• "offline" - 离线/停用<br>默认为"running" |
| create_time | DateTime | 自动生成 | 系统录入时间，格式：YYYY-MM-DD HH:MM:SS |

**响应示例**:
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "structure": 1,
      "device_name": "倒垂线传感器-坝顶1#",
      "device_type": "inverted_plumb_up_down",
      "install_position": "大坝坝顶中部",
      "install_time": "2020-06-01",
      "device_status": "running",
      "create_time": "2026-01-06T10:00:00Z"
    },
    {
      "id": 2,
      "structure": 1,
      "device_name": "静力水准仪-坝身2#",
      "device_type": "hydrostatic_leveling",
      "install_position": "大坝坝身高程80米处",
      "install_time": "2020-06-02",
      "device_status": "running",
      "create_time": "2026-01-06T10:05:00Z"
    }
  ]
}
```

### 2.2 获取单个设备详情
- **接口**: `GET /api/water-structures/devices/{id}/`
- **说明**: 获取指定ID的设备详细信息
- **路径参数**: `id` - 设备ID
- **响应**: 单个设备完整信息

### 2.3 创建新设备
- **接口**: `POST /api/water-structures/devices/`
- **说明**: 新增监测设备
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "structure": 1,
  "device_name": "水位传感器-上游1#",
  "device_type": "water_level_upstream",
  "install_position": "上游坝前20米处",
  "install_time": "2024-01-15",
  "device_status": "running"
}
```
- **响应**: 返回创建的设备完整信息

### 2.4 更新设备信息
- **接口**: `PUT /api/water-structures/devices/{id}/`
- **说明**: 更新指定设备的完整信息
- **路径参数**: `id` - 设备ID
- **请求体**: 同创建接口
- **响应**: 返回更新后的设备完整信息

### 2.5 删除设备
- **接口**: `DELETE /api/water-structures/devices/{id}/`
- **说明**: 删除指定设备（同时会删除关联的所有监测点和监测数据）
- **路径参数**: `id` - 设备ID
- **响应**: `204 No Content`

---

## 4. 监测点接口

### 3.1 获取监测点列表
- **接口**: `GET /api/water-structures/points/`
- **说明**: 获取所有监测点（按测点编号排序），包含Cesium世界坐标系坐标
- **查询参数**: 
  - `page`: 页码（可选，默认第1页）
  - `page_size`: 每页数量（默认10条）
  - `device`: 所属设备ID（可选，筛选特定设备的监测点）
- **响应**: 监测点列表（分页格式）

**字段说明**:

| 字段名 | 类型 | 必填 | 含义 |
|--------|------|------|------|
| id | Integer | 自动生成 | 监测点唯一标识符 |
| device | Integer | 是 | 所属监测设备的ID，外键关联MonitoringDevice表 |
| device_info | Object | 只读 | 设备详细信息（嵌套对象），包含设备的所有字段，方便前端一次性获取设备信息 |
| point_code | String(50) | 是 | 监测点编号，唯一标识监测点，如"DQ-BD-001"（倒垂-坝顶-001） |
| relative_x | Float | 是 | 相对于大坝中心的X轴偏移量（米），东西方向，正值表示向东 |
| relative_y | Float | 是 | 相对于大坝中心的Y轴偏移量（米），南北方向，正值表示向北 |
| relative_z | Float | 是 | 相对于大坝中心的Z轴偏移量（米），垂直方向，正值表示向上 |
| displacement_upper | Float | 否 | 位移监测上限阈值（毫米），超过此值触发预警，用于倒垂线、引张线设备 |
| displacement_lower | Float | 否 | 位移监测下限阈值（毫米），低于此值触发预警，用于倒垂线、引张线设备 |
| settlement_upper | Float | 否 | 沉降监测上限阈值（毫米），超过此值触发预警，用于静力水准设备 |
| settlement_lower | Float | 否 | 沉降监测下限阈值（毫米），低于此值触发预警，用于静力水准设备 |
| water_level_upper | Float | 否 | 水位监测上限阈值（米），超过此值触发预警，用于水位传感器 |
| water_level_lower | Float | 否 | 水位监测下限阈值（米），低于此值触发预警，用于水位传感器 |
| create_time | DateTime | 自动生成 | 系统录入时间，格式：YYYY-MM-DD HH:MM:SS |
| cesium_world_coords | Object | 只读 | Cesium世界坐标系坐标（自动计算），包含：<br>• x - 世界坐标X值<br>• y - 世界坐标Y值<br>• z - 世界坐标Z值（高程）<br>**计算公式**: 大坝中心坐标 + 相对偏移量<br>前端Cesium可直接使用此坐标定位监测点 |

**响应示例**:
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "device": 1,
      "device_info": {
        "id": 1,
        "device_name": "倒垂线传感器-坝顶1#",
        "device_type": "inverted_plumb_up_down",
        "structure": 1,
        "install_position": "大坝坝顶中部"
      },
      "point_code": "DQ-BD-001",
      "relative_x": 10.0,
      "relative_y": 5.0,
      "relative_z": 20.0,
      "displacement_upper": 5.0,
      "displacement_lower": -5.0,
      "settlement_upper": null,
      "settlement_lower": null,
      "water_level_upper": null,
      "water_level_lower": null,
      "create_time": "2026-01-06T10:00:00Z",
      "cesium_world_coords": {
        "x": 1010.0,
        "y": 505.0,
        "z": 120.0
      }
    }
  ]
}
```

### 3.2 获取单个监测点详情（P0增强）
- **接口**: `GET /api/water-structures/points/{id}/`
- **说明**: 获取指定ID的监测点详细信息，**包含5个增强字段用于前端实时显示**
- **路径参数**: `id` - 监测点ID
- **响应**: 单个监测点完整信息（包含device_info、cesium_world_coords、**以及新增的5个实时字段**）

**🎯 P0增强 - 新增5个关键字段**：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `unit` | string | 单位（根据设备类型自动判断） | "m" (水位传感器) / "mm" (位移/沉降) |
| `current_value` | number | 当前实时值（虚拟数据，基于历史基线+波动） | 85.98 |
| `current_status` | string | 当前状态（根据current_value与阈值对比） | "normal" / "warning" / "alarm" |
| `relevant_thresholds` | object | 该设备类型对应的所有阈值 | {"min":85, "max":95, "warning":95, "critical":190} |
| `last_update_time` | string | 最后数据更新时间 (ISO 8601) | "2026-01-11T06:26:16.988608+00:00" |

**响应示例**:
```json
{
  "id": 62,
  "point_code": "DQ-WL-001",
  "device": 62,
  "device_info": {
    "id": 62,
    "device_name": "水位传感器-上游",
    "device_type": "water_level_upstream",
    "install_position": "",
    "install_time": null,
    "device_status": "running",
    "structure": 3
  },
  "cesium_world_coords": {
    "x": 985.0,
    "y": 492.0,
    "z": 100.0
  },
  "relative_x": -15.0,
  "relative_y": -8.0,
  "relative_z": 0.0,
  "water_level_upper": 95.0,
  "water_level_lower": 85.0,
  "displacement_upper": null,
  "displacement_lower": null,
  "settlement_upper": null,
  "settlement_lower": null,
  "create_time": "2026-01-11T14:17:53.717413+08:00",
  
  "unit": "m",
  "current_value": 85.98,
  "current_status": "alarm",
  "relevant_thresholds": {
    "min": 85.0,
    "max": 95.0,
    "warning": 95.0,
    "critical": 190.0
  },
  "last_update_time": "2026-01-11T06:26:16.988608+00:00"
}
```

**前端使用示例**：
```javascript
// 获取单点详情
const response = await api.get(`/water-structures/points/${pointId}/`);
const point = response.data;

// 直接使用P0增强字段显示在仪表盘
console.log(`${point.point_code}: ${point.current_value}${point.unit}`);
console.log(`状态: ${point.current_status}`);  // normal/warning/alarm
console.log(`上限: ${point.relevant_thresholds.max}${point.unit}`);
```

### 3.3 监测点阈值管理（P2）

#### 3.3.1 获取监测点阈值
- **接口**: `GET /api/water-structures/points/{id}/thresholds/`
- **说明**: 获取指定监测点的所有告警阈值配置
- **路径参数**: `id` - 监测点ID
- **权限**: 任何认证用户可查询
- **响应示例**:
```json
{
  "device_type": "water_level_upstream",
  "unit": "m",
  "water_level_upper": 95.0,
  "water_level_lower": 85.0,
  "displacement_upper": null,
  "displacement_lower": null,
  "settlement_upper": null,
  "settlement_lower": null
}
```

#### 3.3.2 修改监测点阈值
- **接口**: `PUT /api/water-structures/points/{id}/thresholds/`
- **说明**: 动态修改指定监测点的告警阈值（仅需提供要修改的字段）
- **路径参数**: `id` - 监测点ID
- **权限**: 仅 **admin** 或 **monitor** 角色可修改
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "water_level_upper": 100,
  "water_level_lower": 80
}
```

**说明**:
- 只需提供要修改的字段，其他字段保持不变
- 可同时修改多个字段
- 修改后立即生效，后续新数据使用新阈值判断状态

**响应示例**:
```json
{
  "device_type": "water_level_upstream",
  "unit": "m",
  "water_level_upper": 100.0,
  "water_level_lower": 80.0,
  "displacement_upper": null,
  "displacement_lower": null,
  "settlement_upper": null,
  "settlement_lower": null
}
```

**成功响应**: 200 OK  
**权限不足**: 403 Forbidden  
**测点不存在**: 404 Not Found

### 3.4 创建新监测点
- **接口**: `POST /api/water-structures/points/`
- **说明**: 新增监测点
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "device": 1,
  "point_code": "DQ-BD-002",
  "relative_x": 15.0,
  "relative_y": 8.0,
  "relative_z": 25.0,
  "displacement_upper": 5.0,
  "displacement_lower": -5.0
}
```

**说明**:
- `cesium_world_coords`字段会自动计算，无需手动填写
- `device_info`字段会自动关联，无需手动填写
- 根据设备类型，只需填写对应的阈值字段（如位移监测设备填写displacement_upper/lower）

- **响应**: 返回创建的监测点完整信息（包含自动计算的cesium_world_coords）

### 3.5 更新监测点信息
- **接口**: `PUT /api/water-structures/points/{id}/`
- **说明**: 更新指定监测点的完整信息
- **路径参数**: `id` - 监测点ID
- **请求体**: 同创建接口
- **响应**: 返回更新后的监测点完整信息（cesium_world_coords会自动重新计算）

### 3.6 删除监测点
- **接口**: `DELETE /api/water-structures/points/{id}/`
- **说明**: 删除指定监测点（同时会删除关联的所有监测数据）
- **路径参数**: `id` - 监测点ID
- **响应**: `204 No Content`

---

## 5. 监测数据接口

### 5.1 获取监测数据列表
- **接口**: `GET /api/monitoring/monitor-datas/`
- **说明**: 获取所有监测数据（按监测时间倒序，最新数据在前）
- **查询参数**: 
  - `page`: 页码（可选，默认第1页）
  - `page_size`: 每页数量（默认10条）
  - `point`: 监测点ID（可选，筛选特定监测点的数据）
  - `start_time`: 开始时间（可选，筛选时间范围）
  - `end_time`: 结束时间（可选，筛选时间范围）
  - `status`: 预警状态（可选，筛选特定状态的数据："normal"/"warning"/"alarm"）
- **响应**: 监测数据列表（分页格式）

**字段说明**:

| 字段名 | 类型 | 必填 | 含义 |
|--------|------|------|------|
| id | Integer | 自动生成 | 监测数据唯一标识符 |
| point | Integer | 是 | 监测点ID，外键关联Point表 |
| point_info | Object | 只读 | 监测点详细信息（嵌套对象），包含监测点的所有字段、设备信息和Cesium坐标 |
| monitor_time | DateTime | 是 | 数据采集时间，格式：YYYY-MM-DD HH:MM:SS 或 ISO 8601格式 |
| inverted_plumb_up_down | Float | 否 | 倒垂线-上下游位移监测值，单位：毫米（mm），正值表示向下游位移 |
| inverted_plumb_left_right | Float | 否 | 倒垂线-左右岸位移监测值，单位：毫米（mm），正值表示向右岸位移 |
| tension_wire_up_down | Float | 否 | 引张线-上下游位移监测值，单位：毫米（mm），正值表示向下游位移 |
| hydrostatic_leveling_settlement | Float | 否 | 静力水准-沉降监测值，单位：毫米（mm），正值表示沉降，负值表示抬升 |
| water_level_upstream | Float | 否 | 上游水位监测值，单位：米（m），表示上游水库水位高程 |
| water_level_downstream | Float | 否 | 下游水位监测值，单位：米（m），表示下游河道水位高程 |
| status | String(10) | 自动计算 | 预警状态（系统自动判断，无需手动填写），可选值：<br>• "normal" - 正常（所有监测值在安全范围内）<br>• "warning" - 预警（监测值接近阈值）<br>• "alarm" - 告警（监测值超过阈值）<br>**判断逻辑**: 系统根据监测点设置的阈值自动对比当前监测值 |
| monitor_person | String(50) | 否 | 监测人员姓名，用于记录数据采集人员 |
| remark | Text | 否 | 备注说明，用于记录特殊情况或异常信息 |
| create_time | DateTime | 自动生成 | 系统录入时间，格式：YYYY-MM-DD HH:MM:SS |

**响应示例**:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/monitoring/monitor-datas/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "point": 1,
      "point_info": {
        "id": 1,
        "point_code": "DQ-BD-001",
        "device_info": {
          "device_name": "倒垂线传感器-坝顶1#",
          "device_type": "inverted_plumb_up_down"
        },
        "cesium_world_coords": {
          "x": 1010.0,
          "y": 505.0,
          "z": 120.0
        }
      },
      "monitor_time": "2026-01-06T09:00:00Z",
      "inverted_plumb_up_down": 2.5,
      "inverted_plumb_left_right": null,
      "tension_wire_up_down": null,
      "hydrostatic_leveling_settlement": null,
      "water_level_upstream": null,
      "water_level_downstream": null,
      "status": "normal",
      "monitor_person": "张三",
      "remark": "",
      "create_time": "2026-01-06T09:05:00Z"
    }
  ]
}
```

### 5.2 获取单条监测数据
- **接口**: `GET /api/monitoring/monitor-datas/{id}/`
- **说明**: 获取指定ID的监测数据详细信息
- **路径参数**: `id` - 监测数据ID
- **响应**: 单条监测数据完整信息

### 5.3 新增监测数据
- **接口**: `POST /api/monitoring/monitor-datas/`
- **说明**: 新增一条监测数据，系统会自动判断预警状态
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "point": 1,
  "monitor_time": "2026-01-06T10:00:00Z",
  "inverted_plumb_up_down": 3.2,
  "monitor_person": "李四",
  "remark": "正常监测"
}
```

**说明**:
- `status`字段会根据监测值和阈值自动计算，无需手动填写
- `point_info`字段会自动关联，无需手动填写
- 至少填写一个监测值字段（根据设备类型选择对应字段）
- `monitor_time`可使用ISO 8601格式或"YYYY-MM-DD HH:MM:SS"格式
- 同一监测点在同一时间只能有一条数据（unique_together约束）

- **响应**: 返回完整数据，包含自动判断的`status`字段

### 5.4 更新监测数据
- **接口**: `PUT /api/monitoring/monitor-datas/{id}/`
- **说明**: 更新指定监测数据的完整信息
- **路径参数**: `id` - 监测数据ID
- **请求体**: 同新增接口
- **响应**: 返回更新后的完整数据（status会自动重新计算）

### 5.5 删除监测数据
- **接口**: `DELETE /api/monitoring/monitor-datas/{id}/`
- **说明**: 删除指定监测数据
- **路径参数**: `id` - 监测数据ID
- **响应**: `204 No Content`

### 5.6 批量新增监测数据
- **接口**: `POST /api/monitoring/monitor-datas/batch/`
- **说明**: 批量新增监测数据，适用于数据导入、历史数据补录等场景
- **Content-Type**: `application/json`
- **请求体示例**:
```json
[
  {
    "point": 1,
    "monitor_time": "2026-01-06T09:00:00Z",
    "inverted_plumb_up_down": 2.5,
    "monitor_person": "张三"
  },
  {
    "point": 1,
    "monitor_time": "2026-01-06T10:00:00Z",
    "inverted_plumb_up_down": 2.8,
    "monitor_person": "张三"
  },
  {
    "point": 2,
    "monitor_time": "2026-01-06T09:00:00Z",
    "water_level_upstream": 85.5,
    "monitor_person": "李四"
  }
]
```

**说明**:
- 请求体为监测数据对象数组，每个对象格式同单条新增接口
- 批量操作会进行事务处理，全部成功或全部回滚
- 建议单次批量操作不超过1000条数据
- 每条数据的`status`字段会自动计算
- 如遇到重复数据（同测点同时间），会返回错误信息并指明具体行号

**响应示例**:
```json
{
  "success": true,
  "created_count": 3,
  "message": "成功创建3条监测数据",
  "data": [
    {
      "id": 101,
      "point": 1,
      "monitor_time": "2026-01-06T09:00:00Z",
      "inverted_plumb_up_down": 2.5,
      "status": "normal"
    },
    // ... 其他创建的数据
  ]
}
```

**错误响应示例**:
```json
{
  "success": false,
  "error": "数据验证失败",
  "details": [
    {
      "index": 1,
      "errors": {
        "monitor_time": ["不能录入未来时间"]
      }
    },
    {
      "index": 2,
      "errors": {
        "point": ["该监测点在此时间已有数据记录"]
      }
    }
  ]
}
```

---

## 6. 数据统计接口（P1增强）

### 6.1 获取数据统计概览
- **接口**: `GET /api/monitoring/statistics/`
- **说明**: 获取系统监测数据的聚合统计，包括总监测点数、状态分布、设备类型分布等
- **权限**: 任何认证用户可访问
- **查询参数**: 无
- **响应**: 统计数据汇总

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_points` | integer | 系统中所有监测点的总数 |
| `status_distribution` | object | 按监测数据状态分布统计：<br>• `normal` - 正常状态的点数<br>• `warning` - 预警状态的点数<br>• `alarm` - 告警状态的点数 |
| `device_type_distribution` | object | 按设备类型分布统计，包含各种设备类型的点数：<br>• `water_level_upstream` - 上游水位监测点<br>• `water_level_downstream` - 下游水位监测点<br>• `inverted_plumb_up_down` - 倒垂线-上下游点<br>• `inverted_plumb_left_right` - 倒垂线-左右岸点<br>• `tension_wire_up_down` - 引张线点<br>• `hydrostatic_leveling_settlement` - 静力水准点 |
| `timestamp` | string | 统计数据时间戳 (ISO 8601) |

**响应示例**:
```json
{
  "total_points": 58,
  "status_distribution": {
    "normal": 42,
    "warning": 12,
    "alarm": 4
  },
  "device_type_distribution": {
    "water_level_upstream": 10,
    "water_level_downstream": 8,
    "inverted_plumb_up_down": 15,
    "inverted_plumb_left_right": 12,
    "tension_wire_up_down": 8,
    "hydrostatic_leveling_settlement": 5
  },
  "timestamp": "2026-01-11T06:44:03.404938+00:00"
}
```

**前端使用示例**：
```javascript
// 获取统计数据
const response = await api.get('/monitoring/statistics/');
const stats = response.data;

console.log(`总监测点数: ${stats.total_points}`);
console.log(`告警: ${stats.status_distribution.alarm}`);
console.log(`预警: ${stats.status_distribution.warning}`);
console.log(`正常: ${stats.status_distribution.normal}`);

// 用于图表展示
const statusChart = {
  xAxis: {
    data: ['正常', '预警', '告警']
  },
  yAxis: {},
  series: [{
    data: [
      stats.status_distribution.normal,
      stats.status_distribution.warning,
      stats.status_distribution.alarm
    ],
    type: 'bar'
  }]
};
```

---

## 7. 用户信息接口

### 7.1 获取用户列表
- **接口**: `GET /api/users/user-profiles/`
- **说明**: 获取所有用户档案
- **查询参数**: 
  - `page`: 页码（可选，默认第1页）
  - `page_size`: 每页数量（默认10条）
  - `role`: 角色类型（可选，筛选特定角色的用户）
- **响应**: 用户列表（分页格式）

**字段说明**:

| 字段名 | 类型 | 必填 | 含义 |
|--------|------|------|------|
| id | Integer | 自动生成 | 用户档案唯一标识符 |
| user | Integer | 是 | 关联的Django用户ID，外键关联User表（一对一关系） |
| user_basic_info | Object | 只读 | 用户基本信息（嵌套对象），包含：<br>• id - 用户ID<br>• username - 用户名<br>• email - 邮箱地址<br>• is_active - 是否激活<br>• date_joined - 加入时间 |
| role | String(20) | 是 | 用户角色权限，可选值：<br>• "admin" - 系统管理员（可操作所有数据）<br>• "monitor" - 监测员（可录入/查看数据）<br>• "viewer" - 数据查看者（仅可查看数据）<br>默认为"viewer" |
| phone | String(20) | 否 | 手机号码，用于联系和身份验证 |
| department | String(100) | 否 | 所属部门，如"技术部"、"监测中心"等 |
| create_time | DateTime | 自动生成 | 用户档案创建时间，格式：YYYY-MM-DD HH:MM:SS |

**响应示例**:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_basic_info": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_active": true,
        "date_joined": "2026-01-06T08:00:00Z"
      },
      "role": "admin",
      "phone": "13800138000",
      "department": "技术部",
      "create_time": "2026-01-06T08:00:00Z"
    }
  ]
}
```

### 7.2 获取单个用户档案
- **接口**: `GET /api/users/user-profiles/{id}/`
- **说明**: 获取指定ID的用户档案详细信息
- **路径参数**: `id` - 用户档案ID
- **响应**: 单个用户档案完整信息

### 7.3 创建用户档案
- **接口**: `POST /api/users/user-profiles/`
- **说明**: 创建新用户档案
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "user": 2,
  "role": "monitor",
  "phone": "13900139000",
  "department": "监测部"
}
```

**说明**:
- 创建用户档案前，需要先在Django Admin中创建对应的User用户
- `user`字段填写已存在的User ID
- 一个User只能对应一个UserProfile（一对一关系）
- `user_basic_info`字段会自动关联，无需手动填写

- **响应**: 返回创建的用户档案完整信息（包含user_basic_info）

### 7.4 更新用户信息
- **接口**: `PUT /api/users/user-profiles/{id}/`
- **说明**: 更新指定用户档案的完整信息
- **路径参数**: `id` - 用户档案ID
- **请求体**: 同创建接口
- **响应**: 返回更新后的用户档案完整信息

### 7.5 删除用户档案
- **接口**: `DELETE /api/users/user-profiles/{id}/`
- **说明**: 删除指定用户档案（不会删除关联的User，只删除档案信息）
- **路径参数**: `id` - 用户档案ID
- **响应**: `204 No Content`

---

## 8. 权限说明

本系统采用基于角色的访问控制（RBAC），不同角色对各接口的操作权限如下：

### 8.1 角色定义

| 角色 | 说明 | 典型用户 |
|------|------|----------|
| **admin** | 系统管理员 | 技术负责人、系统维护人员 |
| **monitor** | 监测员 | 现场监测、数据录入人员 |
| **viewer** | 访客/查看者 | 领导、外部审查人员 |

### 8.2 接口权限矩阵

#### 大坝信息接口

| 操作 | 接口 | admin | monitor | viewer |
|------|------|-------|---------|--------|
| 查看大坝列表 | GET /structures/ | ✅ | ✅ | ✅ |
| 查看大坝详情 | GET /structures/{id}/ | ✅ | ✅ | ✅ |
| 创建大坝 | POST /structures/ | ✅ | ❌ | ❌ |
| 更新大坝 | PUT /structures/{id}/ | ✅ | ❌ | ❌ |
| 删除大坝 | DELETE /structures/{id}/ | ✅ | ❌ | ❌ |

#### 监测设备接口

| 操作 | 接口 | admin | monitor | viewer |
|------|------|-------|---------|--------|
| 查看设备列表 | GET /devices/ | ✅ | ✅ | ✅ |
| 查看设备详情 | GET /devices/{id}/ | ✅ | ✅ | ✅ |
| 创建设备 | POST /devices/ | ✅ | ✅ | ❌ |
| 更新设备 | PUT /devices/{id}/ | ✅ | ✅ | ❌ |
| 删除设备 | DELETE /devices/{id}/ | ✅ | ✅ | ❌ |

#### 监测点接口

| 操作 | 接口 | admin | monitor | viewer |
|------|------|-------|---------|--------|
| 查看监测点列表 | GET /points/ | ✅ | ✅ | ✅ |
| 查看监测点详情 | GET /points/{id}/ | ✅ | ✅ | ✅ |
| 创建监测点 | POST /points/ | ✅ | ✅ | ❌ |
| 更新监测点 | PUT /points/{id}/ | ✅ | ✅ | ❌ |
| 删除监测点 | DELETE /points/{id}/ | ✅ | ✅ | ❌ |

#### 监测数据接口

| 操作 | 接口 | admin | monitor | viewer |
|------|------|-------|---------|--------|
| 查看监测数据 | GET /monitor-datas/ | ✅ | ✅ | ✅ |
| 查看单条数据 | GET /monitor-datas/{id}/ | ✅ | ✅ | ✅ |
| 新增监测数据 | POST /monitor-datas/ | ✅ | ✅ | ❌ |
| 批量新增数据 | POST /monitor-datas/batch/ | ✅ | ✅ | ❌ |
| 更新监测数据 | PUT /monitor-datas/{id}/ | ✅ | ✅ | ❌ |
| 删除监测数据 | DELETE /monitor-datas/{id}/ | ✅ | ✅ | ❌ |

#### 用户信息接口

| 操作 | 接口 | admin | monitor | viewer |
|------|------|-------|---------|--------|
| 查看用户列表 | GET /user-profiles/ | ✅ | ✅ | ✅ |
| 查看用户详情 | GET /user-profiles/{id}/ | ✅ | ✅ | ✅ |
| 创建用户档案 | POST /user-profiles/ | ✅ | ❌ | ❌ |
| 更新用户信息 | PUT /user-profiles/{id}/ | ✅ | ❌ | ❌ |
| 删除用户档案 | DELETE /user-profiles/{id}/ | ✅ | ❌ | ❌ |

**说明**: 上表基于后端权限策略；前端可在UI层做相应按钮的显隐与禁用。

### 8.3 权限实现建议

- 课程设计阶段：如未完全接入权限，可保持文档声明并在前端控制入口。
- 生产环境：使用 DRF Permission Classes，自定义按角色放行；删除/批量操作建议二次确认并记录操作日志。
- 数据隔离（可选）：如多大坝/多部门，可在 `get_queryset()` 中按用户部门过滤。

---

## 9. 数据校验规则

为保证数据质量和系统稳定性，所有接口在数据录入时会进行以下校验：

### 9.1 大坝信息校验

| 字段 | 校验规则 | 错误提示 |
|------|---------|----------|
| name | 必填，长度1-100字符 | "大坝名称不能为空" / "名称长度不能超过100字符" |
| cesium_center_x | 必填，数值型 | "X坐标必须为有效数值" |
| cesium_center_y | 必填，数值型 | "Y坐标必须为有效数值" |
| cesium_center_z | 必填，数值型，建议范围：-100 ~ 5000米 | "Z坐标（高程）超出合理范围" |
| cesium_heading | 数值型，范围：0 ~ 360度 | "航向角必须在0-360度之间" |
| cesium_pitch | 数值型，范围：-90 ~ 90度 | "俯仰角必须在-90至90度之间" |
| cesium_roll | 数值型，范围：-180 ~ 180度 | "翻滚角必须在-180至180度之间" |
| cesium_scale | 数值型，范围：0.01 ~ 100 | "缩放比例必须在0.01-100之间" |
| completion_time | 日期格式，不能晚于当前日期 | "建成时间不能是未来日期" |

### 9.2 监测设备校验

| 字段 | 校验规则 | 错误提示 |
|------|---------|----------|
| structure | 必填，必须是已存在的大坝ID | "所属大坝不存在" |
| device_name | 必填，长度1-100字符 | "设备名称不能为空" |
| device_type | 必填，必须是6种类型之一 | "设备类型无效" |
| install_position | 必填，长度1-200字符 | "安装位置不能为空" |
| install_time | 日期格式，不能晚于当前日期 | "安装时间不能是未来日期" |
| device_status | 必须是4种状态之一 | "设备状态无效" |

### 9.3 监测点校验

| 字段 | 校验规则 | 错误提示 |
|------|---------|----------|
| device | 必填，必须是已存在的设备ID | "所属设备不存在" |
| point_code | 必填，全局唯一，长度1-50字符 | "测点编号已存在" / "测点编号不能为空" |
| relative_x | 必填，数值型，建议范围：-500 ~ 500米 | "X偏移量超出合理范围" |
| relative_y | 必填，数值型，建议范围：-500 ~ 500米 | "Y偏移量超出合理范围" |
| relative_z | 必填，数值型，建议范围：-100 ~ 100米 | "Z偏移量超出合理范围" |
| displacement_upper | 数值型，建议范围：-1000 ~ 1000 mm | "位移上限阈值超出合理范围" |
| displacement_lower | 数值型，建议范围：-1000 ~ 1000 mm | "位移下限阈值超出合理范围" |
| settlement_upper | 数值型，建议范围：-1000 ~ 1000 mm | "沉降上限阈值超出合理范围" |
| settlement_lower | 数值型，建议范围：-1000 ~ 1000 mm | "沉降下限阈值超出合理范围" |
| water_level_upper | 数值型，建议范围：0 ~ 500 m | "水位上限阈值超出合理范围" |
| water_level_lower | 数值型，建议范围：0 ~ 500 m | "水位下限阈值超出合理范围" |

### 9.4 监测数据校验

| 字段 | 校验规则 | 错误提示 |
|------|---------|----------|
| point | 必填，必须是已存在的监测点ID | "监测点不存在" |
| monitor_time | 必填，**不能是未来时间** | "不能录入未来时间的监测数据" |
| 唯一性约束 | 同一监测点同一时间只能有一条数据 | "该监测点在此时间已有数据记录" |
| inverted_plumb_up_down | 数值型，建议范围：-1000 ~ 1000 mm | "位移值超出合理范围" |
| inverted_plumb_left_right | 数值型，建议范围：-1000 ~ 1000 mm | "位移值超出合理范围" |
| tension_wire_up_down | 数值型，建议范围：-1000 ~ 1000 mm | "位移值超出合理范围" |
| hydrostatic_leveling_settlement | 数值型，建议范围：-1000 ~ 1000 mm | "沉降值超出合理范围" |
| water_level_upstream | 数值型，建议范围：0 ~ 500 m | "水位值超出合理范围" |
| water_level_downstream | 数值型，建议范围：0 ~ 500 m | "水位值超出合理范围" |
| 监测值要求 | 至少填写一个监测值字段 | "至少需要填写一项监测数据" |

### 9.5 用户档案校验

| 字段 | 校验规则 | 错误提示 |
|------|---------|----------|
| user | 必填，必须是已存在的User ID，一对一关系 | "用户不存在" / "该用户已有档案" |
| role | 必填，必须是3种角色之一 | "用户角色无效" |
| phone | 手机号格式（可选），11位数字 | "手机号格式不正确" |
| department | 长度不超过100字符 | "部门名称过长" |

**说明**:
- 所有"建议范围"为软性限制，超出范围会记录警告日志但不阻止录入
- 可通过系统配置调整各项阈值的具体数值
- 批量操作时，任何一条数据校验失败会导致整批数据回滚

---

## 10. 通用说明

### 10.1 分页格式

所有列表接口都支持分页，响应格式如下：

```json
{
  "count": 100,
  "next": "URL",
  "previous": "URL",
  "results": []
}
```

**分页参数**:
- `page`: 页码（从1开始）
- `page_size`: 每页数量（默认10，最大100）

### 10.2 HTTP状态码

| 状态码 | 含义 |
|--------|------|
| 200 OK | 请求成功（GET、PUT） |
| 201 Created | 创建成功（POST） |
| 204 No Content | 删除成功（DELETE） |
| 400 Bad Request | 请求参数错误（字段验证失败） |
| 404 Not Found | 资源不存在（ID不存在） |
| 500 Internal Server Error | 服务器内部错误 |

### 10.3 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

或字段验证错误时：

```json
{
  "field_name": [
    "错误描述1",
    "错误描述2"
  ]
}
```

### 10.4 时间格式

1. **ISO 8601格式** (推荐): `2026-01-06T10:00:00Z`
2. **常规格式**: `2026-01-06 10:00:00`

### 10.5 前端调用示例（Axios）

```javascript
// 1. 获取所有监测点（包含Cesium坐标）
axios.get('http://localhost:8000/api/water-structures/points/')
  .then(response => {
    const points = response.data.results;
    points.forEach(point => {
      console.log(`测点 ${point.point_code} 的Cesium坐标:`, point.cesium_world_coords);
    });
  });

// 2. 新增监测数据
axios.post('http://localhost:8000/api/monitoring/monitor-datas/', {
  point: 1,
  monitor_time: '2026-01-06T10:00:00Z',
  inverted_plumb_up_down: 3.2,
  monitor_person: '李四'
})
  .then(response => {
    console.log('新增成功，预警状态:', response.data.status);
  })
  .catch(error => {
    console.error('错误:', error.response.data);
  });

// 3. 获取分页 + 过滤
axios.get('http://localhost:8000/api/monitoring/monitor-datas/', {
  params: {
    page: 1,
    page_size: 20,
    status: 'warning'
  }
})
  .then(response => {
    console.log('总数:', response.data.count);
    console.log('预警数据:', response.data.results);
  });
```

#### JavaScript (Axios)

```javascript
// 1. 获取所有监测点（包含Cesium坐标）
axios.get('http://localhost:8000/api/water-structures/points/')
  .then(response => {
    const points = response.data.results;
    points.forEach(point => {
      console.log(`测点 ${point.point_code} 的Cesium坐标:`, point.cesium_world_coords);
      // 可直接在Cesium中使用 point.cesium_world_coords.x/y/z
    });
  });

// 2. 新增监测数据
axios.post('http://localhost:8000/api/monitoring/monitor-datas/', {
  point: 1,
  monitor_time: '2026-01-06T10:00:00Z',
  inverted_plumb_up_down: 3.2,
  monitor_person: '李四'
})
  .then(response => {
    console.log('新增成功，预警状态:', response.data.status);
  })
  .catch(error => {
    console.error('错误:', error.response.data);
  });

// 3. 获取分页数据
axios.get('http://localhost:8000/api/monitoring/monitor-datas/', {
  params: {
    page: 1,
    page_size: 20,
    status: 'warning'  // 只查询预警数据
  }
})
  .then(response => {
    console.log('总数:', response.data.count);
    console.log('预警数据:', response.data.results);
  });

// 4. 筛选特定时间范围的数据
axios.get('http://localhost:8000/api/monitoring/monitor-datas/', {
  params: {
    point: 1,
    start_time: '2026-01-01 00:00:00',
    end_time: '2026-01-06 23:59:59'
  }
})
  .then(response => {
    console.log('时间范围内的数据:', response.data.results);
  });
```

#### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 获取大坝信息
response = requests.get(f"{BASE_URL}/water-structures/structures/")
dams = response.json()['results']
print(f"共有 {len(dams)} 个大坝")

# 创建监测点
new_point = {
    "device": 1,
    "point_code": "DQ-BD-003",
    "relative_x": 20.0,
    "relative_y": 10.0,
    "relative_z": 30.0,
    "displacement_upper": 5.0,
    "displacement_lower": -5.0
}
response = requests.post(
    f"{BASE_URL}/water-structures/points/", 
    json=new_point
)
print(f"创建成功，Cesium坐标: {response.json()['cesium_world_coords']}")
```

### 10.6 测试工具推荐

1. **DRF可视化界面** (推荐新手): 
   - 访问 `http://localhost:8000/api/` 
   - 提供图形化界面，可直接测试所有接口

2. **Postman**: 
   - 图形化API测试工具
   - 支持保存请求、批量测试

3. **curl命令行**:
```bash
# 获取大坝列表
curl http://localhost:8000/api/water-structures/structures/

# 创建新设备（POST请求）
curl -X POST http://localhost:8000/api/water-structures/devices/ \
  -H "Content-Type: application/json" \
  -d '{"structure": 1, "device_name": "测试设备", "device_type": "inverted_plumb_up_down", "install_position": "测试位置", "device_status": "running"}'
```

---

## 附录：完整接口清单

| 接口路径 | 方法 | 说明 |
|---------|------|------|
| `/api/water-structures/structures/` | GET | 获取大坝列表 |
| `/api/water-structures/structures/` | POST | 创建大坝 |
| `/api/water-structures/structures/{id}/` | GET | 获取大坝详情 |
| `/api/water-structures/structures/{id}/` | PUT | 更新大坝 |
| `/api/water-structures/structures/{id}/` | DELETE | 删除大坝 |
| `/api/water-structures/devices/` | GET | 获取设备列表 |
| `/api/water-structures/devices/` | POST | 创建设备 |
| `/api/water-structures/devices/{id}/` | GET | 获取设备详情 |
| `/api/water-structures/devices/{id}/` | PUT | 更新设备 |
| `/api/water-structures/devices/{id}/` | DELETE | 删除设备 |
| `/api/water-structures/points/` | GET | 获取测点列表 |
| `/api/water-structures/points/` | POST | 创建测点 |
| `/api/water-structures/points/{id}/` | GET | 获取测点详情 |
| `/api/water-structures/points/{id}/` | PUT | 更新测点 |
| `/api/water-structures/points/{id}/` | DELETE | 删除测点 |
| `/api/monitoring/monitor-datas/` | GET | 获取监测数据列表 |
| `/api/monitoring/monitor-datas/` | POST | 新增监测数据 |
| `/api/monitoring/monitor-datas/batch/` | POST | 批量新增监测数据 |
| `/api/monitoring/monitor-datas/{id}/` | GET | 获取单条数据 |
| `/api/monitoring/monitor-datas/{id}/` | PUT | 更新监测数据 |
| `/api/monitoring/monitor-datas/{id}/` | DELETE | 删除监测数据 |
| `/api/users/user-profiles/` | GET | 获取用户列表 |
| `/api/users/user-profiles/` | POST | 创建用户 |
| `/api/users/user-profiles/{id}/` | GET | 获取用户详情 |
| `/api/users/user-profiles/{id}/` | PUT | 更新用户 |
| `/api/users/user-profiles/{id}/` | DELETE | 删除用户 |

---

**文档版本**: v1.0  
**最后更新**: 2026-01-06  
**维护者**: 感谢chat和豆包的支持
