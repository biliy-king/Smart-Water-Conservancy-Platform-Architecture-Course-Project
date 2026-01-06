# water_structures/urls.py
# 导入必要模块
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views  # 导入当前APP的views（包含3个ViewSet）

# 1. 创建DRF默认路由器（自动生成RESTful接口）
router = DefaultRouter()

# 2. 注册3个ViewSet，对应3个接口（路由地址+ViewSet）
# 大坝接口：路由地址 -> "structures"，对应视图集 -> StructureViewSet
router.register(r"structures", views.StructureViewSet)
# 设备接口：路由地址 -> "devices"，对应视图集 -> MonitoringDeviceViewSet
router.register(r"devices", views.MonitoringDeviceViewSet)
# 测点接口：路由地址 -> "points"，对应视图集 -> PointViewSet
router.register(r"points", views.PointViewSet)

# 3. 定义当前APP的子路由（挂载路由器）
urlpatterns = [
    # 把路由器生成的所有接口，挂载到当前APP的子路由根路径
    path("", include(router.urls)),
]