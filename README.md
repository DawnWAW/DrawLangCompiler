# DrawLangCompiler - 函数绘图语言编译器

## 概述
> 西电编译原理实验作业

这是一个基于 Python 实现的函数绘图语言编译器，能够解析特定的绘图语言源代码，并将其中定义的数学表达式可视化为二维图形。该编译器具备完整的编译器前端功能，包括词法分析、语法分析和语义分析三个阶段，最终通过 matplotlib 库渲染图形输出。

支持的语言特性包括：
- 基本数学运算（加减乘除、幂运算）
- 数学函数（sin, cos, tan, sqrt, exp, ln）
- 图形变换指令（原点平移、缩放、旋转）
- 循环绘图语句（FOR...DRAW）
- 样式设置（颜色、透明度、线宽）
- 多种注释方式（单行注释、多行注释）

## 环境配置
### 软件环境
- **操作系统**: Ubuntu Linux (推荐) 或其他 Linux 发行版
- **编程语言**: Python 3.8+
- **GUI框架**: Tkinter
- **绘图库**: Matplotlib (with Tkinter backend)

### 依赖库
```bash
pip install matplotlib tkinter
```


> 注意：由于使用了 Tkinter GUI 框架，该项目主要适用于 Linux 平台。Windows 或 macOS 上可能存在兼容性问题。

## 实现过程

本项目的实现分为以下几个主要阶段：

1. **词法分析器(scanner)**  
   将输入的源代码转换为 token 流。使用 DFA 自动机识别各种 token 类型，包括关键字、标识符、常量、运算符等。

2. **语法分析器(parser)**  
   使用递归下降解析法将 token 流转换为抽象语法树(AST)。支持运算符优先级和结合性处理。

3. **语义分析器(semantics)**  
   遍历语法树执行语义动作，包括表达式求值、坐标变换和图形绘制。

整体架构体现了经典编译器三阶段设计思想，同时结合图形绘制需求进行了针对性优化。

## 启动方式

### 运行程序
```bash
cd /path/to/CompilerExperiment
python src/main.py
```


### 使用说明
1. 程序启动后会显示图形界面窗口
2. 点击菜单栏 "文件(File)" -> "打开脚本(Open Script)"
3. 选择绘图语言脚本文件（通常为 .txt 格式）
4. 程序将自动解析并绘制图形

### 示例脚本
```txt
-- Arrow
scale is (1, 1);
style is (yellow, 0.5, 2);
origin is (450, 450);
rot is pi;
for t from 0 to 400 step 1 draw( t, t );


-- 心形曲线

origin is (200, 200);
rot is 3*pi/2;
style is (red, 0.7, 1);

-- 圆润型
scale is (50, 50);
for t from -pi to pi step pi/200 draw((2*cos(t) - cos(2*t)),  (2*sin(t)-sin(2*t))  );

-- 尖锐型
origin is (200+80, 200+80);
style is (blue, 0.9, 2);
scale is (8, 8);
rot is 0;
for t from 0 to 2*pi  step pi/200 draw(
            16*(sin(t)**3),
			13*cos(t) - 5*cos(2*t) - 2*cos(3*t)-cos(4*t)
	  );
```
![Heart](./doc/semantics/heart.png)


### 菜单功能
- **文件(File)**:
  - 打开脚本: 加载并执行绘图脚本
  - 退出: 关闭程序
- **编辑(Edit)**:
  - 清空画布: 清除当前绘制的所有图形

## 项目特点

1. **完整的编译器前端实现**：涵盖词法分析、语法分析和语义分析全过程
2. **良好的错误处理机制**：对词法错误、语法错误和语义错误都有适当处理
3. **丰富的图形控制指令**：支持多种图形变换和样式设置
4. **样式设置**: 支持颜色、透明度和线宽的设置
5. **灵活的注释支持**：支持多种注释格式(--, //, #, /* */)