# 项目总urls.py（如：your_project_name/urls.py）
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 原有Admin后台路由（保留不变，不影响你之前的Admin操作）
    path("admin/", admin.site.urls),
    
    # 1. 挂载water_structures APP的子路由，统一前缀：/api/water-structures/
    path("api/water-structures/", include("water_structures.urls")),
    
    # 2. 挂载monitoring APP的子路由，统一前缀：/api/monitoring/
    path("api/monitoring/", include("monitoring.urls")),
    
    # 3. 挂载users APP的子路由，统一前缀：/api/users/
    path("api/users/", include("users.urls")),
]