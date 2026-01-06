from django.db import models
from water_structures.models import Point

class MonitorData(models.Model):
    """
    动态监测数据表（无核心修改，支撑单一大坝场景）
    """
    point = models.ForeignKey(
        Point, 
        on_delete=models.CASCADE, 
        related_name="monitor_records", 
        verbose_name="关联监测点"
    )
    monitor_time = models.DateTimeField(verbose_name="监测时间")

    # 4个指标的监测值（保留原有字段，无需修改）
    inverted_plumb_up_down = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="倒垂线-上下游位移值(mm)"
    )
    inverted_plumb_left_right = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="倒垂线-左右岸位移值(mm)"
    )
    tension_wire_up_down = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="引张线-上下游位移值(mm)"
    )
    hydrostatic_leveling_settlement = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="静力水准-沉降值(mm)"
    )
    water_level_upstream = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="上游水位值(m)"
    )
    water_level_downstream = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="下游水位值(m)"
    )

    # 预警状态（自动判断，无需手动填写）
    STATUS_CHOICES = [
        ("normal", "正常"),
        ("warning", "预警"),
        ("alarm", "告警"),
    ]
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default="normal", 
        verbose_name="预警状态"
    )
    monitor_person = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name="监测人员"
    )
    remark = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="备注说明"
    )
    create_time = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="系统录入时间"
    )

    class Meta:
        verbose_name = "动态监测数据"
        verbose_name_plural = verbose_name
        ordering = ["-monitor_time"]
        unique_together = ["point", "monitor_time"]

    def __str__(self):
        return f"{self.point.point_code}-{self.monitor_time.strftime('%Y-%m-%d %H:%M')}-{self.get_status_display()}"

    # 自动判断预警状态（保留原有逻辑，不受单一大坝影响）
    def save(self, *args, **kwargs):
        device_type = self.point.device.device_type
        point = self.point
        current_value = None
        upper_threshold = None
        lower_threshold = None

        # 按设备类型匹配指标值和阈值
        if device_type == "inverted_plumb_up_down":
            current_value = self.inverted_plumb_up_down
            upper_threshold = point.displacement_upper
            lower_threshold = point.displacement_lower
        elif device_type == "inverted_plumb_left_right":
            current_value = self.inverted_plumb_left_right
            upper_threshold = point.displacement_upper
            lower_threshold = point.displacement_lower
        elif device_type == "tension_wire_up_down":
            current_value = self.tension_wire_up_down
            upper_threshold = point.displacement_upper
            lower_threshold = point.displacement_lower
        elif device_type == "hydrostatic_leveling":
            current_value = self.hydrostatic_leveling_settlement
            upper_threshold = point.settlement_upper
            lower_threshold = point.settlement_lower
        elif device_type == "water_level_upstream":
            current_value = self.water_level_upstream
            upper_threshold = point.water_level_upper
            lower_threshold = point.water_level_lower
        elif device_type == "water_level_downstream":
            current_value = self.water_level_downstream
            upper_threshold = point.water_level_upper
            lower_threshold = point.water_level_lower

        # 判断状态
        if current_value is not None and upper_threshold is not None and lower_threshold is not None:
            if current_value > upper_threshold * 2 or current_value < lower_threshold * 2:
                self.status = "alarm"
            elif current_value > upper_threshold or current_value < lower_threshold:
                self.status = "warning"
            else:
                self.status = "normal"

        super().save(*args, **kwargs)