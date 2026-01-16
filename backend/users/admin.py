from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "phone", "department", "create_time")
    list_filter = ("role",)
    search_fields = ("user__username",)
    
    def has_change_permission(self, request, obj=None):
        """
        检查是否有权限修改用户
        规则：
        1. 超级管理员可以修改所有用户
        2. 普通管理员不能修改自己的权限，也不能修改其他管理员的权限
        """
        if not obj:
            return True  # 列表页面
        
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 普通管理员不能修改自己的权限
        if obj.user == request.user:
            return False
        
        # 普通管理员不能修改其他管理员的权限
        if obj.role == 'admin':
            return False
        
        # 普通管理员可以修改 monitor 和 viewer 的权限
        return True
    
    def save_model(self, request, obj, form, change):
        """
        保存用户时进行权限检查
        """
        if change:  # 更新操作
            # 检查是否尝试将角色设置为 admin
            if 'role' in form.changed_data and obj.role == 'admin':
                if not request.user.is_superuser:
                    # 如果原本不是 admin，尝试设置为 admin
                    try:
                        original_obj = UserProfile.objects.get(pk=obj.pk)
                        if original_obj.role != 'admin':
                            messages.error(
                                request,
                                '只有超级管理员可以设置或修改管理员权限'
                            )
                            return  # 阻止保存
                    except UserProfile.DoesNotExist:
                        pass
        
        super().save_model(request, obj, form, change)