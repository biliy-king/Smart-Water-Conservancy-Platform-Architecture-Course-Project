#!/usr/bin/env python
"""
详细检查数据库中是否有重复的测点（point_code相同但ID不同）
使用原始SQL查询和Django ORM两种方式验证
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydro_platform.settings')
django.setup()

from water_structures.models import Point
from django.db import connection

def check_with_sql():
    """使用原始SQL查询检查重复"""
    print("\n" + "=" * 80)
    print("方法1: 使用原始SQL查询检查重复的point_code")
    print("=" * 80)
    
    with connection.cursor() as cursor:
        # 查询重复的point_code
        cursor.execute("""
            SELECT point_code, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM water_structures_point 
            GROUP BY point_code 
            HAVING COUNT(*) > 1
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("✅ SQL查询结果：未发现重复的point_code")
        else:
            print(f"⚠️  SQL查询发现 {len(results)} 个重复的point_code：\n")
            for row in results:
                point_code, count, ids = row
                print(f"  point_code: {point_code}")
                print(f"  重复次数: {count}")
                print(f"  ID列表: {ids}")
                print()
        
        return results

def check_with_orm():
    """使用Django ORM检查重复"""
    print("\n" + "=" * 80)
    print("方法2: 使用Django ORM检查重复的point_code")
    print("=" * 80)
    
    from collections import defaultdict
    
    all_points = Point.objects.all().select_related('device')
    total_count = all_points.count()
    
    print(f"数据库中共有 {total_count} 个测点记录")
    
    if total_count == 0:
        print("⚠️  数据库中没有测点记录！")
        return {}
    
    # 按point_code分组
    point_code_groups = defaultdict(list)
    for point in all_points:
        point_code_groups[point.point_code].append(point)
    
    # 找出重复的point_code
    duplicates = {code: points for code, points in point_code_groups.items() if len(points) > 1}
    
    if not duplicates:
        print("✅ ORM查询结果：未发现重复的point_code")
        return {}
    
    print(f"⚠️  ORM查询发现 {len(duplicates)} 个重复的point_code：\n")
    
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
    
    return duplicates

def show_all_points_summary():
    """显示所有测点的摘要信息"""
    print("\n" + "=" * 80)
    print("所有测点摘要（前20条）")
    print("=" * 80)
    
    points = Point.objects.all().select_related('device')[:20]
    count = Point.objects.count()
    
    print(f"数据库中共有 {count} 个测点记录（显示前20条）：\n")
    
    for point in points:
        device_name = point.device.device_name if point.device else "未绑定设备"
        print(f"  ID: {point.id:4d} | point_code: {point.point_code:20s} | 设备: {device_name}")

if __name__ == "__main__":
    print("=" * 80)
    print("详细检查重复的测点（point_code相同但ID不同）")
    print("=" * 80)
    
    # 显示摘要
    show_all_points_summary()
    
    # 方法1: SQL查询
    sql_results = check_with_sql()
    
    # 方法2: ORM查询
    orm_results = check_with_orm()
    
    # 总结
    print("\n" + "=" * 80)
    print("检查总结")
    print("=" * 80)
    
    if not sql_results and not orm_results:
        print("✅ 两种方法都确认：数据库中没有重复的point_code")
        print("\n建议：")
        print("1. 如果前端仍然遇到问题，可能是前端传递的point_id不正确")
        print("2. 检查前端代码中point_id的获取逻辑")
        print("3. 确认前端使用的point_id是否与数据库中的ID匹配")
    else:
        print("⚠️  发现重复记录，请根据上述信息选择需要保留的记录")
        print("\n建议：")
        print("1. 请检查上述重复记录，确定需要保留哪一个")
        print("2. 删除不需要的记录，确保每个point_code只对应一个ID")
        print("3. 如果数据库层面没有唯一约束，建议运行迁移以确保约束生效")
    
    print("=" * 80)
