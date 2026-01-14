from rest_framework.permissions import BasePermission

class CanModifyUserPermission(BasePermission):
    """
    用户权限修改权限控制
    
    规则：
    1. 超级管理员（superuser）可以修改所有用户的权限
    2. 普通管理员（admin role）不能修改自己的权限，也不能修改其他管理员的权限
    3. 普通管理员只能修改 monitor 和 viewer 角色的权限
    4. 非管理员用户不能修改任何权限
    """
    
    def has_permission(self, request, view):
        # GET、HEAD、OPTIONS 操作允许所有已认证用户
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # POST（创建）操作：只有管理员可以创建用户
        if request.method == 'POST':
            if not request.user or not request.user.is_authenticated:
                return False
            # 超级管理员或普通管理员都可以创建用户
            if request.user.is_superuser:
                return True
            try:
                user_profile = request.user.user_profile
                return user_profile.role == 'admin'
            except:
                return False
        
        # PUT、PATCH、DELETE 操作需要进一步检查（在 has_object_permission 中）
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        检查是否有权限修改特定用户对象
        
        obj 是 UserProfile 实例
        """
        # GET、HEAD、OPTIONS 操作允许所有已认证用户
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
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
        if obj.user == request.user:
            return False
        
        # 普通管理员不能修改其他管理员的权限
        if obj.role == 'admin':
            return False
        
        # 普通管理员可以修改 monitor 和 viewer 的权限
        return True
