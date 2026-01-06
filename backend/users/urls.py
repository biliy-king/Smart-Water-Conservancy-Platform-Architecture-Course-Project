# users/urls.py
<<<<<<< HEAD
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
=======
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, 
    login_view, 
    refresh_token_view, 
    current_user_view
)

# 创建路由器
router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)

urlpatterns = [
    # ========== JWT认证接口 ==========
    path('login/', login_view, name='login'),                  # POST /api/users/login/
    path('refresh/', refresh_token_view, name='refresh'),      # POST /api/users/refresh/
    path('current/', current_user_view, name='current'),       # GET /api/users/current/
    
    # ========== 用户管理接口 ==========
    path('', include(router.urls)),  # /api/users/profiles/
>>>>>>> 后端
]