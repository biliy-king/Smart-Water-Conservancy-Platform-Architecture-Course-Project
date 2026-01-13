DAM_SEGMENTS = {
    "1": {"name": "1号坝段", "order": 1},
    "2": {"name": "2号坝段", "order": 2},
    "3": {"name": "3号坝段", "order": 3},
    "4": {"name": "4号坝段", "order": 4},
    "5": {"name": "5号坝段", "order": 5},
    "6": {"name": "6号坝段", "order": 6},
    "7": {"name": "7号坝段", "order": 7},
    "8": {"name": "8号坝段", "order": 8},
    "9": {"name": "9号坝段", "order": 9},
    "10": {"name": "10号坝段", "order": 10},
}

def get_segment_id_from_position(position_str):
    if not position_str:
        return None
    import re
    nums = re.findall(r'\d+', position_str)
    if not nums:
        return None
    seg_id = nums[0]
    return seg_id if seg_id in DAM_SEGMENTS else None

def get_devices_by_segment(segment_id, queryset=None):
    from .models import MonitoringDevice
    qs = queryset or MonitoringDevice.objects.all()
    # 允许形如 “1号坝段-IP1” 或 “坝段1-左岸” 等写法，匹配数字即可
    return qs.filter(install_position__regex=rf".*{segment_id}\D*号?坝段?.*")

def get_points_by_segment(segment_id, queryset=None):
    from .models import Point
    qs = queryset or Point.objects.all()
    # 通过设备的安装位置推断所属坝段，同样使用宽松正则
    return qs.filter(device__install_position__regex=rf".*{segment_id}\D*号?坝段?.*")

def get_segment_summary(segment_id):
    from monitoring.utils import generate_baseline_value
    seg = DAM_SEGMENTS.get(segment_id)
    if not seg:
        return None
    devices = get_devices_by_segment(segment_id)
    points = get_points_by_segment(segment_id)
    warning_count, normal_count = 0, 0
    for p in points:
        data = generate_baseline_value(p.id)
        if data and data.get("status") == "warning":
            warning_count += 1
        else:
            normal_count += 1
    return {
        "segment_id": segment_id,
        "segment_name": seg["name"],
        "device_count": devices.count(),
        "point_count": points.count(),
        "warning_count": warning_count,
        "normal_count": normal_count,
        "has_warning": warning_count > 0,
        "devices": devices,
        "points": points,
    }

def get_all_segments():
    return [get_segment_summary(k) for k in sorted(DAM_SEGMENTS.keys(), key=int)]