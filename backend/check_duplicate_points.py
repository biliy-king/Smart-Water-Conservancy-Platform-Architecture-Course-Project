#!/usr/bin/env python
"""
检查数据库中是否有重复的测点（point_code相同但ID不同）
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydro_platform.settings')
django.setup()

from water_structures.models import Point
from collections import defaultdict

def check_duplicate_points():
    """检查重复的point_code"""
    print("=" * 80)
    print("检查重复的测点（point_code相同但ID不同）")
    print("=" * 80)
    
    # 使用Django ORM查询所有测点
    all_points = Point.objects.all().select_related('device')
    
    # 按point_code分组
    point_code_groups = defaultdict(list)
    for point in all_points:
        point_code_groups[point.point_code].append(point)
    
    # 找出重复的point_code
    duplicates = {code: points for code, points in point_code_groups.items() if len(points) > 1}
    
    if not duplicates:
        print("\n✅ 未发现重复的测点！所有point_code都是唯一的。")
        return
    
    print(f"\n⚠️  发现 {len(duplicates)} 个重复的point_code：\n")
    
    # 显示详细信息
    for point_code, points in sorted(duplicates.items()):
        print(f"\n{'=' * 80}")
        print(f"重复的point_code: {point_code}")
        print(f"共有 {len(points)} 条记录：")
        print("-" * 80)
        
        for idx, point in enumerate(points, 1):
            device_name = point.device.device_name if point.device else "未绑定设备"
            print(f"\n  记录 {idx}:")
            print(f"    ID: {point.id}")
            print(f"    设备名称: {device_name}")
            print(f"    设备ID: {point.device.id if point.device else 'N/A'}")
            print(f"    坐标: ({point.relative_x}, {point.relative_y}, {point.relative_z})")
            print(f"    创建时间: {point.create_time}")
            print(f"    位移阈值: 上限={point.displacement_upper}, 下限={point.displacement_lower}")
            print(f"    沉降阈值: 上限={point.settlement_upper}, 下限={point.settlement_lower}")
            print(f"    水位阈值: 上限={point.water_level_upper}, 下限={point.water_level_lower}")
    
    print("\n" + "=" * 80)
    print("\n建议：")
    print("1. 请检查上述重复记录，确定需要保留哪一个")
    print("2. 删除不需要的记录，确保每个point_code只对应一个ID")
    print("3. 如果数据库层面没有唯一约束，建议运行迁移以确保约束生效")
    print("=" * 80)
    
    return duplicates

if __name__ == "__main__":
    check_duplicate_points()
