import tkinter as tk
from tkinter import filedialog, Menu
from src.parser.Parser import parse
import src.semantics.SemanticContext as sc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 配置 Matplotlib 支持中文（可选）
# mpl.rcParams['font.sans-serif'] = ['SimHei']  # Windows 中文支持
# mpl.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class FuncPlotInterpreter:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Function Plotting Language Interpreter")
        self.root.geometry("800x600")

        # ---------------------------
        # 初始化 Matplotlib 绘图环境
        # ---------------------------
        # 1. 创建 Figure（绘图容器）
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        # 2. 配置坐标轴（可选：设置画布范围与窗口大小一致）
        self.ax.set_xlim(-400, 400)
        self.ax.set_ylim(-300, 300)
        self.ax.set_aspect("equal")  # 等比例缩放（避免图形拉伸）
        self.ax.grid(True, alpha=0.3)  # 显示网格（可选，便于观察）

        # 3. 将 Matplotlib Figure 嵌入 Tkinter 窗口
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()  # 初始化绘制
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 创建菜单（保持原有交互逻辑）
        self.create_menu()

    def create_menu(self) -> None:
        """保持原有菜单逻辑，仅修改绘图调用对象"""
        menu_bar = Menu(self.root)

        # 文件菜单
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="打开脚本", command=self.load_script)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)

        # 编辑菜单
        edit_menu = Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="清空画布", command=self.clear_canvas)
        menu_bar.add_cascade(label="编辑", menu=edit_menu)

        self.root.config(menu=menu_bar)

    def load_script(self) -> None:
        """加载脚本：调用 parse 时传递 Matplotlib Axes 对象（self.ax）"""
        file_path = filedialog.askopenfilename(
            title="选择绘图脚本",
            filetypes=[("Plot Script", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            print(f"\n加载脚本：{file_path}")
            self.clear_canvas()  # 清空画布
            parse(file_path, self.ax)  # 传递 Axes 对象给 Parser

            # 更新坐标轴范围
            self.set_axes_range(sc.AxisRange["x_min"], sc.AxisRange["x_max"], sc.AxisRange["y_min"], sc.AxisRange["y_max"])

    def clear_canvas(self) -> None:
        """Matplotlib 清空画布：清除所有绘制元素"""
        self.ax.clear()  # 清除坐标轴上的曲线/点
        self.ax.set_xlim(-400, 400)
        self.ax.set_ylim(-300, 300)
        self.ax.set_aspect("equal")
        self.ax.grid(True, alpha=0.3)  # 重新显示网格
        self.canvas.draw()  # 刷新画布
        sc.reset_context()
        print("画布已清空")

    def set_axes_range(self, x_min: float, x_max: float, y_min: float, y_max: float) -> None:
        """
        根据给定的坐标范围设置坐标轴，并添加边距

        Args:
            x_min: x轴最小值
            x_max: x轴最大值
            y_min: y轴最小值
            y_max: y轴最大值
        """

        self.ax.set_xlim(x_min - 50, x_max + 50)
        self.ax.set_ylim(y_min - 50, y_max + 50)

        # 重新绘制画布
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = FuncPlotInterpreter(root)
    root.mainloop()