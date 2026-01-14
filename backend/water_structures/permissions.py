from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    """
    仅管理员可写删，其他角色只读
    """
    def has_permission(self, request, view):
        # 读操作全允许
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # 写删操作仅admin，需要登录
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            user_profile = request.user.user_profile
            return user_profile.role == 'admin'
        except:
            # 如果没有user_profile，只允许是超级用户
            return request.user.is_superuser


class IsMonitorOrAdminForWrite(BasePermission):
    """
    monitor/admin 可写删监测数据，viewer 只读
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # 写操作需要登录
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 如果是超级用户，直接允许
        if request.user.is_superuser:
            return True
        
        try:
            user_profile = request.user.user_profile
            return user_profile.role in ['monitor', 'admin']
        except:
            # 如果没有user_profile，拒绝写操作
            return False