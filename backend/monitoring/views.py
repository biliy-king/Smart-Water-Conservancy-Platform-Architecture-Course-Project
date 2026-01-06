# monitoring/views.py
from rest_framework import viewsets
from .models import MonitorData
from .serializers import MonitorDataSerializer
from water_structures.permissions import IsMonitorOrAdminForWrite

class MonitorDataViewSet(viewsets.ModelViewSet):
    # 查询所有监测数据，按监测时间倒序排列（最新数据在前）
    queryset = MonitorData.objects.all().order_by("-monitor_time")
    # 关联对应的序列化器
    serializer_class = MonitorDataSerializer
    permission_classes = [IsMonitorOrAdminForWrite]  # monitor/admin可录入数据