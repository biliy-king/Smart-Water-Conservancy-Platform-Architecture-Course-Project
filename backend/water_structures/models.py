from django.db import models

class Structure(models.Model):
    """
    大坝基础信息表（静态）
    调整点：1. 新增Cesium全局三维配置字段；2. 适配单一大坝，字段保留扩展性
    说明：仅需录入1条数据（你的唯一大坝），后续所有设备/测点都关联这条数据
    """
    name = models.CharField(
        max_length=100, 
        verbose_name="大坝名称"  # 如“芹山水电站大坝”
    )
    # Cesium全局三维配置（加载大坝3D模型必需，支撑前端Cesium布置）
    cesium_center_x = models.FloatField(
        verbose_name="Cesium大坝中心点X（世界坐标）"  # 如118.xxx（经度转换后的笛卡尔坐标，或直接填虚拟值如1000.0）
    )
    cesium_center_y = models.FloatField(
        verbose_name="Cesium大坝中心点Y（世界坐标）"  # 如26.xxx（纬度转换后的笛卡尔坐标，或直接填虚拟值如500.0）
    )
    cesium_center_z = models.FloatField(
        verbose_name="Cesium大坝中心点Z（世界坐标/高程）"  # 如100.0（大坝基座高程）
    )
    cesium_heading = models.FloatField(
        default=0.0, 
        verbose_name="Cesium大坝模型航向角"  # 绕Z轴旋转，0=正北，Cesium默认值即可
    )
    cesium_pitch = models.FloatField(
        default=0.0, 
        verbose_name="Cesium大坝模型俯仰角"  # 绕X轴旋转，0=水平，Cesium默认值即可
    )
    cesium_roll = models.FloatField(
        default=0.0, 
        verbose_name="Cesium大坝模型翻滚角"  # 绕Y轴旋转，0=水平，Cesium默认值即可
    )
    cesium_scale = models.FloatField(
        default=1.0, 
        verbose_name="Cesium大坝模型缩放比例"  # 1=原始大小，可根据场景调整
    )
    cesium_model_url = models.CharField(
        max_length=500, 
        null=True, 
        blank=True, 
        verbose_name="Cesium大坝3D模型文件路径"  # 如"/static/models/dam.glb"，前端加载模型用
    )
    # 原有基础字段（保留，无需删除，适配单一大坝）
    level = models.CharField(
        max_length=20, 
        choices=[("1级", "1级大坝"), ("2级", "2级大坝"), ("3级", "3级大坝")], 
        default="2级", 
        verbose_name="大坝等级"
    )
    completion_time = models.DateField(
        null=True, 
        blank=True,  # 单一大坝，不清楚建成时间可留空
        verbose_name="大坝建成时间"
    )
    create_time = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="系统录入时间"
    )

    class Meta:
        verbose_name = "大坝信息"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __str__(self):
        return self.name  # 单一大坝，直接显示名称即可

    @property
    def is_default_dam(self):
        """
        【辅助属性】标记为默认大坝（单一大坝场景下，第一条数据即为默认）
        用途：前端Cesium默认加载该大坝，后端自动关联设备/测点
        """
        return self.id == 1  # 假设第一条录入的大坝数据（id=1）为默认大坝


