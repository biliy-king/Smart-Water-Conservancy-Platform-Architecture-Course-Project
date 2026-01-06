# water_structures/views.py
from rest_framework import viewsets
from .models import Structure, MonitoringDevice, Point
from .serializers import StructureSerializer, MonitoringDeviceSerializer, PointSerializer

# 大坝视图集（加载Cesium大坝模型的核心接口）
class StructureViewSet(viewsets.ModelViewSet):
    # 查询所有大坝数据（你目前是单一大坝，后续扩展多大坝也无需修改）
    queryset = Structure.objects.all().order_by("-id")  # 按id倒序，最新创建的大坝在前
    # 关联大坝序列化器
    serializer_class = StructureSerializer

# 监测设备视图集（完善数据关联，方便前端排查）
class MonitoringDeviceViewSet(viewsets.ModelViewSet):
    # 查询所有设备数据，按设备名称排序
    queryset = MonitoringDevice.objects.all().order_by("device_name")
    # 关联设备序列化器
    serializer_class = MonitoringDeviceSerializer

# 测点视图集（核心，对接Cesium布置测点）
class PointViewSet(viewsets.ModelViewSet):
    # 查询所有测点数据，按测点编号排序
    queryset = Point.objects.all().order_by("point_code")
    # 关联测点序列化器
    serializer_class = PointSerializer