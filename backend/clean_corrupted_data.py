import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydro_platform.settings')
django.setup()

from monitoring.models import MonitorData
from django.db.models import Q

# 查找所有乱码数据（-999.9）
anomaly_records = MonitorData.objects.filter(
    Q(inverted_plumb_left_right=-999.9) | Q(inverted_plumb_up_down=-999.9) |
    Q(tension_wire_up_down=-999.9) | Q(hydrostatic_leveling_settlement=-999.9) |
    Q(water_level_upstream=-999.9) | Q(water_level_downstream=-999.9)
)

count = anomaly_records.count()
print(f'【删除前统计】')
print(f'乱码数据总数: {count}')

if count > 0:
    print(f'\n【样例数据】')
    for record in anomaly_records[:5]:
        fields = []
        if record.inverted_plumb_left_right == -999.9:
            fields.append(f'左右=-999.9')
        if record.inverted_plumb_up_down == -999.9:
            fields.append(f'上下=-999.9')
        if record.tension_wire_up_down == -999.9:
            fields.append(f'引张=-999.9')
        if record.hydrostatic_leveling_settlement == -999.9:
            fields.append(f'水准=-999.9')
        if record.water_level_upstream == -999.9:
            fields.append(f'上游=-999.9')
        if record.water_level_downstream == -999.9:
            fields.append(f'下游=-999.9')
        print(f'{record.point.point_code} | {record.monitor_time.strftime("%Y-%m-%d")} | {", ".join(fields)}')
    
    # 执行删除
    deleted_count, _ = anomaly_records.delete()
    print(f'\n【删除完成】')
    print(f'已删除 {deleted_count} 条乱码数据')
    
    # 验证删除结果
    remaining = MonitorData.objects.filter(
        Q(inverted_plumb_left_right=-999.9) | Q(inverted_plumb_up_down=-999.9) |
        Q(tension_wire_up_down=-999.9) | Q(hydrostatic_leveling_settlement=-999.9) |
        Q(water_level_upstream=-999.9) | Q(water_level_downstream=-999.9)
    ).count()
    print(f'验证：剩余乱码数据 {remaining} 条')
else:
    print('没有乱码数据')
