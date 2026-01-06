# users/views.py
<<<<<<< HEAD
from rest_framework import viewsets
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    # 查询所有用户信息，按创建时间倒序排列
    queryset = UserProfile.objects.all().order_by("-create_time")
    # 关联对应的序列化器
=======
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import UserProfile
from .serializers import UserProfileSerializer

# ==================== JWT认证接口（3个） ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 【重点】登录接口允许匿名访问
def login_view(request):
    """
    用户登录接口（JWT版本）
    POST /api/users/login/
    请求体: {"username": "admin", "password": "password123"}
    
    【答辩要点】
    1. 使用 Django 内置 authenticate() 验证用户名密码
    2. 生成 JWT Token（access + refresh）
    3. 前端收到后存储到 localStorage，后续请求带在 Header 中
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    # 参数校验
    if not username or not password:
        return Response({
            'success': False,
            'message': '用户名和密码不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Django内置认证（自动加密密码比对）
    user = authenticate(username=username, password=password)
    
    if user is not None:
        if not user.is_active:
            return Response({
                'success': False,
                'message': '用户已被禁用'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 【核心】生成JWT Token
        refresh = RefreshToken.for_user(user)
        
        # 构建用户信息
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        
        # 获取/补齐用户档案（related_name=user_profile）
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'viewer'}
        )
        user_data.update({
            'role': profile.role,
            'phone': profile.phone,
            'department': profile.department,
        })
        
        return Response({
            'success': True,
            'message': '登录成功',
            'tokens': {
                'access': str(refresh.access_token),   # 访问Token（1小时有效）
                'refresh': str(refresh),                # 刷新Token（7天有效）
            },
            'user': user_data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': '用户名或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])  # 刷新Token不需要认证（用refresh token换新的access token）
def refresh_token_view(request):
    """
    刷新Token接口
    POST /api/users/refresh/
    请求体: {"refresh": "旧的refresh_token"}
    
    【答辩要点】
    当 access_token 过期时（1小时后），用 refresh_token 换取新的 access_token
    避免用户频繁登录，提升用户体验
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'success': False,
            'message': 'refresh token不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 验证并生成新Token
        refresh = RefreshToken(refresh_token)
        
        return Response({
            'success': True,
            'message': 'Token刷新成功',
            'tokens': {
                'access': str(refresh.access_token),  # 新的access token
                'refresh': str(refresh),               # 新的refresh token（轮换机制）
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Token无效或已过期'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 需要JWT认证
def current_user_view(request):
    """
    获取当前登录用户信息
    GET /api/users/current/
    请求头: Authorization: Bearer <access_token>
    
    【答辩要点】
    DRF的 JWTAuthentication 自动从请求头解析Token，验证后将用户注入到 request.user
    """
    user = request.user
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    }
    
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'viewer'}
    )
    user_data.update({
        'role': profile.role,
        'phone': profile.phone,
        'department': profile.department,
    })
    
    return Response({
        'success': True,
        'user': user_data
    }, status=status.HTTP_200_OK)


# ==================== 用户管理接口 ====================

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    用户档案管理（CRUD）
    
    【答辩要点】
    - 继承全局 IsAuthenticated 权限，必须携带有效JWT Token
    - ModelViewSet 自动提供 GET/POST/PUT/DELETE
    """
    queryset = UserProfile.objects.all().order_by("-create_time")
>>>>>>> 后端
    serializer_class = UserProfileSerializer