# water_structures/views.py
from rest_framework import viewsets
from .models import Structure, MonitoringDevice, Point
from .serializers import StructureSerializer, MonitoringDeviceSerializer, PointSerializer
from .permissions import IsAdminOrReadOnly, IsMonitorOrAdminForWrite
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import PointSerializer, ThresholdSerializer
from .segment_manager import get_all_segments, get_segment_summary
from .serializers import SegmentSummarySerializer, SegmentDetailSerializer
from monitoring.models import MonitorData

# 大坝视图集（加载Cesium大坝模型的核心接口）
class StructureViewSet(viewsets.ModelViewSet):
    # 查询所有大坝数据（你目前是单一大坝，后续扩展多大坝也无需修改）
    queryset = Structure.objects.all().order_by("-id")  # 按id倒序，最新创建的大坝在前
    # 关联大坝序列化器
    serializer_class = StructureSerializer
    permission_classes = [IsAdminOrReadOnly]
    @action(detail=True, methods=["get"])
    def segments(self, request, pk=None):
        summaries = [s for s in get_all_segments() if s]
        serializer = SegmentSummarySerializer(summaries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="segments/(?P<segment_id>[^/.]+)")
    def segment_detail(self, request, pk=None, segment_id=None):
        summary = get_segment_summary(segment_id)
        if not summary:
            return Response({"detail": "segment not found"}, status=404)
        serializer = SegmentDetailSerializer(summary)
        return Response(serializer.data)

# 监测设备视图集（完善数据关联，方便前端排查）
class MonitoringDeviceViewSet(viewsets.ModelViewSet):
    # 查询所有设备数据，按设备名称排序
    queryset = MonitoringDevice.objects.all().order_by("device_name")
    # 关联设备序列化器
    serializer_class = MonitoringDeviceSerializer
    permission_classes = [IsMonitorOrAdminForWrite]

# 测点视图集（核心，对接Cesium布置测点）
class PointViewSet(viewsets.ModelViewSet):
    # 查询所有测点数据，按测点编号排序
    queryset = Point.objects.all().order_by("point_code")
    # 关联测点序列化器
    serializer_class = PointSerializer
    permission_classes = [IsMonitorOrAdminForWrite]
    
    @action(detail=True, methods=['get', 'put'], serializer_class=ThresholdSerializer)
    def thresholds(self, request, pk=None):
        """
        获取或修改单个测点的告警阈值
        GET /api/water-structures/points/{id}/thresholds/ - 获取阈值
        PUT /api/water-structures/points/{id}/thresholds/ - 修改阈值
        """
        point = self.get_object()
        
        if request.method == 'GET':
            serializer = self.get_serializer(point)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = self.get_serializer(point, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_data(self, request):
        """
        获取有监测数据的测点列表
        GET /api/water-structures/points/with_data/
        只返回至少有一条监测数据的测点
        """
        # 获取所有有监测数据的测点ID
        point_ids_with_data = MonitorData.objects.values_list('point_id', flat=True).distinct()
        
        # 获取这些测点的详细信息
        points = Point.objects.filter(id__in=point_ids_with_data).select_related('device', 'device__structure')
        
        serializer = self.get_serializer(points, many=True)
        return Response({
            'count': points.count(),
            'results': serializer.data
        })