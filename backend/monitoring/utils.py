# backend/monitoring/utils.py
import random
from datetime import datetime, timedelta
from django.utils import timezone
from .models import MonitorData
from water_structures.models import Point
from hydro_platform.config import MonitoringConfig

def get_field_name_by_device_type(device_type):
    """根据设备类型获取对应字段名"""
    mapping = {
        'water_level_upstream': 'water_level_upstream',
        'water_level_downstream': 'water_level_downstream',
        'inverted_plumb_left_right': 'inverted_plumb_left_right',
        'inverted_plumb_up_down': 'inverted_plumb_up_down',
        'tension_wire_up_down': 'tension_wire_up_down',
        'hydrostatic_leveling': 'hydrostatic_leveling_settlement',
    }
    return mapping.get(device_type)

def filter_special_markers(value):
    """过滤特殊标识值（-999.1/-999.2保留，但不用于计算）"""
    if value in [-999.1, -999.2]:
        return None  # 不参与计算
    return value

def apply_physical_bounds(value, device_type):
    """应用物理边界约束"""
    if value is None:
        return None
    bounds = MonitoringConfig.PHYSICAL_BOUNDS.get(device_type)
    if bounds:
        return max(bounds['min'], min(bounds['max'], value))
    return value

def generate_baseline_value(point_id):
    """
    生成虚拟实时值（历史最新值 + 随机波动）
    
    Args:
        point_id: 测点ID
        
    Returns:
        dict: {
            'value': 虚拟值,
            'timestamp': 时间戳,
            'source': 'baseline',
            'confidence': 0.7,
            'status': 'normal|warning|alarm'
        }
    """
    try:
        point = Point.objects.select_related('device').get(id=point_id)
        device_type = point.device.device_type
        field_name = get_field_name_by_device_type(device_type)
        
        if not field_name:
            return None
        
        # 获取最新历史数据
        latest_record = MonitorData.objects.filter(
            point=point
        ).exclude(
            **{f'{field_name}__isnull': True}
        ).order_by('-monitor_time').first()
        
        if not latest_record:
            return None
        
        # 获取基准值并过滤特殊标识
        base_value = getattr(latest_record, field_name)
        base_value = filter_special_markers(base_value)
        
        if base_value is None:
            return None
        
        # 计算波动范围
        fluctuation_range = MonitoringConfig.FLUCTUATION_RANGES.get(device_type, 0.03)
        fluctuation = base_value * random.uniform(-fluctuation_range, fluctuation_range)
        
        # 生成虚拟值并应用物理边界
        simulated_value = base_value + fluctuation
        simulated_value = apply_physical_bounds(simulated_value, device_type)
        
        # 判断状态
        status = calculate_status(point, simulated_value, device_type)
        
        return {
            'point_id': point_id,
            'point_code': point.point_code,
            'device_type': device_type,
            'field_name': field_name,
            'value': round(simulated_value, 2),
            'unit': get_unit_by_device_type(device_type),
            'timestamp': timezone.now().isoformat(),
            'source': 'baseline',
            'confidence': 0.7,
            'status': status,
            'threshold': get_threshold(point, device_type)
        }
    except Point.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error generating baseline value for point {point_id}: {e}")
        return None



def calculate_status(point, value, device_type):
    """计算预警状态"""
    if value is None:
        return 'unknown'
    
    # 根据设备类型获取阈值
    if 'water_level' in device_type:
        upper = point.water_level_upper
        lower = point.water_level_lower
    elif 'settlement' in device_type or 'hydrostatic' in device_type:
        upper = point.settlement_upper
        lower = point.settlement_lower
    else:
        upper = point.displacement_upper
        lower = point.displacement_lower
    
    if upper is None or lower is None:
        return 'normal'
    
    # 判断状态
    if value > upper * 2 or value < lower * 2:
        return 'alarm'
    elif value > upper or value < lower:
        return 'warning'
    else:
        return 'normal'

def get_threshold(point, device_type):
    """获取阈值配置"""
    if 'water_level' in device_type:
        return {
            'min': point.water_level_lower or 0,
            'max': point.water_level_upper or 100,
            'warning': point.water_level_upper,
            'critical': point.water_level_upper * 2 if point.water_level_upper else None
        }
    elif 'settlement' in device_type or 'hydrostatic' in device_type:
        return {
            'min': point.settlement_lower or -20,
            'max': point.settlement_upper or 20,
            'warning': point.settlement_upper,
            'critical': point.settlement_upper * 2 if point.settlement_upper else None
        }
    else:
        return {
            'min': point.displacement_lower or -50,
            'max': point.displacement_upper or 50,
            'warning': point.displacement_upper,
            'critical': point.displacement_upper * 2 if point.displacement_upper else None
        }

def get_unit_by_device_type(device_type):
    """获取单位"""
    if 'water_level' in device_type:
        return 'm'
    else:
        return 'mm'