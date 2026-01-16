# Smart-Water-Conservancy-Platform-Architecture-Course-Project

> A water conservancy digital twin platform powered by Django REST Framework + Vue3 + Cesium  
> 智慧水利数字孪生平台课程设计实现

![Python](https://img.shields.io/badge/Python-3.10.11-blue)
![Django](https://img.shields.io/badge/Django-5.2.9-darkgreen)
![DRF](https://img.shields.io/badge/DRF-3.16.1-lightgreen)
![Vue](https://img.shields.io/badge/Vue-3.4.0-brightgreen)
![Cesium](https://img.shields.io/badge/Cesium-1.136-blue)
![JWT](https://img.shields.io/badge/Auth-JWT%2FToken-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 项目简介

本项目是一个智慧水利数字孪生平台的课程设计实现，是一个**完整的全栈应用**，集成了先进的实时监测、三维可视化和数据分析能力。

### 🎯 核心功能

- **✅ 三维数字孪生**：基于Cesium实现大坝三维模型和监测点空间可视化
- **✅ 实时监测数据管理**：支持6种设备类型、多种监测指标的数据采集和管理
- **✅ 智能预警系统**：自动判断监测数据的正常/预警/告警状态，支持阈值自定义
- **✅ 多用户权限管理**：管理员/监测员/访客三种角色的权限隔离
- **✅ 数据可视化统计**：监测数据图表展示、历史数据查询、统计分析（ECharts集成）
- **✅ 高效数据录入**：支持单条和批量导入监测数据
- **✅ 完整REST API**：规范的后端接口设计，支持前后端分离
- **✅ 用户注册登录**：完整的JWT认证系统，支持用户注册、登录、Token刷新

### 📊 后端新增功能（Phase 2）

- **P0 - 单点详情增强** ✅：point detail响应新增 `unit/current_value/current_status/relevant_thresholds/last_update_time` 5个关键字段
- **P1 - 数据统计分析** ✅：提供 `/api/monitoring/statistics/` 聚合接口，返回监测点总数、状态分布、设备类型分布
- **P2 - 阈值管理API** ✅：提供 `/api/water-structures/points/{id}/thresholds/` GET/PUT接口，支持动态调整告警阈值
- **实时数据接口** ✅：提供虚拟实时数据生成、历史数据查询、预警摘要等接口
- **坝段管理** ✅：支持大坝坝段信息查询和汇总
- **用户注册** ✅：新增用户注册接口，支持自动创建用户档案

### 🛠️ 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| **后端** | Django + DRF | 5.2.9 + 3.16.1 |
| **前端** | Vue 3 + Vite + Cesium | 3.4.0 + 4.4.0 + 1.136 |
| **UI框架** | Element Plus | 2.4.0 |
| **图表库** | ECharts | 5.4.0 |
| **认证** | JWT Token | djangorestframework-simplejwt 5.5.1 |
| **数据库** | SQLite3/MySQL | - |
| **HTTP客户端** | Axios | 1.6.0 |
| **跨域** | django-cors-headers | 4.9.0 |

---

## 🚀 快速开始

### 环境需求

- Python 3.10+
- Node.js 18+ (前端开发)
- MySQL 5.7+ 或 SQLite 3

### 后端环境配置

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python manage.py migrate

# 5. 创建超级用户（可选）
python manage.py createsuperuser

# 6. 启动开发服务器
python manage.py runserver
```

**默认配置**：
- 后端服务运行在：`http://localhost:8000`
- Django Admin：`http://localhost:8000/admin/`
- API根路径：`http://localhost:8000/api/`

### 前端环境配置

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（推荐 Node.js 18+）
npm install

# 3. 启动开发服务器（默认端口3000）
npm run dev

# 4. 构建生产版本
npm run build

# 5. 预览构建结果
npm run preview
```

**Cesium 配置说明**：
- Cesium库已内置于 `public/Cesium-1.136/`
- Ion Token 已配置在 `src/main.js`（若需替换，请注册 [Cesium Ion](https://cesium.com/ion/)）
- 基础路径：`window.CESIUM_BASE_URL = '/Cesium-1.136/Build/Cesium/'`

### 访问地址

- **前端应用**: `http://localhost:3000/`（Vue3 + Cesium 三维场景）
- **后端API**: `http://localhost:8000/api/`
- **Django Admin**: `http://localhost:8000/admin/`
- **API详细文档**: 见项目根目录 `API接口文档.md`

---

## 🔐 JWT 认证指南

### 前端对接快速指南

本平台已全局启用 **JWT Token认证**，所有API（除登录/刷新/注册外）需要携带有效的 access token。

#### 1. 用户注册

```bash
POST /api/users/register/
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123"
}
```

#### 2. 用户登录

```bash
POST /api/users/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

**响应**：
```json
{
  "success": true,
  "message": "登录成功",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",    # 有效期 1 小时
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."    # 有效期 7 天
  },
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

**前端保存策略**：
- 将 `tokens.access` 存储到内存（或 sessionStorage）
- 将 `tokens.refresh` 存储到 localStorage（用于刷新token）
- 将 `user` 存储到 Vuex/Pinia（用于权限检查和UI展示）

#### 3. 携带Token访问受保护接口

所有受保护接口都需要在请求头中加入 Authorization：

```bash
GET /api/water-structures/structures/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**前端代码示例（Axios）**：
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// 请求拦截器：自动添加Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理401过期
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token过期，尝试刷新
      const refreshToken = localStorage.getItem('refresh_token');
      try {
        const { data } = await axios.post('/api/users/refresh/', {
          refresh: refreshToken,
        });
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        // 重新发送原请求
        return api.request(error.config);
      } catch {
        // 刷新失败，跳转登录
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

#### 4. 刷新Token

当 access token 过期时（1小时后），使用 refresh token 刷新：

```bash
POST /api/users/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Token有效期**：
- **Access Token**: 1 小时
- **Refresh Token**: 7 天

---

## 📁 项目结构

```
Smart-Water-Conservancy-Platform-Architecture-Course-Project/
├── backend/                          # Django后端项目
│   ├── hydro_platform/              # 项目主配置
│   │   ├── settings.py              # 核心配置（DRF、CORS、数据库）
│   │   ├── urls.py                  # 主路由
│   │   ├── config.py                # 配置文件
│   │   └── wsgi.py
│   ├── water_structures/            # 大坝结构app
│   │   ├── models.py                # Structure/MonitoringDevice/Point模型
│   │   ├── serializers.py           # 序列化器（含嵌套关系）
│   │   ├── views.py                 # ViewSet视图
│   │   ├── urls.py                  # 应用路由
│   │   ├── permissions.py           # 权限控制
│   │   └── segment_manager.py       # 坝段管理
│   ├── monitoring/                  # 监测数据app
│   │   ├── models.py                # MonitorData模型（自动预警）
│   │   ├── serializers.py           # 序列化器
│   │   ├── views.py                 # ViewSet视图
│   │   ├── urls.py                  # 应用路由
│   │   ├── utils.py                 # 工具函数（实时数据生成）
│   │   └── permissions.py           # 权限控制
│   ├── users/                       # 用户管理app
│   │   ├── models.py                # UserProfile模型
│   │   ├── serializers.py           # 序列化器
│   │   ├── views.py                 # ViewSet视图（含JWT认证）
│   │   ├── urls.py                  # 应用路由
│   │   └── permissions.py           # 权限控制
│   ├── manage.py
│   ├── requirements.txt             # Python依赖
│   └── db.sqlite3                   # SQLite数据库（开发环境）
├── frontend/                         # Vue3 前端项目
│   ├── public/
│   │   ├── Cesium-1.136/            # CesiumJS 完整库（1.136版本）
│   │   └── models/                  # 3D模型文件
│   ├── src/
│   │   ├── api/                     # API接口封装
│   │   │   ├── auth.js              # 认证接口
│   │   │   ├── monitoring.js        # 监测数据接口
│   │   │   ├── users.js             # 用户接口
│   │   │   ├── waterStructures.js   # 大坝结构接口
│   │   │   └── request.js           # Axios配置
│   │   ├── components/              # Vue组件
│   │   │   ├── CesiumScene.vue       # 三维地球核心组件
│   │   │   ├── LoginPage.vue        # 登录页面
│   │   │   ├── RegisterPage.vue     # 注册页面
│   │   │   ├── DataPanel.vue         # 数据面板
│   │   │   ├── SensorPanel.vue      # 传感器面板
│   │   │   ├── DatabaseView.vue      # 数据库视图
│   │   │   ├── charts/               # 图表组件（ECharts）
│   │   │   └── ...
│   │   ├── views/                   # 页面视图
│   │   │   ├── MainDashboard.vue    # 主仪表盘
│   │   │   ├── SceneView.vue          # 三维场景视图
│   │   │   └── DatabaseViewPage.vue  # 数据库视图页面
│   │   ├── store/                   # 状态管理
│   │   │   └── auth.js               # 认证状态
│   │   ├── utils/                   # 工具函数
│   │   │   ├── auth.js               # 认证工具
│   │   │   └── sensorMapping.js     # 传感器映射
│   │   ├── App.vue                   # 根组件
│   │   └── main.js                   # 入口文件（Cesium Token配置）
│   ├── index.html                   # 主页面
│   ├── vite.config.js               # Vite配置（端口3000、CORS、别名）
│   └── package.json                 # 依赖管理（Vue3/Axios/Vite）
├── .gitignore                        # Git忽略规则
├── API接口文档.md                    # 完整的API文档（1800+行）
├── DATABASE_DESIGN.md                # 数据库设计文档
├── README.md                         # 本文件
└── 课设材料/                         # 课程设计相关材料（RVT模型等）
```

---

## 📋 权限系统

### 三种用户角色

本平台采用**基于角色的访问控制（RBAC）** 模式，定义了三个用户角色及其权限：

| 角色 | 权限级别 | 操作权限 | 使用场景 |
|------|---------|--------|--------|
| **admin** | 最高 | 读写删所有资源 | 系统管理员，维护基础设施和大坝信息 |
| **monitor** | 中级 | 读所有，写监测数据/设备/测点 | 监测员，现场数据采集和上报，不可修改大坝本体信息 |
| **viewer** | 只读 | 仅读取所有数据 | 数据查看者，查看监测数据和分析，禁止任何写入操作 |

### 接口权限矩阵

#### 大坝结构（Structures）
- **GET** (列表/详情)：所有**认证用户**可读
- **POST** (创建)：仅 **admin** 可操作
- **PUT/PATCH** (更新)：仅 **admin** 可操作
- **DELETE** (删除)：仅 **admin** 可操作

#### 监测设备（Devices）和测点（Points）
- **GET** (列表/详情)：所有**认证用户**可读
- **POST** (创建)：**admin** 和 **monitor** 可操作
- **PUT/PATCH** (更新)：**admin** 和 **monitor** 可操作
- **DELETE** (删除)：**admin** 和 **monitor** 可操作

#### 监测数据（MonitorData）
- **GET** (列表/详情)：所有**认证用户**可读
- **GET** (实时查询：latest_data/alert_summary/history)：所有**认证用户**可读
- **POST** (创建)：**admin** 和 **monitor** 可操作
- **PUT/PATCH** (更新)：**admin** 和 **monitor** 可操作
- **DELETE** (删除)：**admin** 和 **monitor** 可操作

#### 用户信息（Users）
- **GET** `/api/users/current/`：所有**认证用户**可读（获取自己的信息）
- **GET** `/api/users/user-profiles/`：所有**认证用户**可读（查看其他用户档案）
- **POST/PUT/DELETE**：仅 **admin** 可操作

---

## 🔌 API快览

**完整API文档**：见 [API接口文档.md](API接口文档.md)

```
认证接口      : /api/users/register/            (用户注册)
               : /api/users/login/              (登录获取Token)
               : /api/users/refresh/            (刷新Token)
               : /api/users/current/            (获取当前用户)
大坝信息      : /api/water-structures/structures/
               : /api/water-structures/structures/{id}/segments/ (坝段列表)
               : /api/water-structures/structures/{id}/segments/{segment_id}/ (坝段详情)
监测设备      : /api/water-structures/devices/
监测点        : /api/water-structures/points/
               : /api/water-structures/points/with_data/ (有数据的测点)
               : /api/water-structures/points/{id}/thresholds/ (阈值管理)
监测数据      : /api/monitoring/data/ (含批量导入)
               : /api/monitoring/data/latest_data/ (最新数据)
               : /api/monitoring/data/alert_summary/ (预警汇总)
               : /api/monitoring/data/history/ (历史数据)
               : /api/monitoring/latest/ (实时数据)
               : /api/monitoring/history/{point_id}/ (测点历史)
               : /api/monitoring/alerts/ (预警摘要)
               : /api/monitoring/statistics/ (数据统计)
               : /api/monitoring/health/ (健康检查)
用户管理      : /api/users/user-profiles/

每个资源支持：GET(查), POST(增), PUT(改), DELETE(删)
总计40+个接口 = 认证4 + 大坝7 + 设备5 + 测点7 + 数据13 + 用户5
```

---

## 📊 数据模型

### 1. Structure（大坝信息）
- **字段**：名称、Cesium三维坐标、建成时间、工程等级等（12字段）
- **特色**：完整的Cesium定位参数（center、heading、pitch、roll、scale、model_url）
- **用途**：数字孪生的中心节点

### 2. MonitoringDevice（监测设备）
- **支持6种类型**：倒垂线、引张线、静力水准、水位传感器
- **字段**：名称、安装位置、安装时间、运行状态
- **用途**：物理设备管理

### 3. Point（监测点）
- **特色**：自动计算Cesium世界坐标（大坝中心 + 相对偏移）
- **字段**：测点编号、相对坐标、阈值配置
- **用途**：空间化表示，支持三维可视化

### 4. MonitorData（监测数据）
- **自动预警**：在save()方法中根据阈值判断状态
- **字段**：采集时间、6种监测指标、监测人员、备注
- **约束**：同一测点同一时间仅一条数据
- **用途**：历史数据存储 + 时间序列分析

### 5. UserProfile（用户档案）
- **三种角色**：admin(管理员) / monitor(监测员) / viewer(访客)
- **字段**：关联Django用户、角色、电话、部门
- **用途**：权限隔离 + 用户追踪

详细数据库设计见 [DATABASE_DESIGN.md](DATABASE_DESIGN.md)

---

## 📊 工作日志

### 2026-01-06（第1天）✅ 后端完成

#### 完成的工作

**1. 项目框架搭建**
- ✅ Django 5.2.9 + DRF 3.16.1 环境配置
- ✅ 创建3个业务app（water_structures、monitoring、users）
- ✅ CORS跨域支持，Python 3.10.11环境
- ✅ 中文本地化 + 亚洲/上海时区配置

**2. JWT 认证系统** ⭐
- ✅ djangorestframework-simplejwt 集成
- ✅ 登录接口 (POST /api/users/login/)：返回 access + refresh token
- ✅ 注册接口 (POST /api/users/register/)：用户注册并自动登录
- ✅ 刷新接口 (POST /api/users/refresh/)：延期 access token
- ✅ 当前用户接口 (GET /api/users/current/)：获取登录用户信息
- ✅ 全局Token认证：所有受保护接口需要 Authorization 头
- ✅ 用户档案自动创建：登录时自动创建 UserProfile，默认角色为 viewer

**3. 三角色权限系统** ⭐
- ✅ admin（管理员）：读写删所有资源
- ✅ monitor（监测员）：读所有，写监测数据/设备/测点
- ✅ viewer（访客）：仅读，禁止任何写操作
- ✅ 权限拦截：403 Forbidden自动返回

**4. 数据模型（5个）**
- ✅ **Structure** (大坝)：12字段，含Cesium三维参数
- ✅ **MonitoringDevice** (设备)：6种设备类型支持
- ✅ **Point** (监测点)：自动Cesium坐标计算
- ✅ **MonitorData** (数据)：6种指标 + 自动预警 + 字段验证
- ✅ **UserProfile** (用户)：3种角色权限 + 部门电话信息

**5. REST API (40+个接口)** ⭐
- ✅ 4个认证接口 (注册/登录/刷新/当前用户)
- ✅ 7个大坝接口 (CRUD + 坝段列表/详情)
- ✅ 5个设备接口 (CRUD + 列表)
- ✅ 7个测点接口 (CRUD + 有数据筛选 + 阈值管理)
- ✅ 13个监测数据接口 (CRUD + 批量导入 + 最新数据 + 预警汇总 + 历史数据 + 实时数据 + 预警摘要 + 统计 + 健康检查)
- ✅ 5个用户接口 (CRUD + 当前用户)
- ✅ 分页、过滤、排序支持

**6. 数据验证** ⭐
- ✅ 字段级验证：6个监测指标的数据类型、精度、范围检查
  - 倒垂线上下、左右：允许负数，精度2位
  - 引张线上下：允许负数，精度2位
  - 静力水准沉降：允许负数，精度2位
  - 水位上下游：不允许负数，精度3位
- ✅ 全局验证：同一测点同一时刻仅一条数据（unique_together）
- ✅ 时间验证：禁止记录未来时间的数据
- ✅ 自动状态计算：save()方法根据阈值判断 normal/warning/alarm

**7. Django Admin**
- ✅ 5个模型注册 + 中文化
- ✅ 字段可读性优化
- ✅ 数据快速录入界面

**8. 完整API文档** (1800+行)
- ✅ 所有接口详细说明（40+个）
- ✅ 字段级说明表格（类型、必填、含义）
- ✅ 请求/响应示例 + JavaScript/Python示例
- ✅ JWT认证指南及前端集成示例
- ✅ 权限说明和RBAC矩阵
- ✅ 数据校验规则详细说明
- ✅ curl命令行用例

### 2026-01-07 ~ 2026-01-16（前端开发）✅ 前端完成

#### 完成的工作

**1. 前端项目搭建**
- ✅ Vue3 + Vite 项目初始化
- ✅ Element Plus UI框架集成
- ✅ ECharts 图表库集成
- ✅ Axios HTTP客户端配置
- ✅ 路由和状态管理设置

**2. Cesium三维可视化** ⭐
- ✅ Cesium 1.136 完整集成
- ✅ 大坝3D模型加载（GLB/GLTF格式）
- ✅ 监测点三维标注（Entity + Label）
- ✅ 相机控制和场景交互
- ✅ 实时数据更新和可视化

**3. 用户认证界面**
- ✅ 登录页面（LoginPage.vue）
- ✅ 注册页面（RegisterPage.vue）
- ✅ JWT Token自动管理
- ✅ 权限路由守卫

**4. 数据可视化** ⭐
- ✅ 主仪表盘（MainDashboard.vue）
- ✅ 数据面板（DataPanel.vue）
- ✅ 传感器面板（SensorPanel.vue）
- ✅ 数据库视图（DatabaseView.vue）
- ✅ 多种图表组件（ECharts）：
  - 水位趋势图
  - 位移对比图
  - 沉降面积图
  - 上下游水位对比
  - 等等

**5. 三维场景视图**
- ✅ 场景视图（SceneView.vue）
- ✅ Cesium场景组件（CesiumScene.vue）
- ✅ 监测点交互和详情展示
- ✅ 实时数据展示

**6. API接口封装**
- ✅ 认证接口（auth.js）
- ✅ 监测数据接口（monitoring.js）
- ✅ 用户接口（users.js）
- ✅ 大坝结构接口（waterStructures.js）
- ✅ Axios请求拦截器配置（request.js）

#### 关键技术亮点

| 点 | 实现 |
|----|------|
| **JWT认证** | simplejwt + RefreshToken，access(1h)/refresh(7d) 双token方案 |
| **权限管理** | Custom PermissionClass + UserProfile.role，精细化RBAC控制 |
| **嵌套序列化** | PointSerializer → device_info，MonitorDataSerializer → point_info → device_info |
| **自动计算字段** | SerializerMethodField实现cesium_world_coords，前端直接用无需计算 |
| **预警系统** | MonitorData.save()中自动判断，支持6种指标的阈值对比 |
| **数据验证** | 字段级validators + 全局validate() + unique_together约束 |
| **实时查询** | latest_data(单点最新) / alert_summary(预警统计) / history(时间序列) |
| **三维可视化** | Cesium集成，支持3D模型加载和空间标注 |
| **数据可视化** | ECharts集成，多种图表类型支持 |
| **模块化设计** | 3个app独立开发，便于团队合作 |

---

## 🎯 技术选型说明

### 为什么选择Django REST Framework？
- ✅ Python学习友好，快速开发
- ✅ 完整的权限和认证框架
- ✅ 强大的序列化器（嵌套、自定义字段）
- ✅ 可视化API界面，便于测试和演示
- ✅ 有丰富的生产级别最佳实践

### 为什么用Cesium做三维可视化？
- ✅ 开源免费，功能完整
- ✅ 支持WebGL，性能优秀
- ✅ GIS能力强，坐标系统完善
- ✅ 社区活跃，文档齐全
- ✅ 易于集成Vue3

### 为什么选择Vue3？
- ✅ 组件化开发，代码复用性高
- ✅ 响应式系统，实时数据绑定
- ✅ Composition API，逻辑复用更灵活
- ✅ 与Cesium集成方案成熟
- ✅ 就业市场需求量大

### 为什么用Vite构建？
- ✅ 开发服务器启动极快（ESM）
- ✅ 热更新性能优秀
- ✅ 开箱即用的TypeScript/Vue支持
- ✅ 构建产物优化（Rollup）
- ✅ 配置简洁直观

### 为什么选择Element Plus？
- ✅ Vue3官方推荐的UI框架
- ✅ 组件丰富，开箱即用
- ✅ 文档完善，中文支持好
- ✅ 样式美观，易于定制

### 为什么选择ECharts？
- ✅ 功能强大，图表类型丰富
- ✅ 性能优秀，支持大数据量
- ✅ 文档完善，示例丰富
- ✅ 与Vue3集成简单

---

## 📝 开发规范

### 命名约定

```
模型类      : PascalCase  (Structure, MonitoringDevice)
数据库字段  : snake_case  (cesium_center_x, monitor_time)
API路由    : kebab-case  (/monitor-datas/, /user-profiles/)
Python函数  : snake_case  (get_cesium_coords, save_monitor_data)
Vue组件    : PascalCase  (CesiumScene.vue, DataPanel.vue)
JavaScript变量: camelCase (accessToken, userInfo)
```

### 代码注释示例

```python
class MonitorData(models.Model):
    """
    监测数据模型 - 存储监测点的实时/历史数据
    
    该模型支持：
    - 6种监测指标的数据录入
    - 自动预警状态判断
    - 历史数据查询和统计
    """
    point = models.ForeignKey(Point, ...)  # 关联到具体监测点
    monitor_time = models.DateTimeField()  # 采集时间（禁止未来时间）
```

---

## 🧪 测试指南

### 快速测试

```bash
# 1. 访问DRF可视化界面（推荐新手）
http://localhost:8000/api/

# 2. 获取大坝列表
curl http://localhost:8000/api/water-structures/structures/

# 3. 创建监测数据
curl -X POST http://localhost:8000/api/monitoring/data/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"point":1,"monitor_time":"2026-01-06T10:00:00Z","inverted_plumb_up_down":2.5}'
```

### 使用Postman
- 导入API文档中的请求示例
- 设置环境变量 `BASE_URL = http://localhost:8000/api`
- 逐个测试各接口

### 前端测试
- 启动前端开发服务器：`npm run dev`
- 访问 `http://localhost:3000`
- 使用测试账号登录测试各项功能

---

## 📋 课设材料清单

```
✅ 已完成：
├─ 需求分析文档 (README.md)
├─ 数据库设计文档 (DATABASE_DESIGN.md)
├─ API接口文档 (API接口文档.md, 1800+行)
├─ 源代码 (后端完整实现 + 前端完整实现)
├─ 工作日志 (本README)
└─ 项目演示材料

🔄 可选完善：
├─ 单元测试用例
├─ 性能优化
├─ 批量导入功能完善
└─ 答辩PPT准备
```

---

## 🤝 技能收获

通过这个项目，你将学到：

| 技能 | 深度 | 应用场景 |
|------|------|--------|
| **Django/DRF** | ⭐⭐⭐⭐ | 后端API开发 |
| **数据库设计** | ⭐⭐⭐⭐ | 关系模型、ForeignKey、唯一约束 |
| **REST API设计** | ⭐⭐⭐⭐ | 接口规范、版本管理、文档化 |
| **JWT认证** | ⭐⭐⭐⭐ | Token机制、刷新策略 |
| **权限管理** | ⭐⭐⭐ | RBAC、粒度控制 |
| **Vue3 + Vite** | ⭐⭐⭐ | Composition API、组件化 |
| **Cesium三维GIS** | ⭐⭐⭐ | 地球渲染、3D Tiles、坐标变换 |
| **ECharts数据可视化** | ⭐⭐⭐ | 图表设计、数据展示 |
| **Element Plus** | ⭐⭐⭐ | UI组件使用、样式定制 |
| **Axios HTTP** | ⭐⭐⭐ | 拦截器、异步请求 |
| **Git工作流** | ⭐⭐⭐ | 分支管理、冲突解决 |
| **系统设计** | ⭐⭐⭐⭐ | 从零到一的思维 |

---

## 📚 参考资源

### 官方文档
- [Django官网](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Cesium.js文档](https://cesium.com/docs/)
- [Vue3官网](https://vuejs.org/)
- [Element Plus文档](https://element-plus.org/)
- [ECharts文档](https://echarts.apache.org/)

### 推荐教程
- DRF序列化器深度讲解
- Cesium Entity与坐标系统
- Vue3 Composition API
- ECharts图表设计

---

## 📞 常见问题

**Q: 后端怎样支持生产环境？**  
A: 需要配置PostgreSQL数据库、Gunicorn WSGI服务器、Nginx反向代理、Redis缓存等。

**Q: 权限控制如何实现？**  
A: 后端使用Custom PermissionClass实现RBAC，前端通过role字段控制按钮显示和路由守卫。

**Q: 前端怎样调用后端API？**  
A: 使用Axios库，详见API文档中的JavaScript示例。已封装在`src/api/`目录下。

**Q: 如何进行性能优化？**  
A: 建立数据库索引、使用字段过滤、分页查询、缓存热数据、前端虚拟滚动等。

**Q: Cesium模型如何加载？**  
A: 将GLB/GLTF模型文件放在`public/models/`目录下，在CesiumScene组件中使用`viewer.entities.add()`加载。

---

## 🎉 致谢

感谢：
- Django社区提供的优秀框架
- Cesium团队提供的强大三维引擎
- Vue.js团队提供的现代化前端框架
- Element Plus团队提供的UI组件库
- ECharts团队提供的数据可视化库
- 教授的课程指导和作业设计
- Stack Overflow的技术支持
-各大ai
---

