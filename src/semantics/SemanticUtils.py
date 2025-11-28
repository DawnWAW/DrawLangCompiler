import math
import matplotlib.pyplot as plt
from src.parser.ExprNode import ExprNode
from src.scanner.TokenType import TokenType
from src.semantics import SemanticContext as sc


def get_expr_value(root: ExprNode) -> float:
    """
    深度优先后序遍历语法树，计算表达式值
    """
    if root is None:
        return 0.0

    op_code = root.op_code
    if op_code == TokenType.CONST_ID:
        # 常数节点：直接返回常数值
        return root.const_val
    elif op_code == TokenType.T:
        # 参数节点：返回全局变量T的值
        return Parameter_T
    elif op_code == TokenType.FUNC:
        # 函数节点：计算子表达式值后调用函数指针
        child_val = get_expr_value(root.child)
        return root.func_ptr(child_val) if root.func_ptr else 0.0
    elif op_code in (TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV, TokenType.POWER):
        # 二元运算节点：递归计算左右子树
        left_val = get_expr_value(root.left)
        right_val = get_expr_value(root.right)
        if op_code == TokenType.PLUS:
            return left_val + right_val
        elif op_code == TokenType.MINUS:
            return left_val - right_val
        elif op_code == TokenType.MUL:
            return left_val * right_val
        elif op_code == TokenType.DIV:
            if right_val == 0:
                # 除零错误
                raise ZeroDivisionError("Division by zero in expression")
            return left_val / right_val
        elif op_code == TokenType.POWER:
            return math.pow(left_val, right_val)
    else:
        return 0.0


def calc_coord(x_expr: ExprNode, y_expr: ExprNode) -> tuple[float, float]:
    """
    坐标变换：原始坐标 → 缩放 → 旋转 → 平移
    返回变换后的实际窗口坐标（x, y）
    """

    # 1. 计算原始坐标（基于T的表达式值）
    local_x = get_expr_value(x_expr)
    local_y = get_expr_value(y_expr)

    # 2. 缩放变换
    local_x *= sc.Scale_x
    local_y *= sc.Scale_y

    # 3. 旋转变换（弧度制，逆时针为正）
    cos_ang = math.cos(sc.Rot_ang)
    sin_ang = math.sin(sc.Rot_ang)
    temp_x = local_x * cos_ang + local_y * sin_ang
    temp_y = local_y * cos_ang - local_x * sin_ang
    local_x, local_y = temp_x, temp_y

    # 4. 平移变换（窗口坐标系：Y轴向下，需翻转Y值以符合数学习惯）
    actual_x = sc.Origin_x + local_x
    actual_y = sc.Origin_y + local_y

    return actual_x, actual_y

def cache_points(start_expr: ExprNode, end_expr: ExprNode, step_expr: ExprNode, x_expr: ExprNode, y_expr: ExprNode) -> None:
    """
    新增：缓存所有坐标点（替换原 draw_loop 的逐点绘制）
    遍历 T 值，计算坐标并存入 CachedPoints
    """
    global Parameter_T

    # 计算循环参数（起始值、结束值、步长）
    start_val = get_expr_value(start_expr)
    end_val = get_expr_value(end_expr)
    step_val = get_expr_value(step_expr)

    # 校验步长合法性
    if step_val <= 0:
        raise SyntaxError("Step value must be positive")
    if (start_val > end_val and step_val > 0) or (start_val < end_val and step_val < 0):
        raise SyntaxError("Start/End/Step mismatch (loop will not execute)")

    # 清空当前缓存（避免多轮绘制叠加）
    sc.CachedPoints["x"].clear()
    sc.CachedPoints["y"].clear()

    # 遍历 T 值，缓存坐标
    Parameter_T = start_val
    while (step_val > 0 and Parameter_T <= end_val) or (step_val < 0 and Parameter_T >= end_val):
        x, y = calc_coord(x_expr, y_expr)
        sc.CachedPoints["x"].append(x)
        sc.CachedPoints["y"].append(y)
        Parameter_T += step_val

    print(f"缓存坐标点数量：{len(sc.CachedPoints['x'])}")


def batch_draw(ax: plt.Axes) -> None:
    """
    新增：批量绘制缓存的坐标点（Matplotlib 核心绘图函数）
    ax：Matplotlib 的坐标轴对象（用于绘图）
    """

    # 获取样式配置
    color = sc.StyleConfig["color"]
    line_width = sc.StyleConfig["line_width"]
    alpha = sc.StyleConfig.get("opacity", 1.0)  # 获取透明度值，默认不透明

    # 批量绘制曲线（Matplotlib plot 自动连接点为线）
    ax.plot(
        sc.CachedPoints["x"], sc.CachedPoints["y"],
        color=color,
        linewidth=line_width,
        alpha=alpha
    )

    # 如果有坐标点，计算并返回范围用于后续设置坐标轴
    if len(sc.CachedPoints["x"]) > 0 and len(sc.CachedPoints["y"]) > 0:
        x_min = min(sc.CachedPoints["x"])
        x_max = max(sc.CachedPoints["x"])
        y_min = min(sc.CachedPoints["y"])
        y_max = max(sc.CachedPoints["y"])

        # 存储范围信息供外部使用
        sc.AxisRange = {
            "x_min": x_min if sc.AxisRange["x_min"] is None or x_min < sc.AxisRange["x_min"] else sc.AxisRange["x_min"],
            "x_max": x_max if sc.AxisRange["x_max"] is None or x_max > sc.AxisRange["x_max"] else sc.AxisRange["x_max"],
            "y_min": y_min if sc.AxisRange["y_min"] is None or y_min < sc.AxisRange["y_min"] else sc.AxisRange["y_min"],
            "y_max": y_max if sc.AxisRange["y_max"] is None or y_max > sc.AxisRange["y_max"] else sc.AxisRange["y_max"]
        }

    # 刷新画布（立即显示绘制结果）
    ax.figure.canvas.draw()
