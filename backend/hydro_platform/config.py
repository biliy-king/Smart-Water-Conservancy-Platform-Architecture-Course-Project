# backend/hydro_platform/config.py
import os

class MonitoringConfig:
    """监测系统配置"""
    
    # 虚拟实时数据开关
    USE_ML_PREDICTION = os.getenv('USE_ML_PREDICTION', 'False').lower() == 'true'
    
    # 波动范围配置（按设备类型）
    FLUCTUATION_RANGES = {
        'water_level_upstream': 0.05,      # 水位 ±5%
        'water_level_downstream': 0.05,
        'inverted_plumb_left_right': 0.02, # 倒垂线 ±2%
        'inverted_plumb_up_down': 0.02,
        'tension_wire_up_down': 0.02,      # 引张线 ±2%
        'hydrostatic_leveling': 0.02,      # 静力水准 ±2%
    }
    
    # 物理边界配置
    PHYSICAL_BOUNDS = {
        'water_level_upstream': {'min': 0, 'max': 100},
        'water_level_downstream': {'min': 0, 'max': 100},
        'inverted_plumb_left_right': {'min': -50, 'max': 50},
        'inverted_plumb_up_down': {'min': -50, 'max': 50},
        'tension_wire_up_down': {'min': -30, 'max': 30},
        'hydrostatic_leveling': {'min': -20, 'max': 20},
    }
    
    # 最大日变化率（斜率限制）
    MAX_DAILY_CHANGE = {
        'water_level_upstream': 1.0,       # 水位最大1m/日
        'water_level_downstream': 1.0,
        'inverted_plumb_left_right': 2.0,  # 位移最大2mm/日
        'inverted_plumb_up_down': 2.0,
        'tension_wire_up_down': 2.0,
        'hydrostatic_leveling': 1.5,
    }