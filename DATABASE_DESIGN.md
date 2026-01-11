# 智慧水利监测平台 - 数据库设计说明

## 1. 数据库概览

| 项目 | 说明 |
|------|------|
| **数据库名** | `hydro_platform` |
| **数据库类型** | MySQL 8.0+ |
| **字符集** | utf8mb4（支持中文、emoji） |
| **排序规则** | utf8mb4_unicode_ci |
| **总表数** | 15 张（业务表 5 个 + Django 框架表 10 个） |

---

## 2. 核心业务表（5 张）

### 2.1 用户管理 - `auth_user`（Django 认证表）
**用途**: 存储系统用户的基本认证信息（用户名、密码、邮箱等）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK | 用户唯一标识 |
| username | varchar(150) | UNIQUE | 登录用户名 |
| password | varchar(128) | NOT NULL | 加密密码（Django PBKDF2） |
| email | varchar(254) | - | 用户邮箱 |
| first_name | varchar(150) | - | 名 |
| last_name | varchar(150) | - | 姓 |
| is_active | tinyint(1) | - | 是否激活（0=禁用，1=启用） |
| is_staff | tinyint(1) | - | 是否为员工（可进后台） |
| is_superuser | tinyint(1) | - | 是否为超级用户 |
| date_joined | datetime(6) | - | 注册时间 |
| last_login | datetime(6) | NULL | 最后登录时间 |

**示例数据**:
```sql
INSERT INTO auth_user (username, password, email, is_active, is_staff, is_superuser, date_joined) 
VALUES ('admin', 'pbkdf2_sha256$...', 'admin@example.com', 1, 1, 1, NOW());
```

---

### 2.2 用户扩展 - `users_userprofile`（自定义用户角色表）
**用途**: 扩展 Django 用户，添加角色、部门、电话等业务属性

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | bigint | PK | 扩展用户唯一标识 |
| user_id | int | FK(auth_user.id) UNI | 关联的 auth_user（一对一） |
| role | varchar(10) | NOT NULL | 用户角色：admin/monitor/viewer |
| phone | varchar(11) | NULL | 联系电话 |
| department | varchar(100) | NULL | 所属部门 |
| create_time | datetime(6) | NOT NULL | 账号创建时间 |

**角色说明**:
| 角色 | 权限 |
|------|------|
| admin | 管理员：可操作所有数据（新增/编辑/删除） |
| monitor | 监测员：可录入/修改/查看监测数据 |
| viewer | 查看者：仅可查看数据（只读） |

**关系**: `users_userprofile.user_id` → `auth_user.id` (一对一)

**查询完整用户信息示例**:
```sql
SELECT au.username, au.email, up.role, up.phone, up.department
FROM auth_user au
INNER JOIN users_userprofile up ON au.id = up.user_id
WHERE au.username = 'admin';
```

---

### 2.3 大坝信息 - `water_structures_structure`（静态数据）
**用途**: 存储大坝的基本信息和 Cesium 3D 配置（单条记录）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK | 大坝唯一标识 |
| name | varchar(100) | NOT NULL | 大坝名称（如"河海大坝"） |
| level | varchar(20) | - | 大坝等级（1级/2级/3级） |
| cesium_center_x | float | - | Cesium 3D 中心点 X 坐标（经度转换后或虚拟值） |
| cesium_center_y | float | - | Cesium 3D 中心点 Y 坐标（纬度转换后或虚拟值） |
| cesium_center_z | float | - | Cesium 3D 中心点 Z 坐标（高程） |
| cesium_heading | float | DEFAULT 0.0 | 大坝模型航向角（绕 Z 轴旋转）|
| cesium_pitch | float | DEFAULT 0.0 | 大坝模型俯仰角（绕 X 轴旋转） |
| cesium_roll | float | DEFAULT 0.0 | 大坝模型翻滚角（绕 Y 轴旋转） |
| cesium_scale | float | DEFAULT 1.0 | 大坝模型缩放比例（1=原始） |
| cesium_model_url | varchar(500) | NULL | Cesium 3D 模型文件路径（如"/static/models/dam.glb"） |

