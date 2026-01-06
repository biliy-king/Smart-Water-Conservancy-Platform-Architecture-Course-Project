# monitoring/views.py
<<<<<<< HEAD
from rest_framework import viewsets
from .models import MonitorData
from .serializers import MonitorDataSerializer
=======
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery, Count
from rest_framework import viewsets
from .models import MonitorData
from .serializers import MonitorDataSerializer
from water_structures.permissions import IsMonitorOrAdminForWrite
>>>>>>> 后端

class MonitorDataViewSet(viewsets.ModelViewSet):
    # 查询所有监测数据，按监测时间倒序排列（最新数据在前）
    queryset = MonitorData.objects.all().order_by("-monitor_time")
    # 关联对应的序列化器
<<<<<<< HEAD
    serializer_class = MonitorDataSerializer
=======
    serializer_class = MonitorDataSerializer
    permission_classes = [IsMonitorOrAdminForWrite]  # monitor/admin可录入数据

    def create(self, request, *args, **kwargs):
        """新增监测数据，统一返回格式"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "success": True,
                "message": "监测数据录入成功",
                "data": serializer.data
            }, status=201)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"监测数据录入失败：{str(e)}",
                "data": None
            }, status=400)

    def update(self, request, *args, **kwargs):
        """修改监测数据，统一返回格式"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "success": True,
                "message": "监测数据修改成功",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"监测数据修改失败：{str(e)}",
                "data": None
            }, status=400)


    # 实时数据：每个测点最新一条，支持按大坝/测点筛选，供大屏实时面板
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def latest_data(self, request):
        structure_id = request.query_params.get("structure_id")
        point_id = request.query_params.get("point_id")

        base_qs = MonitorData.objects.select_related("point", "point__device", "point__device__structure")
        if structure_id:
            base_qs = base_qs.filter(point__device__structure_id=structure_id)
        if point_id:
            base_qs = base_qs.filter(point_id=point_id)

        latest_sub = (
            base_qs.filter(point_id=OuterRef("point_id"))
                  .order_by("-monitor_time", "-id")
                  .values("id")[:1]
        )
        latest_qs = base_qs.filter(id__in=Subquery(latest_sub)).order_by("point_id")
        data = MonitorDataSerializer(latest_qs, many=True).data
        return Response({"success": True, "data": data})

    # 预警汇总：按状态统计，并给出各大坝分布，供预警面板
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def alert_summary(self, request):
        structure_id = request.query_params.get("structure_id")
        qs = MonitorData.objects.select_related("point__device__structure")
        if structure_id:
            qs = qs.filter(point__device__structure_id=structure_id)

        status_counts = qs.values("status").annotate(count=Count("id"))
        status_dict = {item["status"]: item["count"] for item in status_counts}

        structure_counts = (
            qs.values("point__device__structure_id", "point__device__structure__name")
              .annotate(count=Count("id"))
              .order_by("-count")
        )

        return Response({
            "success": True,
            "summary": {
                "status": status_dict,
                "structures": [
                    {
                        "structure_id": item["point__device__structure_id"],
                        "structure_name": item["point__device__structure__name"],
                        "count": item["count"],
                    } for item in structure_counts
                ],
            },
        })

    # 历史趋势：指定测点+时间范围，按时间正序返回，用于趋势图
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def history(self, request):
        point_id = request.query_params.get("point_id")
        start_time = request.query_params.get("start_time")
        end_time = request.query_params.get("end_time")

        if not point_id:
            return Response({"success": False, "message": "point_id 必填"}, status=400)

        qs = (MonitorData.objects.filter(point_id=point_id)
              .select_related("point", "point__device", "point__device__structure")
              .order_by("monitor_time"))
        if start_time:
            qs = qs.filter(monitor_time__gte=start_time)
        if end_time:
            qs = qs.filter(monitor_time__lte=end_time)

        data = MonitorDataSerializer(qs, many=True).data
        return Response({"success": True, "data": data})
    
    
>>>>>>> 后端
