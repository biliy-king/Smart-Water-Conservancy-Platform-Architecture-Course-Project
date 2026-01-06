from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    用户扩展表（调整点：删除多对多大坝权限关联，简化为角色判断）
    说明：单一大坝场景下，权限只需区分“能否访问该大坝数据”，无需选择具体大坝
    """
    # 一对一关联Django自带User表
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="user_profile", 
        verbose_name="关联系统用户"
    )
    # 用户角色：简化权限判断，单一大坝下直接按角色控制访问
    ROLE_CHOICES = [
        ("admin", "系统管理员（可操作所有数据）"),
        ("monitor", "监测员（可录入/查看数据）"),
        ("viewer", "数据查看者（仅可查看数据）"),
    ]
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default="viewer", 
        verbose_name="用户角色"
    )
    # 删除多对多的accessible_structures（单一大坝无需授权选择）
    # 补充用户基础信息（可选）
    phone = models.CharField(
        max_length=11, 
        null=True, 
        blank=True, 
        verbose_name="联系电话"
    )
    department = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="所属部门"
    )
    create_time = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="账号创建时间"
    )

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __str__(self):
        return f"{self.user.username}（{self.get_role_display()}）"

    def has_access_to_dam_data(self):
        """
        【辅助方法】判断用户是否有权访问大坝数据（单一大坝场景专用）
        返回：True（有权访问）/False（无权访问）
        用途：前端数据展示、后端接口权限校验
        """
        # 所有角色都可查看数据，仅管理员可操作数据（可根据需求调整）
        return self.role in ["admin", "monitor", "viewer"]