**说明**: 单一大坝场景，通常只有 **1 条记录**

**示例数据**:
```sql
INSERT INTO water_structures_structure 
(name, level, cesium_center_x, cesium_center_y, cesium_center_z, cesium_model_url)
VALUES ('河海大坝', '2级', 1000.0, 500.0, 100.0, '/static/models/dam.glb');
```

---

### 2.4 监测设备 - `water_structures_monitoringdevice`（动态数据）
**用途**: 存储所有监测设备的信息（倒垂线、静力水准、引张线、水位计等）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK | 设备唯一标识 |
| structure_id | int | FK(water_structures_structure.id) | 所属大坝 |
| device_name | varchar(100) | NOT NULL | 设备名称（如"IP1"、"TC1"、"EX1"） |
| device_type | varchar(50) | NOT NULL | 设备类型：inverted_plumb_left_right/inverted_plumb_up_down/hydrostatic_leveling/tension_wire/water_level_upstream/water_level_downstream |
| install_position | varchar(100) | NOT NULL | 安装位置（如"坝段1-左岸"） |
| install_time | date | NOT NULL | 安装时间 |
| device_status | varchar(20) | DEFAULT "running" | 设备状态：running/offline/maintenance |

**唯一约束**: (structure_id, install_position, device_type) - **不允许重复**

**设备类型说明**:
| device_type | 说明 |
|------|------|
| inverted_plumb_left_right | 倒垂线-左右岸位移 |
| inverted_plumb_up_down | 倒垂线-上下游位移 |
| hydrostatic_leveling | 静力水准沉降 |
| tension_wire | 引张线-上下游位移 |
| water_level_upstream | 水位计-上游 |
| water_level_downstream | 水位计-下游 |

**示例数据**:
```sql
INSERT INTO water_structures_monitoringdevice 
(structure_id, device_name, device_type, install_position, install_time, device_status)
VALUES 
(1, 'IP1', 'inverted_plumb_left_right', '坝段1-左岸', '2011-03-26', 'running'),
(1, 'TC1', 'hydrostatic_leveling', '坝段1中线', '2018-05-05', 'running');
```

---

### 2.5 监测测点 - `water_structures_point`（设备与数据的映射）
**用途**: 每个设备对应一个测点，用于存储该测点的配置（阈值、编码等）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK | 测点唯一标识 |
| device_id | int | FK(water_structures_monitoringdevice.id) OneToOne | 所属设备（一对一） |
| point_code | varchar(100) | NOT NULL UNIQUE | 测点编码（如"IP1-左右岸CH1"） |
| displacement_upper | float | NULL | 位移上限阈值（mm） |
| displacement_lower | float | NULL | 位移下限阈值（mm） |
| settlement_upper | float | NULL | 沉降上限阈值（mm） |
| settlement_lower | float | NULL | 沉降下限阈值（mm） |
| water_level_upper | float | NULL | 水位上限阈值（m） |
| water_level_lower | float | NULL | 水位下限阈值（m） |

**关系**: `water_structures_point.device_id` → `water_structures_monitoringdevice.id` (一对一)

**说明**: 每个设备只有一个测点，反之亦然。测点是数据录入时的"容器"。

**示例数据**:
```sql
INSERT INTO water_structures_point 
(device_id, point_code, displacement_upper, displacement_lower)
VALUES (1, 'IP1-左右岸CH1', 10.0, -10.0);
```

---

### 2.6 监测数据 - `monitoring_monitordata`（大数据量）
**用途**: 存储所有监测记录，是最重要的业务数据表（37000+ 条记录）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | int | PK | 记录唯一标识 |
| point_id | int | FK(water_structures_point.id) | 所属测点 |
| monitor_time | datetime(6) | NOT NULL | 监测时间 |
| inverted_plumb_left_right | float | NULL | 倒垂线-左右岸位移（mm） |
| inverted_plumb_up_down | float | NULL | 倒垂线-上下游位移（mm） |
| hydrostatic_leveling_settlement | float | NULL | 静力水准沉降（mm） |
| tension_wire_up_down | float | NULL | 引张线-上下游位移（mm） |
| water_level_upstream | float | NULL | 上游水位（m） |
| water_level_downstream | float | NULL | 下游水位（m） |

