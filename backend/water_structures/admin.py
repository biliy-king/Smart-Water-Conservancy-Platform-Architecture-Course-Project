from django.contrib import admin
from .models import Structure, MonitoringDevice, Point

# 注册大坝模型
@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    # 后台列表显示的字段
    list_display = ("id", "name", "cesium_center_x", "cesium_center_y", "cesium_center_z", "create_time")
    # 可搜索的字段（方便快速查找，单一大坝可忽略，但保留扩展性）
    search_fields = ("name",)

# 注册监测设备模型
@admin.register(MonitoringDevice)
class MonitoringDeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "device_name", "device_type", "install_position", "device_status", "create_time")
    # 列表筛选器（方便按设备类型筛选）
    list_filter = ("device_type", "device_status")
    search_fields = ("device_name",)

# 注册测点模型
@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("id", "point_code", "device", "relative_x", "relative_y", "relative_z", "create_time")
    search_fields = ("point_code",)