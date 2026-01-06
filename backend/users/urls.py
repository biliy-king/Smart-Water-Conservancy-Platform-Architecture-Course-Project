# users/urls.py
# 导入必要模块
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views  # 导入当前APP的views（包含UserProfileViewSet）

# 1. 创建DRF默认路由器
router = DefaultRouter()

# 2. 注册用户信息ViewSet，路由地址 -> "user-profiles"
router.register(r"user-profiles", views.UserProfileViewSet)

# 3. 定义当前APP的子路由
urlpatterns = [
    path("", include(router.urls)),
]