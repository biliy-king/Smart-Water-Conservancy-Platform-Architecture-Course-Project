# Smart-Water-Conservancy-Platform-Architecture-Course-Project

> A water conservancy digital twin platform powered by Django REST Framework + Vue3 + Cesium  
> 智慧水利数字孪生平台课程设计实现

![Python](https://img.shields.io/badge/Python-3.10.11-blue)
![Django](https://img.shields.io/badge/Django-5.2.9-darkgreen)
![DRF](https://img.shields.io/badge/DRF-3.16.1-lightgreen)
![Vue](https://img.shields.io/badge/Vue-3.5.25-brightgreen)
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
- **✅ 数据可视化统计**：监测数据图表展示、历史数据查询、统计分析
- **✅ 高效数据录入**：支持单条和批量导入监测数据
- **✅ 完整REST API**：规范的后端接口设计，支持前后端分离

### 📊 后端新增功能（Phase 2）
- **P0 - 单点详情增强**：point detail响应新增 `unit/current_value/current_status/relevant_thresholds/last_update_time` 5个关键字段
- **P1 - 数据统计分析**：提供 `/api/monitoring/statistics/` 聚合接口，返回监测点总数、状态分布、设备类型分布
- **P2 - 阈值管理API**：提供 `/api/water-structures/points/{id}/thresholds/` GET/PUT接口，支持动态调整告警阈值

### 🛠️ 技术栈
| 层级 | 技术 | 版本 |
|------|------|------|
| **后端** | Django + DRF | 5.2.9 + 3.16.1 |
| **前端** | Vue 3 + Vite + Cesium | 3.5.25 + 7.2.4 + 1.136 |
| **认证** | JWT Token | djangorestframework-simplejwt 5.3.2 |
| **数据库** | SQLite3/MySQL | - |
| **HTTP客户端** | Axios | 1.13.2 |
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

# 5. 创建初始数据（可选）
python manage.py loaddata database/fixtures/initial_data.json

# 6. 生成Admin Token用于测试
python get_admin_token.py

# 7. 启动开发服务器
python manage.py runserver
```

### 环境变量
- 复制根目录 `.env.example` 为 `.env`，按需修改：`SECRET_KEY`、`DEBUG`、`ALLOWED_HOSTS`、`DATABASE_URL`。
- 默认 SQLite 开发环境即可运行；生产环境请改为专用数据库并关闭 `DEBUG`。

### 前端环境配置

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（推荐 Node.js 20.19+ 或 22.12+）
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

本平台已全局启用 **JWT Token认证**，所有API（除登录/刷新外）需要携带有效的 access token。

#### 1. 登录获取Token
```bash
# 请求
POST /api/users/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}

# 响应（201 Created）
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

#### 2. 携带Token访问受保护接口
```bash
# 所有受保护接口都需要在请求头中加入 Authorization
GET /api/water-structures/structures/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# 响应（200 OK）
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [...]
}
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

#### 3. 获取当前用户信息
```bash
# 请求
GET /api/users/current/
Authorization: Bearer <access_token>

# 响应（200 OK）
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

**用途**：登录后拉取完整的用户信息（包括部门、电话等扩展字段）

#### 4. 刷新Token
```bash
# 请求（当 access token 过期时调用）
POST /api/users/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  # 来自登录时的 refresh token
}

# 响应（200 OK）
{
  "success": true,
  "message": "Token刷新成功",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",     # 新的 access token（1h有效期）
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."     # 新的 refresh token（7d有效期）
  }
}
```

**Token有效期**：
- **Access Token**: 1 小时
- **Refresh Token**: 7 天

#### 5. 错误处理

| 状态码 | 错误原因 | 处理方式 |
|--------|---------|--------|
| **401** | Token过期或无效 | 调用刷新接口或重新登录 |
| **403** | 权限不足（如 viewer 尝试写操作） | 提示"权限不足，请联系管理员" |
| **400** | 请求参数错误 | 检查请求体和字段格式 |
| **500** | 服务器错误 | 重试或联系技术支持 |

**前端错误处理模板**：
```javascript
try {
  const response = await api.get('/api/water-structures/structures/');
  // 成功，处理数据
} catch (error) {
  if (error.response?.status === 401) {
    console.error('Token过期，请重新登录');
    window.location.href = '/login';
  } else if (error.response?.status === 403) {
    console.error('权限不足');
  } else {
    console.error('请求失败：', error.message);
  }
}
```

---

## 📁 项目结构

```
Smart-Water-Conservancy-Platform-Architecture-Course-Project/
├── backend/                          # Django后端项目
│   ├── hydro_platform/              # 项目主配置
│   │   ├── settings.py              # 核心配置（DRF、CORS、数据库）
│   │   ├── urls.py                  # 主路由
│   │   └── wsgi.py
│   ├── water_structures/            # 大坝结构app
│   │   ├── models.py                # Structure/MonitoringDevice/Point模型
│   │   ├── serializers.py           # 序列化器（含嵌套关系）
│   │   ├── views.py                 # ViewSet视图
│   │   └── urls.py                  # 应用路由
│   ├── monitoring/                  # 监测数据app
│   │   ├── models.py                # MonitorData模型（自动预警）
│   │   ├── serializers.py           # 序列化器
│   │   ├── views.py                 # ViewSet视图
│   │   └── urls.py                  # 应用路由
│   ├── users/                       # 用户管理app
│   │   ├── models.py                # UserProfile模型
│   │   ├── serializers.py           # 序列化器
│   │   ├── views.py                 # ViewSet视图
│   │   └── urls.py                  # 应用路由
│   ├── manage.py
│   └── requirements.txt
├── frontend/                         # Vue3 前端项目
│   ├── public/Cesium-1.136/         # CesiumJS 完整库（1.136版本）
│   ├── src/
│   │   ├── App.vue                  # 根组件
│   │   ├── main.js                  # 入口文件（Cesium Token配置）
│   │   ├── components/
│   │   │   └── CesiumViewer.vue     # 三维地球核心组件
│   │   └── assets/                  # 静态资源
│   ├── index.html                   # 主页面
│   ├── vite.config.js               # Vite配置（端口3000、CORS、别名）
│   ├── package.json                 # 依赖管理（Vue3/Axios/Vite）
│   └── README.md                    # 前端说明文档
├── .gitignore                        # Git忽略规则（pyc/sqlite/env/node_modules）
├── .env.example                      # 环境变量模板
├── API接口文档.md                    # 完整的API文档（1287行）
├── README.md                         # 本文件
└── 课设材料/                         # 课程设计相关材料（RVT模型等）
```

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

### 权限检查示例

**请求头缺少Token（未认证）**：
```
GET /api/water-structures/structures/
# 响应 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

**Token有效但权限不足（如viewer尝试新增）**：
```
POST /api/water-structures/structures/
Authorization: Bearer <viewer_token>
{
  "name": "新大坝",
  ...
}
# 响应 403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}
```

**Token有效且权限足够（如monitor新增监测数据）**：
```
POST /api/monitoring/monitor-datas/
Authorization: Bearer <monitor_token>
{
  "point": 1,
  "monitor_time": "2026-01-06T10:00:00Z",
  "inverted_plumb_up_down": 2.5,
  ...
}
# 响应 201 Created
{
  "success": true,
  "message": "监测数据创建成功",
  "data": { ... }
}
```

---

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

---

## 🔌 API快览

**完整API文档**：见 [API接口文档.md](API接口文档.md)

```
认证接口      : /api/users/login/              (登录获取Token)
               : /api/users/refresh/            (刷新Token)
               : /api/users/current/            (获取当前用户)
大坝信息      : /api/water-structures/structures/
监测设备      : /api/water-structures/devices/
监测点        : /api/water-structures/points/
监测数据      : /api/monitoring/monitor-datas/ (含批量导入 + 三个实时接口)
用户管理      : /api/users/user-profiles/

每个资源支持：GET(查), POST(增), PUT(改), DELETE(删)
总计29个接口 = 认证3 + 大坝5 + 设备5 + 测点5 + 数据5 + 批量1 + 实时3 + 用户2
```

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

**5. REST API (29个接口)** ⭐
- ✅ 3个认证接口 (登录/刷新/当前用户)
- ✅ 5个大坝接口 (GET列表/详情、POST创建、PUT更新、DELETE删除)
- ✅ 5个设备接口 (同上)
- ✅ 5个测点接口 (同上)
- ✅ 5个监测数据接口 + 1个批量导入 (POST batch/)
- ✅ 3个实时查询接口：latest_data / alert_summary / history
- ✅ 2个用户接口 (当前用户、用户列表)
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

**8. 完整API文档** (1000+行)
- ✅ 所有接口详细说明（29个）
- ✅ 字段级说明表格（类型、必填、含义）
- ✅ 请求/响应示例 + JavaScript/Python示例
- ✅ JWT认证指南及前端集成示例
- ✅ 权限说明和RBAC矩阵
- ✅ 数据校验规则详细说明
- ✅ curl命令行用例

**9. 版本管理**
- ✅ Git分支管理（后端分支 + merge到main）
- ✅ 冲突解决
- ✅ .gitignore优化

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
| **模块化设计** | 3个app独立开发，便于团队合作 |

#### 解决的问题
| 问题 | 解决方案 |
|------|--------|
| django-admin PATH错误 | 添加Scripts目录到系统PATH |
| Git merge冲突 | 删除未追踪文件，重新migrate |
| Cesium坐标显示问题 | 改为明确字段列表而非fields="__all__" |
| 模型循环导入 | 分离models + 用related_name管理 |

#### 当前统计
```
后端完成度: ████████████████████ 100%

接口统计：
├─ 认证接口          : 3 个   (login / refresh / current)
├─ 大坝接口          : 5 个   (CRUD + 列表)
├─ 设备接口          : 5 个   (CRUD + 列表)
├─ 测点接口          : 5 个   (CRUD + 列表)
├─ 监测数据接口      : 5 个   (CRUD + 列表)
├─ 批量导入接口      : 1 个   (batch)
├─ 实时查询接口      : 3 个   (latest_data / alert_summary / history)
└─ 用户接口          : 2 个   (profiles / current)
────────────────────────────
   共计            : 29 个 REST API

文件生成：
├─ models.py (3个文件)     : ~20 KB (含UserProfile)
├─ serializers.py (3个)    : ~15 KB (含字段验证)
├─ views.py (3个)          : ~10 KB (含实时查询 + 权限检查)
├─ urls.py (4个)           : ~2.5 KB
├─ permissions.py          : ~1.5 KB (权限类)
├─ settings.py             : ~3 KB (JWT配置)
├─ migrations/             : ~25 KB (10+个迁移文件)
├─ API接口文档.md          : ~80 KB (详细说明)
├─ README.md               : ~60 KB (完整指南)
└─ Admin配置               : 完全中文化

认证系统：
├─ JWT Token验证          : ✅ 全局启用
├─ Token有效期            : access(1h) / refresh(7d)
├─ 用户档案自动创建       : ✅ 登录时get_or_create
├─ 三角色权限控制         : admin / monitor / viewer
└─ 权限检查               : Permission classes + 403响应

数据库：
├─ Structure (示例大坝)    : 1条
├─ MonitoringDevice (设备) : 可按需创建
├─ Point (测点)            : 可按需创建
├─ User (用户)             : 2+条 (admin + 测试用户)
├─ UserProfile (用户档案)  : 关联User
└─ MonitorData (监测数据)  : 可按需导入

部署就绪：
├─ CORS配置              : ✅ Django-cors-headers
├─ 数据库迁移            : ✅ SQLite3就绪
├─ Django Admin          : ✅ 数据管理界面
├─ API可视化             : ✅ DRF BrowsableAPIRenderer
└─ 生产部署指南          : 见API文档第9章
```

#### 下一步计划
- [ ] 前端项目初始化 (Vue3 + Vite + TypeScript)
- [ ] Cesium集成 (三维场景引擎)
- [ ] 大坝3D模型加载 (GLB/GLTF格式)
- [ ] 监测点可视化 (Entity + Label)
- [ ] 数据面板 (实时数值 + 时间序列图)
- [ ] 表单交互 (新增/编辑监测数据)
- [ ] 权限展示 (3种角色演示)
- [ ] 批量导入 (CSV解析)
- [ ] 答辩演示脚本

#### 时间统计
- **学习**：2h (Django/DRF基础)
- **编码**：3h (模型+序列化器+视图+路由)
- **测试+文档**：1h

---

### 2026-01-07（规划）

#### 前端初期（Week 1-2）
- [ ] Vue3项目创建 (npm create vite)
- [ ] 路由框架搭建 (Vue Router)
- [ ] UI组件库集成 (Element Plus)
- [ ] Cesium基础集成 (viewer容器)

#### Cesium开发（Week 2-3）
- [ ] 大坝3D模型加载
- [ ] 监测点定位 (cesium_world_coords)
- [ ] 点击交互事件
- [ ] 实时数据更新

#### 数据面板（Week 3-4）
- [ ] API集成 (Axios)
- [ ] 仪表盘布局 (当前值 + 状态)
- [ ] 时间序列图 (ECharts)
- [ ] 数据表格过滤

#### 完善和答辩（Week 4-5）
- [ ] 权限切换演示
- [ ] 批量导入功能
- [ ] 性能优化
- [ ] 答辩脚本准备

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

---

## 📝 开发规范

### 命名约定
```
模型类      : PascalCase  (Structure, MonitoringDevice)
数据库字段  : snake_case  (cesium_center_x, monitor_time)
API路由    : kebab-case  (/monitor-datas/, /user-profiles/)
Python函数  : snake_case  (get_cesium_coords, save_monitor_data)
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
curl -X POST http://localhost:8000/api/monitoring/monitor-datas/ \
  -H "Content-Type: application/json" \
  -d '{"point":1,"monitor_time":"2026-01-06T10:00:00Z","inverted_plumb_up_down":2.5}'
```

### 使用Postman
- 导入API文档中的请求示例
- 设置环境变量 `BASE_URL = http://localhost:8000/api`
- 逐个测试各接口

---

## 📋 课设材料清单

```
✅ 已完成：
├─ 需求分析文档 (README.md)
├─ 数据库ER图 (模型设计)
├─ API接口文档 (50KB详细文档)
├─ 源代码 (后端完整实现)
├─ 工作日志 (本README)
└─ 项目中间检查材料

🔄 进行中：
├─ 前端三维场景实现（CesiumViewer已就绪）
├─ JWT前后端联调
├─ 监测数据可视化组件
└─ 答辩PPT准备

📝 待开发功能：
├─ 登录/权限管理界面
├─ 大坝模型加载与定位
├─ 监测点三维标注
├─ 实时数据图表（ECharts集成）
└─ 响应式布局适配
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

### 推荐教程
- DRF序列化器深度讲解
- Cesium Entity与坐标系统
- Vue3 Composition API

### 相关项目参考
- Django示例项目
- Cesium官方demo
- Vue3 + Cesium集成示例

---

## 📞 常见问题

**Q: 后端怎样支持生产环境？**  
A: 需要配置PostgreSQL数据库、Gunicorn WSGI服务器、Nginx反向代理、Redis缓存等。

**Q: 权限控制何时实现？**  
A: 当前为设计阶段，代码暂未实现。可在前端通过role字段手动控制按钮显示，后端实现留作进阶优化。

**Q: 前端怎样调用后端API？**  
A: 使用Axios库，详见API文档第6.5章的JavaScript示例。

**Q: 如何进行性能优化？**  
A: 建立数据库索引、使用字段过滤、分页查询、缓存热数据等。详见API文档第8章。

---

## 🎉 致谢

感谢：
- Django社区提供的优秀框架
- 教授的课程指导和作业设计
- Stack Overflow的技术支持

---

**项目状态**: 🔄 开发中（后端✅ / 前端🔄）  
**最后更新**: 2026-01-06  
**预计完成**: 2026-01-底  
**总工时**: ~60小时 (规划)

