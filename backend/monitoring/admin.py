from django.contrib import admin
from .models import MonitorData

@admin.register(MonitorData)
class MonitorDataAdmin(admin.ModelAdmin):
    list_display = ("id", "point", "monitor_time", "status", "monitor_person", "create_time")
    list_filter = ("status", "monitor_time")
    search_fields = ("point__point_code",)  # 支持按测点编号搜索