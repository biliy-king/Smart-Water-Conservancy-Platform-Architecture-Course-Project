# users/serializers.py
from rest_framework import serializers
from .models import UserProfile
# 导入Django自带的User模型，用于嵌套返回用户基础信息
from django.contrib.auth.models import User

# 先编写Django自带User模型的序列化器（简化版，只返回必要字段）
class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 针对User模型，也可使用 fields = "__all__"，此处简化返回核心字段
        fields = "__all__"
        # 标记用户状态、创建时间等为只读
        read_only_fields = ("is_active", "date_joined", "last_login")

class UserProfileSerializer(serializers.ModelSerializer):
    # 自定义嵌套字段：返回关联的用户基础信息
    user_basic_info = UserBasicSerializer(source="user", read_only=True)

    class Meta:
        model = UserProfile
        # 继续使用 fields = "__all__"，便捷返回所有字段+自定义嵌套字段
        fields = "__all__"
        # 标记自动生成的创建时间为只读
        read_only_fields = ("create_time",)