class MonitoringDevice(models.Model):
    """
    监测设备表（静态）
    调整点：无大幅修改，仅关联单一大坝（录入时选择唯一的大坝数据即可）
    """
    # 关联大坝：仍保留外键（兼容后续扩展多大坝），仅需录入1条大坝数据，后续设备都关联它
    structure = models.ForeignKey(
        Structure, 
        on_delete=models.CASCADE, 
        related_name="monitoring_devices", 
        verbose_name="所属大坝"
    )
    device_name = models.CharField(
        max_length=100, 
        verbose_name="设备名称"  # 如“倒垂线传感器-坝顶1#”
    )
    # 设备类型：仍保留明确的“仪器+监测指标”，避免同指标不同仪器混淆
    DEVICE_TYPE_CHOICES = [
        ("inverted_plumb_up_down", "倒垂线-上下游位移监测"),
        ("inverted_plumb_left_right", "倒垂线-左右岸位移监测"),
        ("tension_wire_up_down", "引张线-上下游位移监测"),
        ("hydrostatic_leveling", "静力水准-沉降监测"),
        ("water_level_upstream", "水位传感器-上游水位监测"),
        ("water_level_downstream", "水位传感器-下游水位监测"),
    ]
    device_type = models.CharField(
        max_length=50, 
        choices=DEVICE_TYPE_CHOICES, 
        verbose_name="设备类型（仪器+监测指标）"
    )
    install_position = models.CharField(
        max_length=200, 
        verbose_name="设备安装位置（相对大坝）"  # 坝段
    )
    install_time = models.DateField(
        null=True, 
        blank=True,  # 不清楚安装时间可留空
        verbose_name="设备安装时间"
    )
    DEVICE_STATUS_CHOICES = [
        ("running", "正常运行"),
        ("stopped", "停用"),
        ("faulty", "设备故障"),
    ]
    device_status = models.CharField(
        max_length=20, 
        choices=DEVICE_STATUS_CHOICES, 
        default="running", 
        verbose_name="设备运行状态"
    )
    create_time = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="系统录入时间"
    )

    class Meta:
        verbose_name = "监测设备"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]
        # 唯一约束：单一大坝下，同一位置不重复安装同类型设备
        unique_together = ["structure", "install_position", "device_type"]

    def __str__(self):
        return f"{self.device_name}（{self.get_device_type_display()}）"


class Point(models.Model):
    """
    测点表（静态）
    调整点：1. 坐标字段明确为「相对大坝的局部坐标」；2. 注释优化，支撑Cesium坐标转换
    说明：以大坝Cesium模型的中心点为原点(0,0,0)，填写仪器相对大坝的位置
    """
    # 关联监测设备：1台设备对应1个测点
    device = models.OneToOneField(
        MonitoringDevice, 
        on_delete=models.CASCADE, 
        related_name="bind_point", 
        verbose_name="绑定监测设备"
    )
    point_code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="测点编号"  # 如“DQ-BD-001”（DQ=大坝，BD=倒垂线）
    )
    # 【关键调整】从“大地坐标”改为“相对大坝的局部三维坐标”（支撑Cesium布置）
    # 说明：大坝中心点为(0,0,0)，例如：
    # - 大坝右侧10米、前方5米、高程20米 → (10.0, 5.0, 20.0)
    # - 大坝左侧5米、后方2米、高程15米 → (-5.0, -2.0, 15.0)
    relative_x = models.FloatField(verbose_name="相对大坝X坐标（局部）")
    relative_y = models.FloatField(verbose_name="相对大坝Y坐标（局部）")
    relative_z = models.FloatField(verbose_name="相对大坝Z坐标（局部/高程）")

    # 预警阈值：保持原有逻辑，按设备类型独立设置
    displacement_upper = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="位移预警上限(mm)"
    )
    displacement_lower = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="位移预警下限(mm)"
    )
    settlement_upper = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="沉降预警上限(mm)"
    )
    settlement_lower = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="沉降预警下限(mm)"
    )
    water_level_upper = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="水位预警上限(m)"
    )
    water_level_lower = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="水位预警下限(m)"
    )

    create_time = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="系统录入时间"
    )

    class Meta:
        verbose_name = "监测点"
        verbose_name_plural = verbose_name
        ordering = ["point_code"]

    def __str__(self):
        return f"{self.point_code}（绑定设备：{self.device.device_name}）"

    @property
    def cesium_world_coords(self):
        """
        【辅助属性】计算测点在Cesium中的全局世界坐标
        逻辑：大坝全局坐标 + 测点相对坐标 → 直接给前端Cesium使用，无需前端额外计算
        返回：字典格式（x,y,z）
        """
        dam = self.device.structure
        return {
            "x": dam.cesium_center_x + self.relative_x,
            "y": dam.cesium_center_y + self.relative_y,
            "z": dam.cesium_center_z + self.relative_z
        }