import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydro_platform.settings')
django.setup()

from monitoring.models import MonitorData
from django.db.models import Q

total = MonitorData.objects.count()
print(f'【监测数据总数】: {total}')

# 统计各字段的数据量
print(f'\n【各类型数据量】')
plumb_lr = MonitorData.objects.filter(inverted_plumb_left_right__isnull=False).count()
plumb_ud = MonitorData.objects.filter(inverted_plumb_up_down__isnull=False).count()
tension = MonitorData.objects.filter(tension_wire_up_down__isnull=False).count()
leveling = MonitorData.objects.filter(hydrostatic_leveling_settlement__isnull=False).count()
water_up = MonitorData.objects.filter(water_level_upstream__isnull=False).count()
water_down = MonitorData.objects.filter(water_level_downstream__isnull=False).count()

print(f'倒垂线左右岸: {plumb_lr}')
print(f'倒垂线上下游: {plumb_ud}')
print(f'引张线: {tension}')
print(f'静力水准: {leveling}')
print(f'上游水位: {water_up}')
print(f'下游水位: {water_down}')

# 统计异常值
print(f'\n【异常值统计】')
anomaly_999_1 = MonitorData.objects.filter(
    Q(inverted_plumb_left_right=-999.1) | Q(inverted_plumb_up_down=-999.1) |
    Q(tension_wire_up_down=-999.1) | Q(hydrostatic_leveling_settlement=-999.1) |
    Q(water_level_upstream=-999.1) | Q(water_level_downstream=-999.1)
).count()

anomaly_999_2 = MonitorData.objects.filter(
    Q(inverted_plumb_left_right=-999.2) | Q(inverted_plumb_up_down=-999.2) |
    Q(tension_wire_up_down=-999.2) | Q(hydrostatic_leveling_settlement=-999.2) |
    Q(water_level_upstream=-999.2) | Q(water_level_downstream=-999.2)
).count()

anomaly_999_9 = MonitorData.objects.filter(
    Q(inverted_plumb_left_right=-999.9) | Q(inverted_plumb_up_down=-999.9) |
    Q(tension_wire_up_down=-999.9) | Q(hydrostatic_leveling_settlement=-999.9) |
    Q(water_level_upstream=-999.9) | Q(water_level_downstream=-999.9)
).count()

print(f'-999.1 (低于标尺水位): {anomaly_999_1}')
print(f'-999.2 (被遮挡无法观测): {anomaly_999_2}')
print(f'-999.9 (乱码数据): {anomaly_999_9}')

total_anomaly = anomaly_999_1 + anomaly_999_2 + anomaly_999_9
print(f'异常值总计: {total_anomaly}')

# 统计NULL值
print(f'\n【NULL/空值统计】')
null_count = MonitorData.objects.filter(
    inverted_plumb_left_right__isnull=True,
    inverted_plumb_up_down__isnull=True,
    tension_wire_up_down__isnull=True,
    hydrostatic_leveling_settlement__isnull=True,
    water_level_upstream__isnull=True,
    water_level_downstream__isnull=True
).count()
print(f'全为空的记录: {null_count}')

if total_anomaly > 0:
    print(f'\n【异常数据样例】')
    anomalies = MonitorData.objects.filter(
        Q(inverted_plumb_left_right__lt=-999) | Q(inverted_plumb_up_down__lt=-999) |
        Q(tension_wire_up_down__lt=-999) | Q(hydrostatic_leveling_settlement__lt=-999) |
        Q(water_level_upstream__lt=-999) | Q(water_level_downstream__lt=-999)
    )[:5]
    for data in anomalies:
        fields = []
        if data.inverted_plumb_left_right is not None and data.inverted_plumb_left_right < -999:
            fields.append(f'左右={data.inverted_plumb_left_right}')
        if data.inverted_plumb_up_down is not None and data.inverted_plumb_up_down < -999:
            fields.append(f'上下={data.inverted_plumb_up_down}')
        if data.tension_wire_up_down is not None and data.tension_wire_up_down < -999:
            fields.append(f'引张={data.tension_wire_up_down}')
        if data.hydrostatic_leveling_settlement is not None and data.hydrostatic_leveling_settlement < -999:
            fields.append(f'水准={data.hydrostatic_leveling_settlement}')
        if data.water_level_upstream is not None and data.water_level_upstream < -999:
            fields.append(f'上游={data.water_level_upstream}')
        if data.water_level_downstream is not None and data.water_level_downstream < -999:
            fields.append(f'下游={data.water_level_downstream}')
        print(f'{data.point.point_code} | {data.monitor_time.strftime("%Y-%m-%d")} | {", ".join(fields)}')
