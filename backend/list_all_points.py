#!/usr/bin/env python
"""
列出所有测点的详细信息，帮助选择需要的point_id
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydro_platform.settings')
django.setup()

from water_structures.models import Point

def list_all_points():
    """列出所有测点的详细信息"""
    print("=" * 100)
    print("所有测点详细信息列表")
    print("=" * 100)
    
    points = Point.objects.all().select_related('device').order_by('point_code')
    total = points.count()
    
    print(f"\n数据库中共有 {total} 个测点记录\n")
    print("-" * 100)
    print(f"{'ID':<6} | {'point_code':<30} | {'设备名称':<20} | {'设备ID':<8} | {'坐标(X,Y,Z)':<25}")
    print("-" * 100)
    
    for point in points:
        device_name = point.device.device_name if point.device else "未绑定"
        device_id = point.device.id if point.device else "N/A"
        coords = f"({point.relative_x:.2f},{point.relative_y:.2f},{point.relative_z:.2f})"
        
        print(f"{point.id:<6} | {point.point_code:<30} | {device_name:<20} | {device_id!s:<8} | {coords:<25}")
    
    print("-" * 100)
    print(f"\n总计: {total} 个测点")
    print("\n提示：")
    print("1. 如果前端需要根据point_code查找point_id，可以使用上述对应关系")
    print("2. 如果前端需要根据设备名称查找point_id，也可以使用上述对应关系")
    print("3. 建议前端使用point_code作为唯一标识，而不是point_id")
    print("=" * 100)

if __name__ == "__main__":
    list_all_points()
