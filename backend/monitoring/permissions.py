from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    """
    仅管理员可写删，其他角色只读
    """
    def has_permission(self, request, view):
        # 读操作全允许
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # 写删操作仅admin
        user_profile = request.user.user_profile
        return user_profile.role == 'admin'


class IsMonitorOrAdminForWrite(BasePermission):
    """
    monitor/admin 可写删监测数据，viewer 只读
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        user_profile = request.user.user_profile
        return user_profile.role in ['monitor', 'admin']