**唯一约束**: (point_id, monitor_time) - **同一测点同一时刻不允许重复**

**特殊值说明**:
| 值 | 说明 |
|----|------|
| -999.1 | 低于标尺水位（无法读数） |
| -999.2 | 被遮挡无法观测 |
| -999.9 | 乱码数据（无效） |
| NULL | 该测点该时刻无测量（不同设备间互不影响） |

**关系**: `monitoring_monitordata.point_id` → `water_structures_point.id` (多对一)

**示例数据**:
```sql
INSERT INTO monitoring_monitordata 
(point_id, monitor_time, inverted_plumb_left_right, inverted_plumb_up_down)
VALUES 
(1, '2024-12-31 00:00:00', 5.32, 3.14),
(2, '2024-12-31 00:00:00', -999.1, NULL);  -- -999.1 表示数据异常
```

**数据统计**（截至 2025-01-11）:
- 总记录数: **37,005 条**
- 倒垂线左右岸: 7,746 条
- 倒垂线上下游: 7,744 条
- 引张线: 6,055 条
- 静力水准: 5,366 条
- 上游水位: 5,065 条
- 下游水位: 5,029 条
- 异常标记: 163 条（需人工审核）

---

## 3. Django 框架表（10 张，非业务数据）

| 表名 | 用途 | 是否可删除 |
|------|------|---------|
| auth_group | 用户组管理 | ❌ 否（auth_user 依赖） |
| auth_group_permissions | 用户组权限 | ❌ 否（auth_group 依赖） |
| auth_permission | 权限定义 | ❌ 否（Django 框架必需） |
| auth_user_groups | 用户所属组 | ❌ 否（Django 框架必需） |
| auth_user_user_permissions | 用户权限 | ❌ 否（Django 框架必需） |
| django_admin_log | 后台操作日志 | ✅ 可删除（非核心） |
| django_content_type | 内容类型 | ❌ 否（Django ORM 必需） |
| django_migrations | 迁移历史 | ❌ 否（版本控制必需） |
| django_session | 会话数据 | ✅ 可删除（非核心） |

---

## 4. 表关系图

```
┌─────────────────────┐
│   auth_user         │  （Django 认证）
│ ┌─────────────────┐ │
│ │ id (PK)         │ │
│ │ username (UNI)  │ │
│ │ password        │ │
│ │ email           │ │
│ │ is_active       │ │
│ └─────────────────┘ │
└──────────┬──────────┘
           │
           │ 1:1
           │
           ▼
┌──────────────────────────┐
│ users_userprofile        │  （用户扩展）
│ ┌────────────────────────┤
│ │ id (PK)                 │
│ │ user_id (FK, UNI)       │ ──→ auth_user.id
│ │ role (admin/monitor)    │
│ │ phone, department       │
│ │ create_time             │
│ └────────────────────────┘
└──────────────────────────┘


┌──────────────────────────┐
│ water_structures         │  （大坝）
│ (1 条记录)               │
│ ┌────────────────────────┤
│ │ id (PK)                 │
│ │ name: "河海大坝"        │
│ │ level: "2级"            │
│ │ cesium_center_x/y/z     │
│ │ cesium_model_url        │
│ └────────────────────────┘
└──────────┬───────────────┘
           │
           │ 1:N
           │
           ▼
┌──────────────────────────────────┐
│ water_structures_monitoringdevice│  （设备 58 个）
│ ┌──────────────────────────────┐ │
│ │ id (PK)                      │ │
│ │ structure_id (FK)            │ │ ──→ water_structures.id
│ │ device_name: "IP1", "TC1"... │ │
│ │ device_type                  │ │
│ │ install_position (UNI)       │ │
│ │ install_time                 │ │
│ │ device_status                │ │
│ └──────────────────────────────┘ │
└──────────┬───────────────────────┘
           │
           │ 1:1
           │
           ▼
┌──────────────────────────────┐
│ water_structures_point       │  （测点 58 个）
│ ┌──────────────────────────┐ │
│ │ id (PK)                  │ │
│ │ device_id (FK, UNI)      │ │ ──→ monitoringdevice.id
│ │ point_code (UNI)         │ │
│ │ displacement_upper/lower │ │
│ │ settlement_upper/lower   │ │
│ │ water_level_upper/lower  │ │
│ └──────────────────────────┘ │
└──────────┬──────────────────┘
           │
           │ 1:N
           │
           ▼
┌──────────────────────────────────┐
│ monitoring_monitordata           │  （数据 37,005 条）
│ ┌──────────────────────────────┐ │
│ │ id (PK)                      │ │
│ │ point_id (FK)                │ │ ──→ point.id
│ │ monitor_time                 │ │
│ │ inverted_plumb_left_right    │ │
│ │ inverted_plumb_up_down       │ │
│ │ hydrostatic_leveling_...     │ │
│ │ tension_wire_up_down         │ │
│ │ water_level_upstream         │ │
│ │ water_level_downstream       │ │
│ │ (UNI: point_id + monitor_time)
│ └──────────────────────────────┘ │
└──────────────────────────────────┘
```

