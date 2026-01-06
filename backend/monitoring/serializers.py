# monitoring/serializers.py
from rest_framework import serializers
from .models import MonitorData
# 导入已有的测点序列化器，用于嵌套返回测点信息（含Cesium全局坐标）
from water_structures.serializers import PointSerializer

class MonitorDataSerializer(serializers.ModelSerializer):
    # 自定义嵌套字段：返回测点完整信息（含cesium_world_coords全局坐标）
    # 前端无需额外请求测点接口，直接获取关联数据，优化对接体验
    point_info = PointSerializer(source="point", read_only=True)

    class Meta:
        model = MonitorData
        # 继续使用 fields = "__all__"，便捷返回所有字段+自定义嵌套字段
        fields = "__all__"
        # 关键：标记自动生成/自动计算的字段为只读，禁止前端修改
        # status：由save方法自动判断；create_time：自动生成，均无需手动干预
        read_only_fields = ("status", "create_time")