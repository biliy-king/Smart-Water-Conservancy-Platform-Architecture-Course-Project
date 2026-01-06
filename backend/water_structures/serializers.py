# water_structures/serializers.py
from rest_framework import serializers
from .models import Structure, MonitoringDevice, Point

# 1. 大坝序列化器（返回大坝全局坐标，供Cesium加载模型）
class StructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Structure
        # 序列化所有字段，也可以指定具体字段：fields = ("id", "name", "cesium_center_x", ...)
        fields = "__all__"

# 2. 监测设备序列化器（返回设备基础信息）
class MonitoringDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoringDevice
        fields = "__all__"

# 3. 测点序列化器（核心：返回Cesium全局坐标，供前端布置测点）
class PointSerializer(serializers.ModelSerializer):
    # 新增只读字段：返回Cesium全局坐标（从Model的逻辑计算获取）
    cesium_world_coords = serializers.SerializerMethodField()
    # 嵌套设备信息（前端无需额外请求，直接获取设备详情，优化体验）
    device_info = MonitoringDeviceSerializer(source="device", read_only=True)

    class Meta:
        model = Point
        fields = "__all__"

    # 实现全局坐标的计算逻辑（和Model中的辅助属性一致，确保数据准确）
    def get_cesium_world_coords(self, obj):
        # 获取关联的大坝
        dam = obj.device.structure
        # 计算：大坝全局坐标 + 测点相对坐标 = 测点Cesium全局坐标
        return {
            "x": dam.cesium_center_x + obj.relative_x,
            "y": dam.cesium_center_y + obj.relative_y,
            "z": dam.cesium_center_z + obj.relative_z
        }