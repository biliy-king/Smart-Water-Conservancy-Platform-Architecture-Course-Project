# users/views.py
from rest_framework import viewsets
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    # 查询所有用户信息，按创建时间倒序排列
    queryset = UserProfile.objects.all().order_by("-create_time")
    # 关联对应的序列化器
    serializer_class = UserProfileSerializer