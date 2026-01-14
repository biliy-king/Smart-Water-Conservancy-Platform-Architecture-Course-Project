# monitoring/views.py
from datetime import timedelta

from django.db.models import OuterRef, Subquery, Count, Case, When, FloatField, Q
from django.core.paginator import Paginator
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from .models import MonitorData
from .serializers import MonitorDataSerializer
from .utils import generate_baseline_value, get_field_name_by_device_type, get_unit_by_device_type
from water_structures.models import Point
from water_structures.permissions import IsMonitorOrAdminForWrite
from hydro_platform.config import MonitoringConfig

class MonitorDataViewSet(viewsets.ModelViewSet):
    """监测数据视图集"""
    queryset = MonitorData.objects.all().order_by("-monitor_time")
    serializer_class = MonitorDataSerializer
    permission_classes = [IsMonitorOrAdminForWrite]
    
    # 配置排序
    filter_backends = [OrderingFilter]
    ordering_fields = ['monitor_time', 'create_time', 'status', 'monitor_value']  # 支持的排序字段
    ordering = ['-monitor_time']  # 默认排序（按监测时间降序）

    def get_queryset(self):
        """重写查询集，支持筛选和混合设备类型的排序"""
        queryset = MonitorData.objects.all().select_related('point', 'point__device', 'point__device__structure')
        
        # 获取查询参数
        point_id = self.request.query_params.get('point')
        status = self.request.query_params.get('status')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        ordering_param = self.request.query_params.get('ordering')
        
        # 按测点筛选
        if point_id:
            try:
                point_id = int(point_id)
                queryset = queryset.filter(point_id=point_id)
            except (ValueError, TypeError):
                pass  # 如果point_id不是有效数字，忽略该筛选条件
        
        # 按状态筛选
        if status:
            queryset = queryset.filter(status=status)
        
        # 按时间范围筛选
        if start_time:
            queryset = queryset.filter(monitor_time__gte=start_time)
        if end_time:
            queryset = queryset.filter(monitor_time__lte=end_time)
        
        # 如果是按 monitor_value 排序，需要创建一个统一的排序字段
        if ordering_param and ('monitor_value' in ordering_param or '-monitor_value' in ordering_param):
            # 使用 Case/When 创建一个统一的指标值字段
            # COALESCE 用于合并所有可能的指标字段，返回第一个非空值
            from django.db.models import F
            queryset = queryset.annotate(
                monitor_value=Case(
                    When(point__device__device_type='inverted_plumb_up_down', then=F('inverted_plumb_up_down')),
                    When(point__device__device_type='inverted_plumb_left_right', then=F('inverted_plumb_left_right')),
                    When(point__device__device_type='tension_wire_up_down', then=F('tension_wire_up_down')),
                    When(point__device__device_type='hydrostatic_leveling', then=F('hydrostatic_leveling_settlement')),
                    When(point__device__device_type='water_level_upstream', then=F('water_level_upstream')),
                    When(point__device__device_type='water_level_downstream', then=F('water_level_downstream')),
                    default=None,
                    output_field=FloatField()
                )
            )
            
            # 处理排序方向
            if ordering_param.startswith('-'):
                queryset = queryset.order_by('-monitor_value', '-monitor_time')
            else:
                queryset = queryset.order_by('monitor_value', '-monitor_time')
        else:
            # 其他排序由 OrderingFilter 处理
            pass
        
        return queryset

    def create(self, request, *args, **kwargs):
        """新增监测数据"""
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
        """修改监测数据"""
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

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def latest_data(self, request):
        """获取每个测点最新一条数据"""
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

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def alert_summary(self, request):
        """获取预警汇总"""
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

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def history(self, request):
        """获取指定测点的历史数据"""
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


