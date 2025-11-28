# ---------------------------
# 全局绘图上下文（语义分析核心变量）
# ---------------------------
# 坐标变换参数
Origin_x: float = 0.0  # 平移原点 X
Origin_y: float = 0.0  # 平移原点 Y
Rot_ang: float = 0.0   # 旋转角度（弧度）
Scale_x: float = 1.0   # X轴缩放因子
Scale_y: float = 1.0   # Y轴缩放因子

# 全局参数 T（循环变量）
Parameter_T: float = 0.0

# 绘图样式
StyleConfig = {
    "color": "#000000",    # 线条颜色（默认黑色）
    "opacity": 1.0,        # 透明度（0~1，默认不透明）
    "line_width": 1.0,     # 线条宽度（默认1.0）
}

# 坐标缓存列表（用于批量绘制）
CachedPoints = {
    "x": [],  # 缓存所有变换后的 X 坐标
    "y": []   # 缓存所有变换后的 Y 坐标
}

AxisRange = {
    "x_min": None,
    "x_max": None,
    "y_min": None,
    "y_max": None
}

# 重置全局参数
def reset_context() -> None:
    """重置全局绘图上下文（清空缓存、重置参数）"""
    global Origin_x, Origin_y, Rot_ang, Scale_x, Scale_y, Parameter_T, StyleConfig, AxisRange
    Origin_x = 0.0
    Origin_y = 0.0
    Rot_ang = 0.0
    Scale_x = 1.0
    Scale_y = 1.0
    Parameter_T = 0.0
    CachedPoints["x"].clear()
    CachedPoints["y"].clear()
    StyleConfig = {
        "color": "#000000",
        "opacity": 1.0,
        "line_width": 1.0
    }
    AxisRange = {
        "x_min": None,
        "x_max": None,
        "y_min": None,
        "y_max": None
    }