# monitoring/serializers.py
from rest_framework import serializers
from .models import MonitorData
# 导入已有的测点序列化器，用于嵌套返回测点信息（含Cesium全局坐标）
from water_structures.serializers import PointSerializer
from rest_framework import serializers

class RealtimeDataSerializer(serializers.Serializer):
    """虚拟实时数据序列化器"""
    point_id = serializers.IntegerField()
    point_code = serializers.CharField()
    device_type = serializers.CharField()
    field_name = serializers.CharField()
    value = serializers.FloatField()
    unit = serializers.CharField()
    timestamp = serializers.DateTimeField()
    source = serializers.CharField()  # baseline 或 ml
    confidence = serializers.FloatField()
    status = serializers.CharField()
    threshold = serializers.DictField()
    
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

    #增加数据校验逻辑
    def validate_monitor_time(self, value):
        """时间不能为空，自动处理时区"""
        if not value:
            raise serializers.ValidationError("监测时间不能为空")
        from django.utils import timezone
        if not timezone.is_aware(value):
            value = timezone.make_aware(value)
        return value

    def validate_point(self, value):
        """测点必存在"""
        if not value:
            raise serializers.ValidationError("关联测点不能为空")
        return value
    
    def validate_inverted_plumb_up_down(self, value):
        """位移值允许负数（表示不同方向），只做精度处理"""
        if value is not None:
            return round(value, 2)  # 只保留2位小数
        return value

    def validate_inverted_plumb_left_right(self, value):
        """左右岸位移：允许负数，精度处理"""
        if value is not None:
            return round(value, 2)
        return value

    def validate_tension_wire_up_down(self, value):
        """张线位移：允许负数，精度处理"""
        if value is not None:
            return round(value, 2)
        return value

    def validate_hydrostatic_leveling_settlement(self, value):
        """沉降值：允许负数（表示回弹），精度处理"""
        if value is not None:
            return round(value, 2)
        return value

    def validate_water_level_upstream(self, value):
        """上游水位：不能为负，精度处理"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("上游水位值不能为负数")
            return round(value, 3)  # 水位保留3位小数
        return value

    def validate_water_level_downstream(self, value):
        """下游水位：不能为负，精度处理"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("下游水位值不能为负数")
            return round(value, 3)  # 水位保留3位小数
        return value

    # 全局校验：同测点同时间不能重复
    def validate(self, attrs):
        point = attrs.get("point")
        monitor_time = attrs.get("monitor_time")
        current_instance = self.instance

        if not current_instance and point and monitor_time:
            if MonitorData.objects.filter(point=point, monitor_time=monitor_time).exists():
                raise serializers.ValidationError(f"测点「{point.point_code}」在「{monitor_time}」已存在数据，请勿重复录入")

        if current_instance and point and monitor_time:
            if MonitorData.objects.filter(point=point, monitor_time=monitor_time).exclude(id=current_instance.id).exists():
                raise serializers.ValidationError(f"测点「{point.point_code}」在「{monitor_time}」已被其他数据占用")

        return attrs