# ============ 虚拟实时数据接口 ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_data(request, point_id=None):
    """
    获取虚拟实时数据
    
    GET /api/monitoring/latest/ - 获取所有测点
    GET /api/monitoring/latest/{point_id}/ - 获取单个测点
    """
    try:
        if point_id:
            # 单个测点
            data = generate_baseline_value(point_id)
            if not data:
                return Response({
                    'success': False,
                    'message': f'测点 {point_id} 无可用数据'
                }, status=404)
            return Response({
                'success': True,
                'data': data
            })
        else:
            # 所有测点
            points = Point.objects.all()
            results = []
            for point in points:
                data = generate_baseline_value(point.id)
                if data:
                    results.append(data)
            
            return Response({
                'success': True,
                'count': len(results),
                'data': results
            })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取实时数据失败：{str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history_data(request, point_id):
    """
    获取历史数据（真实值，允许缺口）
    
    GET /api/monitoring/history/{point_id}/?days=7&page=1&size=100
    """
    try:
        point = Point.objects.get(id=point_id)
        device_type = point.device.device_type
        field_name = get_field_name_by_device_type(device_type)
        
        if not field_name:
            return Response({
                'success': False,
                'message': '无效的设备类型'
            }, status=400)
        
        # 参数解析
        days = int(request.query_params.get('days', 7))
        page = int(request.query_params.get('page', 1))
        size = int(request.query_params.get('size', 100))
        
        # 查询历史数据
        # 先尝试查询最近N天的数据
        start_time = timezone.now() - timedelta(days=days)
        
        queryset = MonitorData.objects.filter(
            point=point,
            monitor_time__gte=start_time
        ).exclude(
            **{f'{field_name}__isnull': True}
        ).order_by('-monitor_time')
        
        # 如果最近N天没有数据，则返回该监测点最新的记录
        if not queryset.exists():
            queryset = MonitorData.objects.filter(
                point=point
            ).exclude(
                **{f'{field_name}__isnull': True}
            ).order_by('-monitor_time')
        
        # 分页
        paginator = Paginator(queryset, size)
        page_obj = paginator.get_page(page)
        
        # 序列化
        records = []
        for record in page_obj:
            value = getattr(record, field_name)
            records.append({
                'monitor_time': record.monitor_time.isoformat(),
                'value': value,
                'status': record.status,
                'is_special_marker': value in [-999.1, -999.2]
            })
        
        return Response({
            'success': True,
            'data': {
                'point_code': point.point_code,
                'device_type': device_type,
                'unit': get_unit_by_device_type(device_type),
                'records': records,
                'pagination': {
                    'total': paginator.count,
                    'page': page,
                    'size': size,
                    'total_pages': paginator.num_pages
                }
            }
        })
    except Point.DoesNotExist:
        return Response({
            'success': False,
            'message': f'测点 {point_id} 不存在'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取历史数据失败：{str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_alert_summary(request):
    """
    获取预警摘要
    
    GET /api/monitoring/alerts/
    """
    try:
        points = Point.objects.all()
        
        total_alerts = 0
        critical_count = 0
        warning_count = 0
        normal_count = 0
        alert_list = []
        
        for point in points:
            data = generate_baseline_value(point.id)
            if data:
                status = data['status']
                if status == 'alarm':
                    critical_count += 1
                    total_alerts += 1
                    alert_list.append(data)
                elif status == 'warning':
                    warning_count += 1
                    total_alerts += 1
                    alert_list.append(data)
                else:
                    normal_count += 1
        
        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_alerts': total_alerts,
                    'critical': critical_count,
                    'warning': warning_count,
                    'normal': normal_count
                },
                'alert_list': alert_list[:10]
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取预警摘要失败：{str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([])  # 允许无认证访问
def health_check(request):
    """
    健康检查接口（无需认证）
    """
    return Response({
        'status': 'ok',
        'service': 'monitoring',
        'timestamp': timezone.now().isoformat(),
        'ml_enabled': MonitoringConfig.USE_ML_PREDICTION
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics_view(request):
    """
    获取监测数据统计概览
    GET /api/monitoring/statistics/
    
    返回：
    - total_points: 总测点数
    - normal_count: 正常状态测点数
    - warning_count: 警告状态测点数
    - alarm_count: 严重告警测点数
    - device_type_distribution: 各设备类型的测点数分布
    """
    
    points = Point.objects.all().select_related('device')
    total_points = points.count()
    
    # 统计各状态的测点数
    normal_count = 0
    warning_count = 0
    alarm_count = 0
    
    # 统计设备类型分布
    device_type_dist = {}
    
    for point in points:
        # 获取该测点的实时状态
        data = generate_baseline_value(point.id)
        device_type = point.device.device_type
        
        # 累计设备类型计数
        device_type_dist[device_type] = device_type_dist.get(device_type, 0) + 1
        
        # 统计状态
        if data:
            status = data.get('status')
            if status == 'normal':
                normal_count += 1
            elif status == 'warning':
                warning_count += 1
            elif status == 'alarm':
                alarm_count += 1
    
    return Response({
        'total_points': total_points,
        'status_distribution': {
            'normal': normal_count,
            'warning': warning_count,
            'alarm': alarm_count,
        },
        'device_type_distribution': device_type_dist,
        'timestamp': timezone.now().isoformat()
    })