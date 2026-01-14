# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, 
    register_view,
    login_view, 
    refresh_token_view, 
    current_user_view
)

# 创建路由器
router = DefaultRouter()
router.register(r'user-profiles', UserProfileViewSet)

urlpatterns = [
    # ========== JWT认证接口 ==========
    path('register/', register_view, name='register'),        # POST /api/users/register/
    path('login/', login_view, name='login'),                  # POST /api/users/login/
    path('refresh/', refresh_token_view, name='refresh'),      # POST /api/users/refresh/
    path('current/', current_user_view, name='current'),       # GET /api/users/current/
    
    # ========== 用户管理接口 ==========
    path('', include(router.urls)),  # /api/users/profiles/
]