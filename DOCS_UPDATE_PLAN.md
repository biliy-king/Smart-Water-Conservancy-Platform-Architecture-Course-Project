# README 更新清单

## 📝 建议的变更

### 1. **技术栈部分** - 更新数据库配置
**现状**: 显示 SQLite3（开发环境）
**建议**: 补充 MySQL 生产环置

```markdown
### 技术栈
| 层级 | 技术 | 版本 |
|------|------|------|
| **后端** | Django + DRF | 5.2.9 + 3.16.1 |
| **前端** | Vue 3 + Vite + Cesium | 3.5.25 + 7.2.4 + 1.136 |
| **数据库** | MySQL 8.0+ | 生产环境 |
| **数据库** | SQLite3 | 开发环境 |
| **HTTP客户端** | Axios | 1.13.2 |
| **跨域** | django-cors-headers | 4.9.0 |
| **数据导入** | openpyxl | 3.x |
```

### 2. **环境配置部分** - 添加 MySQL 配置说明
**现状**: 仅有 SQLite
**建议**: 添加 MySQL 配置步骤

```markdown
### 数据库配置

#### SQLite（开发环境）- 默认配置
```bash
# 无需额外配置，Django 自动创建 db.sqlite3
python manage.py migrate
```

#### MySQL（生产环境）
```bash
# 1. 安装 MySQL 驱动
pip install mysqlclient

# 2. 在 settings.py 中配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hydro_platform',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# 3. 执行迁移
python manage.py migrate

# 4. 导入监测数据（可选）
python import_monitor_data.py all
```
```

### 3. **快速开始部分** - 添加数据导入说明
**新增**: 监测数据导入工具说明

```markdown
### 数据导入

项目包含 **Excel → MySQL** 监测数据导入工具，可自动化导入大量监测数据。

#### 使用方法
```bash
# 进入后端目录
cd backend

# 查看所有选项
python import_monitor_data.py

# 全量导入（步骤1-5）
python import_monitor_data.py all

# 仅导入监测数据（假设设备/测点已存在）
python import_monitor_data.py 4

# 清除所有监测数据并重新导入
python import_monitor_data.py clean

# 查看导入统计
python import_monitor_data.py 5
```

#### 输入文件
- **Excel文件**: `backend/Excel/监测数据.xlsx`
- **包含四张表**:
  - 倒垂线（inverted plumb）
  - 静力水准（hydrostatic leveling）
  - 引张线（tension wire）
  - 水位（water level）

#### 输出结果
```
✅ 已导入 37,005 条监测数据
  - 倒垂线左右岸: 7,746 条
  - 倒垂线上下游: 7,744 条
  - 引张线: 6,055 条
  - 静力水准: 5,366 条
  - 上游水位: 5,065 条
  - 下游水位: 5,029 条
  ⚠️  异常标记: 163 条（-999.1/-999.2/-999.9）
```
```

### 4. **新增文档引用** - 指向数据库设计说明
**新增**: 在快速开始后添加

```markdown
## 📚 文档资源

| 文档 | 说明 |
|------|------|
| [API接口文档](./API接口文档.md) | 所有REST API 的完整说明（用户认证、大坝、设备、测点、监测数据）|
| [数据库设计说明](./DATABASE_DESIGN.md) | **新增** - 数据库表结构、字段、关系、示例SQL查询 |
| [环境配置指南](./docs/SETUP.md) | 开发/生产环境配置细节（可选） |
```

### 5. **项目统计部分** - 添加数据规模说明
**新增**: 在功能描述后补充

```markdown
### 数据规模
- **设备数量**: 58 个（6种类型）
- **监测测点**: 58 个
- **监测数据**: 37,005 条记录
- **时间跨度**: 2011-2024 年
- **数据库表数**: 15 张（含 Django 框架表）
- **业务表数**: 5 张（users、water_structures × 3、monitoring）
```

---

