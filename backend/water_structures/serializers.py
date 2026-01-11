# water_structures/serializers.py
from rest_framework import serializers
from .models import Structure, MonitoringDevice, Point
from monitoring.utils import generate_baseline_value, get_unit_by_device_type, calculate_status, get_threshold

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
    
    # ===== 新增字段：单个测点详情增强 =====
    # 1. 单位信息
    unit = serializers.SerializerMethodField()
    # 2. 当前实时值
    current_value = serializers.SerializerMethodField()
    # 3. 当前状态
    current_status = serializers.SerializerMethodField()
    # 4. 相关阈值
    relevant_thresholds = serializers.SerializerMethodField()
    # 5. 最后更新时间
    last_update_time = serializers.SerializerMethodField()

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
    
    # ===== 新增方法：获取单位信息 =====
    def get_unit(self, obj):
        """根据设备类型返回对应单位"""
        return get_unit_by_device_type(obj.device.device_type)
    
    # ===== 新增方法：获取当前实时值 =====
    def get_current_value(self, obj):
        """获取当前实时值（虚拟数据）"""
        data = generate_baseline_value(obj.id)
        if data:
            return data.get('value')
        return None
    
    # ===== 新增方法：获取当前状态 =====
    def get_current_status(self, obj):
        """获取当前预警状态"""
        data = generate_baseline_value(obj.id)
        if data:
            return data.get('status')
        return 'unknown'
    
    # ===== 新增方法：获取相关阈值 =====
    def get_relevant_thresholds(self, obj):
        """获取设备类型对应的阈值（仅相关字段）"""
        return get_threshold(obj, obj.device.device_type)
    
    # ===== 新增方法：获取最后更新时间 =====
    def get_last_update_time(self, obj):
        """获取最后更新时间"""
        data = generate_baseline_value(obj.id)
        if data:
            return data.get('timestamp')
        return None
    
# 4. 阈值管理序列化器
class ThresholdSerializer(serializers.Serializer):
    """阈值管理序列化器"""
    device_type = serializers.CharField(source='device.device_type', read_only=True)
    unit = serializers.SerializerMethodField()
    
    # 根据设备类型，只返回相关的阈值字段
    water_level_upper = serializers.FloatField(required=False, allow_null=True)
    water_level_lower = serializers.FloatField(required=False, allow_null=True)
    displacement_upper = serializers.FloatField(required=False, allow_null=True)
    displacement_lower = serializers.FloatField(required=False, allow_null=True)
    settlement_upper = serializers.FloatField(required=False, allow_null=True)
    settlement_lower = serializers.FloatField(required=False, allow_null=True)
    
    def get_unit(self, obj):
        return get_unit_by_device_type(obj.device.device_type)
    
    def update(self, instance, validated_data):
        """更新阈值"""
        for field, value in validated_data.items():
            if field in ['water_level_upper', 'water_level_lower', 'displacement_upper', 
                        'displacement_lower', 'settlement_upper', 'settlement_lower']:
                setattr(instance, field, value)
        instance.save()
        return instance