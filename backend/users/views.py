# users/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile
from .serializers import UserProfileSerializer
from .permissions import CanModifyUserPermission

# ==================== JWT认证接口（4个） ====================

@api_view(['POST'])
@permission_classes([AllowAny])  # 注册接口允许匿名访问
def register_view(request):
    """
    用户注册接口
    POST /api/users/register/
    请求体: {"username": "newuser", "password": "password123"}
    
    【答辩要点】
    1. 创建Django User对象（自动加密密码）
    2. 创建关联的UserProfile对象（默认角色为viewer）
    3. 返回JWT Token，注册后自动登录
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    # 参数校验
    if not username or not password:
        return Response({
            'success': False,
            'message': '用户名和密码不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查用户名是否已存在
    if User.objects.filter(username=username).exists():
        return Response({
            'success': False,
            'message': '用户名已存在'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 密码长度校验
    if len(password) < 6:
        return Response({
            'success': False,
            'message': '密码长度至少6位'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 创建用户（Django会自动加密密码）
        user = User.objects.create_user(
            username=username,
            password=password,
            is_active=True  # 默认激活
        )
        
        # 创建用户档案（默认角色为viewer）
        profile = UserProfile.objects.create(
            user=user,
            role='viewer'
        )
        
        # 生成JWT Token（注册后自动登录）
        refresh = RefreshToken.for_user(user)
        
        # 构建用户信息
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': profile.role,
            'phone': profile.phone,
            'department': profile.department,
        }
        
        return Response({
            'success': True,
            'message': '注册成功',
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': user_data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    
    权限控制：
    - 超级管理员：可以修改所有用户的权限
    - 普通管理员：只能修改 monitor 和 viewer 的权限，不能修改自己和其他管理员的权限
    - 其他用户：只能查看
    
    筛选和排序：
    - 支持按用户名搜索（search 参数）
    - 支持按角色筛选（role 参数）
    - 支持按创建时间、用户名等字段排序（ordering 参数）
    
    【答辩要点】
    - 使用 CanModifyUserPermission 进行细粒度权限控制
    - 使用 SearchFilter 和 DjangoFilterBackend 支持搜索和筛选
    - 使用 OrderingFilter 支持排序
    - ModelViewSet 自动提供 GET/POST/PUT/DELETE
    """
    queryset = UserProfile.objects.all().select_related('user').order_by("-create_time")
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, CanModifyUserPermission]
    
    # 配置筛选和排序
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role']  # 支持按角色筛选，例如：?role=admin
    search_fields = ['user__username', 'phone', 'department']  # 支持搜索用户名、电话、部门
    ordering_fields = ['create_time', 'user__username', 'role']  # 支持排序的字段
    ordering = ['-create_time']  # 默认排序（按创建时间降序）
    
    def update(self, request, *args, **kwargs):
        """
        更新用户信息（PUT）
        检查权限并验证是否可以修改角色
        """
        instance = self.get_object()
        
        # 检查权限（permission_classes 已经检查，但这里再次确认）
        if not self.check_update_permission(request, instance):
            return Response({
                'success': False,
                'message': '您没有权限修改此用户的权限'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 检查是否尝试修改角色为 admin（普通管理员不允许）
        new_role = request.data.get('role')
        if new_role == 'admin' and not request.user.is_superuser:
            # 如果目标用户原本不是 admin，尝试设置为 admin
            if instance.role != 'admin':
                return Response({
                    'success': False,
                    'message': '只有超级管理员可以设置或修改管理员权限'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        部分更新用户信息（PATCH）
        检查权限并验证是否可以修改角色
        """
        instance = self.get_object()
        
        # 检查权限
        if not self.check_update_permission(request, instance):
            return Response({
                'success': False,
                'message': '您没有权限修改此用户的权限'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 检查是否尝试修改角色为 admin（普通管理员不允许）
        if 'role' in request.data:
            new_role = request.data.get('role')
            if new_role == 'admin' and not request.user.is_superuser:
                # 如果目标用户原本不是 admin，尝试设置为 admin
                if instance.role != 'admin':
                    return Response({
                        'success': False,
                        'message': '只有超级管理员可以设置或修改管理员权限'
                    }, status=status.HTTP_403_FORBIDDEN)
        
        return super().partial_update(request, *args, **kwargs)
    
    def check_update_permission(self, request, instance):
        """
        检查是否有权限更新该用户
        """
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 非管理员用户不能修改任何权限
        try:
            user_profile = request.user.user_profile
            if user_profile.role != 'admin':
                return False
        except:
            return False
        
        # 普通管理员不能修改自己的权限
        if instance.user == request.user:
            return False
        
        # 普通管理员不能修改其他管理员的权限
        if instance.role == 'admin':
            return False
        
        # 普通管理员可以修改 monitor 和 viewer 的权限
        return True