---

## 5. 核心查询示例

### 查询某用户的权限
```sql
SELECT au.username, up.role, up.department
FROM auth_user au
INNER JOIN users_userprofile up ON au.id = up.user_id
WHERE au.username = 'admin';
```

### 查询大坝的所有监测设备
```sql
SELECT md.id, md.device_name, md.device_type, md.install_position, md.device_status
FROM water_structures_monitoringdevice md
WHERE md.structure_id = 1
ORDER BY md.device_name;
```

### 查询某测点的最新 10 条监测数据
```sql
SELECT md.monitor_time, md.inverted_plumb_left_right, md.water_level_upstream
FROM monitoring_monitordata md
WHERE md.point_id = 1
ORDER BY md.monitor_time DESC
LIMIT 10;
```

### 查询某时间段内的所有监测数据
```sql
SELECT p.point_code, md.monitor_time, 
       md.inverted_plumb_left_right, md.inverted_plumb_up_down,
       md.hydrostatic_leveling_settlement, md.tension_wire_up_down,
       md.water_level_upstream, md.water_level_downstream
FROM monitoring_monitordata md
INNER JOIN water_structures_point p ON md.point_id = p.id
WHERE md.monitor_time >= '2024-12-01' AND md.monitor_time < '2024-12-31'
ORDER BY md.monitor_time DESC;
```

### 查询异常数据（需人工修正）
```sql
SELECT p.point_code, md.monitor_time, 
       md.inverted_plumb_left_right, md.inverted_plumb_up_down,
       md.water_level_upstream, md.water_level_downstream
FROM monitoring_monitordata md
INNER JOIN water_structures_point p ON md.point_id = p.id
WHERE md.inverted_plumb_left_right IN (-999.1, -999.2, -999.9)
   OR md.water_level_upstream IN (-999.1, -999.2, -999.9)
   OR md.water_level_downstream IN (-999.1, -999.2, -999.9)
ORDER BY md.monitor_time DESC;
```

---

## 6. 数据维护清单

| 任务 | 频率 | 说明 |
|------|------|------|
| 验证异常数据 | 周1次 | 检查 -999.1/9.2/9.9 标记的 163 条记录 |
| 检查设备状态 | 月1次 | 更新 device_status（offline/maintenance） |
| 备份 MySQL | 日1次 | 保证数据安全 |
| 清理日志表 | 月1次 | 删除 django_admin_log 过期记录（可选） |

---

## 7. 迁移信息

- **数据库版本**: MySQL 8.0.44
- **Django 版本**: 5.2+
- **初始化时间**: 2026-01-11
- **总数据量**: 37,005 监测记录 + 58 设备 + 58 测点 + 1 大坝

---

**文档生成时间**: 2026-01-11  
**维护者**: 智慧水利监测平台技术团队
