# 智慧水利数字孪生平台

> 一个基于Django REST Framework + Vue3 + Cesium的现代化水利工程监测管理系统

![Python](https://img.shields.io/badge/Python-3.10.11-blue)
![Django](https://img.shields.io/badge/Django-5.2.9-darkgreen)
![DRF](https://img.shields.io/badge/DRF-3.16.1-lightgreen)
![License](https://img.shields.io/badge/License-Course%20Project-orange)

---

## 📋 项目简介

本项目是一个智慧水利数字孪生平台的课程设计实现，主要特色包括：

### 核心功能
- **三维数字孪生**：基于Cesium实现大坝三维模型和监测点空间可视化
- **实时监测数据管理**：支持6种设备类型、多种监测指标的数据采集和管理
- **智能预警系统**：自动判断监测数据的正常/预警/告警状态
- **多用户权限管理**：管理员/监测员/访客三种角色的权限隔离
- **高效数据录入**：支持单条和批量导入监测数据
- **完整REST API**：规范的后端接口设计，支持前后端分离

### 技术栈
| 层级 | 技术 | 版本 |
|------|------|------|
| **后端** | Django + DRF | 5.2.9 + 3.16.1 |
| **前端** | Vue3 + Cesium | (规划中) |
| **数据库** | SQLite3 | (开发环境) |
| **其他** | django-cors-headers | 4.9.0 |

---

## 🚀 快速开始

### 后端环境配置

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 执行迁移
python manage.py migrate

# 5. 创建超级用户（可选）
python manage.py createsuperuser

# 6. 启动开发服务器
python manage.py runserver
```

### 访问地址
- **API文档**: `http://localhost:8000/api/`
- **Django Admin**: `http://localhost:8000/admin/`
- **API详细文档**: 见项目根目录 `API接口文档.md`

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
├── frontend/                         # Vue3前端项目（规划中）
├── API接口文档.md                    # 完整的API文档
├── README.md                         # 本文件
└── 课设材料/                         # 课程设计相关材料
```

---

## 📚 核心模型设计

### 数据关系图

```
Structure (大坝) 1---* MonitoringDevice (设备) 1---* Point (监测点) 1---* MonitorData (数据)
                                                                          |
                                                                          └─-> 自动判断status
```

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
大坝信息    : /api/water-structures/structures/
监测设备    : /api/water-structures/devices/
监测点      : /api/water-structures/points/
监测数据    : /api/monitoring/monitor-datas/         (含批量导入)
用户管理    : /api/users/user-profiles/

每个资源支持：GET(查), POST(增), PUT(改), DELETE(删)
总计25个接口 + 1个批量接口 = 26个REST API
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

**2. 数据模型（5个）**
- ✅ **Structure** (大坝)：12字段，含Cesium三维参数
- ✅ **MonitoringDevice** (设备)：6种设备类型支持
- ✅ **Point** (监测点)：自动Cesium坐标计算
- ✅ **MonitorData** (数据)：6种指标 + 自动预警
- ✅ **UserProfile** (用户)：3种角色权限

**3. REST API (26个接口)**
- ✅ 5个ModelViewSet + CRUD操作
- ✅ 模块化路由设计（app-level）
- ✅ 分页、过滤、排序支持
- ✅ 批量导入接口 (POST /monitor-datas/batch/)

**4. Django Admin** 
- ✅ 5个模型注册 + 中文化
- ✅ 字段可读性优化
- ✅ 数据快速录入界面

**5. 完整API文档** (50KB)
- ✅ 1000+行详细文档
- ✅ 字段级说明表格（类型、必填、含义）
- ✅ 请求/响应示例 + JavaScript/Python示例
- ✅ **第6章**：数据校验规则（范围、唯一性、时间）
- ✅ **第7章**：权限说明（RBAC矩阵）
- ✅ curl命令行用例

**6. 版本管理**
- ✅ Git分支管理（后端分支 + merge到main）
- ✅ 冲突解决（db.sqlite3处理）
- ✅ .gitignore优化

#### 关键技术亮点
| 点 | 实现 |
|----|------|
| **嵌套序列化** | PointSerializer → device_info，MonitorDataSerializer → point_info → device_info |
| **自动计算字段** | SerializerMethodField实现cesium_world_coords，前端直接用无需计算 |
| **预警系统** | MonitorData.save()中自动判断，支持6种指标的阈值对比 |
| **模块化设计** | 3个app独立开发，便于团队合作 |
| **完整校验** | 字段范围、唯一性、时间约束全覆盖 |

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

文件生成：
├─ models.py (3个文件)     : ~18 KB
├─ serializers.py (3个)    : ~11 KB  
├─ views.py (3个)          : ~6 KB
├─ urls.py (4个)           : ~2 KB
├─ settings.py             : ~2.5 KB
├─ migrations/             : ~20 KB (9个迁移文件)
├─ API接口文档.md          : ~50 KB
└─ Admin配置               : 完全中文化

数据库：
├─ Structure (1条)         : 示例大坝
├─ 表结构创建              : 完成迁移
└─ Django ORM管理          : 即用状态
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
- ✅ TypeScript支持，开发体验好
- ✅ 与Cesium集成方案成熟
- ✅ 就业市场需求量大

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
├─ 前端代码实现
├─ 演示视频录制
└─ 答辩PPT准备

📝 需要补充：
├─ 部署说明 (Docker/生产配置)
├─ 性能测试报告
├─ 用户手册
└─ 系统架构图详解
```

---

## 🤝 技能收获

通过这个项目，你将学到：

| 技能 | 深度 | 应用场景 |
|------|------|--------|
| **Django/DRF** | ⭐⭐⭐⭐ | 后端API开发 |
| **数据库设计** | ⭐⭐⭐⭐ | 关系模型、ForeignKey、唯一约束 |
| **REST API设计** | ⭐⭐⭐⭐ | 接口规范、版本管理、文档化 |
| **权限管理** | ⭐⭐⭐ | RBAC、粒度控制 |
| **Vue3** | ⭐⭐⭐ (待完成) | 前端框架 |
| **Cesium** | ⭐⭐⭐ (待完成) | 三维可视化 |
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

