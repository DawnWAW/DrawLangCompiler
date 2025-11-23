import matplotlib
# 在Linux系统中明确设置GUI后端以确保图形窗口可以正常显示
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

# 创建图形和轴
fig, ax = plt.subplots(figsize=(8, 6))

# 绘制一个简单的圆形
circle = plt.Circle((0.5, 0.5), 0.3, color='blue', alpha=0.5)
ax.add_patch(circle)

# 绘制一些基本图形
# 1. 绘制一条线
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)
ax.plot(x, y, label='sin(x)', color='red')

# 2. 绘制散点图
x_points = np.random.rand(20)
y_points = np.random.rand(20)
ax.scatter(x_points, y_points, c='green', marker='o', label='random')

# 设置坐标轴范围和标签
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1.5, 1.5)
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_title('sample')
ax.legend()

# 显示网格
ax.grid(True, alpha=0.3)

# 显示图形
plt.show()