## 📄 API 文档建议变更

### 1. **新增章节** - 数据库模型与API映射
在 "目录" 后添加：
```markdown
## 附录 A. 数据库表与 API 对应关系

| 数据库表 | API 端点 | 说明 |
|---------|--------|------|
| water_structures_structure | `/water-structures/structures/` | 大坝信息 |
| water_structures_monitoringdevice | `/water-structures/devices/` | 监测设备 |
| water_structures_point | `/water-structures/points/` | 监测测点 |
| monitoring_monitordata | `/monitoring/data/` | 监测数据 |
| users_userprofile | `/users/profile/` | 用户扩展信息 |
```

### 2. **新增章节** - 监测数据的特殊值说明
在 "数据校验规则" 前添加：
```markdown
## 8. 监测数据特殊值

部分监测数据采用特殊负值标记数据异常，前端需要特别处理：

| 值 | 说明 | 处理方案 |
|----|------|--------|
| -999.1 | 低于标尺水位（无法读数） | 显示图标 "⚠️ 低于标尺" |
| -999.2 | 被遮挡无法观测 | 显示图标 "🚫 被遮挡" |
| -999.9 | 乱码数据（损坏） | 显示 "❌ 数据异常" |
| null | 该测点该时刻无测量 | 不显示数据点（图表留白） |

### 前端处理示例
```javascript
function formatMonitorValue(value) {
  if (value === -999.1) return { icon: '⚠️', text: '低于标尺', color: 'yellow' };
  if (value === -999.2) return { icon: '🚫', text: '被遮挡', color: 'orange' };
  if (value === -999.9) return { icon: '❌', text: '数据异常', color: 'red' };
  if (value === null) return null;  // 不显示
  return { icon: '✓', text: value.toFixed(2), color: 'green' };
}
```
```

### 3. **新增章节** - MySQL 数据库连接示例
在 API 快速开始后添加：
```markdown
## 附录 B. 直接数据库查询示例

对于需要直接查询 MySQL 的情况，可使用以下 SQL：

#### 获取大坝信息
```sql
SELECT * FROM water_structures_structure WHERE id = 1;
```

#### 获取所有设备及其状态
```sql
SELECT 
  md.device_name, 
  md.device_type, 
  md.device_status, 
  md.install_position,
  COUNT(DISTINCT mdata.id) as data_count
FROM water_structures_monitoringdevice md
LEFT JOIN water_structures_point p ON md.id = p.device_id
LEFT JOIN monitoring_monitordata mdata ON p.id = mdata.point_id
WHERE md.structure_id = 1
GROUP BY md.id
ORDER BY md.device_name;
```

#### 查询某测点的最新 50 条监测数据
```sql
SELECT md.monitor_time, md.inverted_plumb_left_right, md.water_level_upstream
FROM monitoring_monitordata md
WHERE md.point_id = 1
ORDER BY md.monitor_time DESC
LIMIT 50;
```

#### 统计异常数据
```sql
SELECT COUNT(*) as abnormal_count
FROM monitoring_monitordata
WHERE inverted_plumb_left_right IN (-999.1, -999.2, -999.9)
   OR water_level_upstream IN (-999.1, -999.2, -999.9)
   OR water_level_downstream IN (-999.1, -999.2, -999.9);
```
```

---

## 📋 修改总结

| 文件 | 变更数 | 主要内容 |
|------|--------|--------|
| README.md | 6 处 | 技术栈、MySQL配置、数据导入、文档链接、数据规模 |
| API接口文档.md | 3 处 | 表-API映射、特殊值说明、SQL示例 |
| DATABASE_DESIGN.md | 已生成 | 数据库完整设计说明（已独立文档） |

**建议执行顺序**:
1. ✅ 已生成 `DATABASE_DESIGN.md`
2. ⏳ 待执行：更新 `README.md`（6处）
3. ⏳ 待执行：更新 `API接口文档.md`（3处）

