# Smart-Water-Conservancy-Platform-Architecture-Course-Project
No description，just a homework（߹‎ᯅ߹）
前端对接 JWT 强制登录的快速说明：

- 登录接口：POST `/api/users/login/`，Body JSON：`{"username":"账号","password":"密码"}`。返回 `tokens.access` 和 `tokens.refresh`，请前端保存。
- 携带凭证：所有受保护接口请求头加 `Authorization: Bearer <access_token>`。
- 当前用户：GET `/api/users/current/`（用于登录后拉取个人信息）。
- 刷新令牌：POST `/api/users/refresh/`，Body JSON：`{"refresh":"<refresh_token>"}`，返回新的 access/refresh。
- 401 处理：如 access 过期，先调用刷新接口；若刷新也失败，则引导重新登录。
- 建议：前端拦截 401 统一跳转登录页；登录成功后将 access 放入请求头，refresh 用于静默续期。

后端已全局启用 JWT 鉴权，未携带 token 访问受保护接口将返回 401。

## 权限划分

三种用户角色及权限：

| 角色 | 权限 | 说明 |
|------|------|------|
| **admin** | 读写删所有资源 | 系统管理员，可操作所有数据 |
| **monitor** | 读所有，写监测数据/设备/测点 | 监测员，可录入监测数据，不可修改大坝信息 |
| **viewer** | 仅读 | 数据查看者，只能读取数据，禁止写删 |

## 接口权限要求

- **大坝结构（Structures）**  
  - GET/POST/PUT/DELETE：仅 admin 可写，所有认证用户可读

- **监测设备（Devices）/测点（Points）**  
  - GET：所有认证用户可读
  - POST/PUT/DELETE：admin/monitor 可操作

- **监测数据（MonitorData）**  
  - GET：所有认证用户可读  
  - POST/PUT/DELETE：admin/monitor 可操作

- **用户信息**  
  - GET /api/users/current/：获取登录用户信息（所有认证用户）
  - GET /api/users/profiles/：查看用户档案列表（所有认证用户可读）