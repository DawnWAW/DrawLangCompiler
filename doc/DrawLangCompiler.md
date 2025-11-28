# 函数绘图编译器实验报告

## 摘要

本实验报告主要描述了该编译器的设计和实现，包括词法分析、语法分析和语义分析三个主要阶段。该编译器能够解析绘图语言源代码，并利用matplotlib库将数学表达式可视化为二维图形。

## 1. 实验环境

### 运行环境依赖

- **操作系统**: Linux Ubuntu
- **GUI框架**: Tkinter (Linux版本)
- **绘图库**: Matplotlib with Tkinter backend

### 环境限制说明

由于本项目使用的是Linux平台下的`tkinter`作为GUI界面依赖，因此：

1. **平台兼容性**:
   - 项目只能在Linux环境下正常运行
   - Windows或macOS环境下可能会出现界面显示异常或依赖缺失问题

2. **依赖配置**:
   - 需要确保Linux系统已安装Python Tkinter支持
   - Matplotlib需配置为使用Tkinter后端(`FigureCanvasTkAgg`)

3. **运行要求**:
   ```python
   # main.py中的关键依赖导入
   import tkinter as tk
   from tkinter import filedialog, Menu
   from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
   ```

这种环境依赖设计确保了在Ubuntu系统上能够获得最佳的图形界面体验和稳定的绘图功能支持。

## 2. 实验内容

### 2.1 语言定义

#### 2.1.1 基本设计

##### 核心语法要素

| 要素类型  | 具体内容                                                     |
| --------- | ------------------------------------------------------------ |
| 保留字    | ORIGIN、SCALE、ROT、IS、FOR、FROM、TO、STEP、DRAW、STYLE     |
| 运算符    | +（加）、-（减）、*（乘）、/（除）、**（幂运算）             |
| 常量/参数 | 数值常量（如3.14、5）、符号常量（PI=3.14159、E=2.71828）、参数T |
| 函数      | sin、cos、tan、sqrt、exp、ln（基础数学函数）                 |
| 分隔符    | ;（语句结束）、( )（括号）、,（坐标分隔）                    |
| 注释      | //、--、# 单行注释，/* */ 多行注释                           |
| 颜色      | RED、BLUE、GREEN、YELLOW、BLACK、WHITE                       |

##### 核心语句格式

1. **原点语句**：`ORIGIN IS (表达式, 表达式);`
2. **缩放语句**：`SCALE IS (表达式, 表达式);`
3. **旋转语句**：`ROT IS 表达式;`
4. **样式语句**：`STYLE IS STYLEVALUE;`
5. **绘图语句**：`FOR T FROM 表达式 TO 表达式 STEP 表达式 DRAW (表达式, 表达式);`
6. **注释语句**: `--`、`//`、`#`或`/* */`

##### 语义规则

- 坐标体系：笛卡尔坐标系，x向右增，y向上增（数学常规坐标系）
- 图形变换顺序：**比例变换 → 旋转变换 → 平移变换**
- 默认值：原点(0,0)、缩放(1,1)、旋转0（不旋转）、样式(黑色, 不透明, 线宽1.0)
- 替换规则: `ORIGIN`、`ROT`、`SCALE` 和 `STYLE` 语句只影响其后的绘图语句，且遵循最后出现的语句有效的原则。
- 大小写不敏感: 语言对大小写不敏感
- 双精度表达式: 语句中表达式的值均为双精度类型
- 旋转角度: 弧度单位, 逆时针旋转
- 平移单位: 像素点单位

#### 2.1.2 语句定义

##### 循环绘图(FOR-DRAW)语句

`FOR T FROM 起点表达式 TO 终点表达式 STEP 步长表达式 DRAW (横坐标, 纵坐标);`

-   语义: 令T从起点到终点、每次改变一个步长，绘制出由(横坐标，纵坐标)所规定的点的轨迹。
-   例子: 如`FOR T FROM 0 TO 2*PI STEP PI/50 DRAW (cos(T), sin(T));`
-   说明: 该语句的作用是令T从0到2*PI、步长 PI/50，绘制出各个点的坐标(cos(T)，sin(T))，即一个单位圆。

##### 比例设置(SCALE)语句

`SCALE IS (横坐标比例因子, 纵坐标比例因子);`

-   语义: 设置横坐标和纵坐标的比例，并分别按照比例因子进行缩放
-   举例: 如`SCALE IS (50, 50);`
-   说明: 将横坐标和纵坐标的比例设置为1:1，且放大50倍。

##### 坐标平移(ORIGIN)语句

`ORIGIN IS (表达式, 表达式);`

-   语义: 将坐标系的原点平移到横坐标和纵坐标规定的点处。
-   举例: 如`ORIGIN IS (300, 200);`
-   说明: 将原点从(0, 0)平移到(300, 200) 处。

##### 角度旋转(ROT)语句

`ROT IS 表达式;`

-   语义: 绕原点逆时针旋转弧度值所规定的角度
    -   计算公式：
    -   $旋转后X = 旋转前X \times \cos(弧度)+旋转前Y \times \sin(弧度)$
    -   $旋转后Y = 旋转前Y \times \cos(弧度)-旋转前X \times \sin(弧度)$
-   举例: 如`ROT IS PI/2;`

##### 样式设置(STYLE)语句

`STYLE IS STYLEVALUE;`

-   语义: 设置绘图的颜色、透明度和线条宽度
-   STYLEVALUE的格式：
    1. `COLOR`：仅设置颜色，如 `STYLE IS RED;`
    2. `CONST_ID`：仅设置线条宽度，如 `STYLE IS 2.0;`
    3. `(COLOR[, OPACITY[, LINE_WIDTH]])`：设置颜色、透明度和线条宽度，如 `STYLE IS (RED, 0.5, 2.0);`
-   默认值：颜色为黑色，透明度为1.0（不透明），线条宽度为1.0

##### 注释语句

支持四种注释方式：

1. `//`：单行注释（忽略到行尾）
2. `--`：单行注释（忽略到行尾）
3. `#`：单行注释（忽略到行尾）
4. `/* */`：多行注释（可跨越多行）

-   语义: 屏蔽掉注释性的语句

### 2.2 词法分析器实现

#### 2.2.1 概述

词法分析器负责将输入的源代码转换为token流。它从输入文件中读取字符，将它们分组为有意义的token，并将这些token传递给解析器。

#### 2.2.2 主要组件

##### Lexer 类

Lexer类是扫描器实现的核心。它处理文件读取、字符处理和token生成。

###### 关键方法：

- `__init__(self, file_path: str)`：使用文件路径初始化词法分析器，以UTF-8编码和错误处理方式打开文件。
- `get_char(self) -> str`：从文件中读取下一个字符并将其转换为大写以进行大小写不敏感处理。
- `back_char(self) -> None`：将文件指针向后移动一个字符（换行符除外）。
- `pre_process(self) -> str`：跳过空白字符并返回第一个非空白字符。
- `get_token(self) -> Token | None`：使用TokenDFA识别并返回下一个token的核心方法。
- `close(self) -> None`：关闭输入文件。

##### TokenDFA

扫描器使用TokenDFA进行token识别。

###### 字符类型：

0. 字母（包括下划线）
1. 数字
2. 句点 (.)
3. 星号 (*)
4. 斜杠 (/)
5. 连字符 (-)
6. 加号 (+)
7. 分号 (;)
8. 左括号 (()
9. 右括号 ())
10. 逗号 (,)
11. 其他字符
12. 井号(#)

###### 状态：

- 状态 0：初始状态
- 状态 1：标识符 (ID)
- 状态 2：整数常量 (CONST_ID)
- 状态 3：小数常量 (CONST_ID)
- 状态 4：乘法运算符 (MUL)
- 状态 5：幂运算符 (**)
- 状态 6：除法运算符 (DIV)
- 状态 7：减法运算符 (MINUS)
- 状态 8：加法运算符 (PLUS)
- 状态 9：注释 (COMMENT)
- 状态 10：分号 (SEMICO)
- 状态 11：左括号 (L_BRACKET)
- 状态 12：右括号 (R_BRACKET)
- 状态 13：逗号 (COMMA)
- 状态 14：多行注释开始

##### Token 和 TokenType

token由Token类表示，包括：
- type：来自TokenType枚举的token类型
- lexeme：源代码中的原始字符串
- value：常量的数值
- func_ptr：数学函数的函数指针

TokenType枚举定义了所有可能的token类型，包括保留字、运算符、分隔符和特殊token。

#### 2.2.3 token识别过程

get_token方法中的token识别过程包含三个主要步骤：

##### 预处理

跳过所有空白字符并返回第一个非空白字符。

##### TokenDFA 状态转换

从初始状态 (0) 开始，使用TRANSITION_TABLE根据字符类型在状态间移动。继续读取字符直到无法继续转换，然后回退一个字符。转换图如下:

![DFA_Transition_Diagram](./DrawLangCompiler.assets/TokenDFA_State_Transition_Diagram.png)

##### 后处理

根据最终状态，使用FINAL_STATE_TABLE确定token类型。需要特殊处理的情况包括：
- ID：在符号表中查找以区分保留字和标识符
- 常量：将字符串转换为数值
- 注释：跳至行尾并继续扫描

#### 2.2.4 符号表

符号表包含预定义的标识符：
- 数学常量 (PI, E)
- 参数 (T)
- 数学函数 (SIN, COS, TAN, SQRT, EXP, LN)
- 保留字 (ORIGIN, SCALE, ROT, IS, FOR, FROM, TO, STEP, DRAW)
- 颜色保留字 (BLACK, WHITE, RED, GREEN, BLUE, YELLOW)

lookup_symbol函数用于区分用户定义的标识符和预定义的标识符。

#### 2.2.5 错误处理

扫描器处理各种错误情况：
- 无效字符：无法启动任何有效token的字符
- 无效编码：由于 `errors="ignore"` 参数，非UTF-8字符被忽略
- 格式错误的数字：无法转换为浮点数的数字

发生错误时，返回 ERRTOKEN，允许解析器适当地处理错误。

#### 2.2.6 特殊功能

##### 大小写不敏感

所有输入都被转换为大写进行处理，使语言大小写不敏感。

##### 注释支持

支持四种类型的注释：
- 以 // 开头的行注释
- 以 -- 开头的行注释
- 以 # 开头的行注释
- 以`/*` `*/`开头结尾的多行注释

这四种都在token化过程中被识别和跳过。

##### 多字符运算符

扫描器正确识别多字符运算符如 **（幂运算）并将其与单字符运算符区分开来。

### 2.3 语法分析器实现

#### 2.3.1 概述

语法分析器负责将词法分析器产生的Token流转换为抽象语法树(AST)。它使用递归下降解析方法，根据预定义的语法规则对Token流进行分析，并构建表达式的语法树结构。

#### 2.3.2 主要组件

##### Parser 类

Parser模块主要由递归下降解析函数组成，每个语法规则对应一个函数。

###### 关键方法：

- `parse(file_path: str)`：解析器入口函数，初始化词法分析器并启动语法分析
- `program(lexer: Lexer)`：处理程序主体，解析语句序列
- `statement(lexer: Lexer)`：处理各种语句类型
- `expression(lexer: Lexer)`：处理表达式（加法、减法运算）
- `term(lexer: Lexer)`：处理项（乘法、除法运算）
- `factor(lexer: Lexer)`：处理因子（一元运算）
- `component(lexer: Lexer)`：处理组件（幂运算）
- `atom(lexer: Lexer)`：处理原子（常量、变量、函数调用、括号表达式）

##### ExprNode 类

ExprNode类表示语法树节点，用于构建表达式的树形结构。

###### 节点属性：

- `op_code`：节点类型（如PLUS、MINUS、CONST_ID等）
- `left`：左子节点（二元运算用）
- `right`：右子节点（二元运算用）
- `child`：子节点（函数调用/一元运算用）
- `const_val`：常数值（CONST_ID用）
- `param_ptr`：参数指针（T用，绑定全局参数T）
- `func_ptr`：函数指针（FUNC用）

#### 2.3.3 语法规则实现

##### EBNF 文法

语法分析器基于以下EBNF文法实现：

```
Program         → { Statement SEMICO }
Statement       → OriginStatement | ScaleStatement | RotStatement | ForStatement | StyleStatement
OriginStatement → ORIGIN IS L_BRACKET Expression COMMA Expression R_BRACKET
ScaleStatement  → SCALE IS L_BRACKET Expression COMMA Expression R_BRACKET
RotStatement    → ROT IS Expression
StyleStatement  → STYLE IS STYLEVALUE
STYLEVALUE      → COLOR | CONST_ID | ( COLOR [, CONST_ID [, CONST_ID] ] )
Expression      → Term { (PLUS | MINUS) Term }
Term            → Factor { (MUL | DIV) Factor }
Factor          → (PLUS | MINUS) Factor | Component
Component       → Atom [ POWER Component ]
Atom            → CONST_ID | T | FUNC L_BRACKET Expression R_BRACKET | L_BRACKET Expression R_BRACKET
```

![EBNF文法图](./DrawLangCompiler.assets/EBNF_Grammar.png)

##### 运算符优先级和结合性

语法分析器正确处理了各种运算符的优先级和结合性：

1. 括号 `()` - 最高优先级
2. 幂运算 `**` - 右结合
3. 一元运算 `+` `-` - 右结合
4. 乘除运算 `*` `/` - 左结合
5. 加减运算 `+` `-` - 左结合

#### 2.3.4 递归下降解析实现

##### 入口流程

解析过程从parse接口开始：

1. `parse`函数初始化Lexer并调用`program`
2. `program`通过`fetch_token`获取第一个记号，然后进入语句循环

##### 语句级处理流程

`program`循环中，每次迭代执行：

1. 调用`statement`处理单条语句
2. 通过`match_token(TokenType.SEMICO, lexer)`匹配语句结束分号

`statement`根据当前记号类型分发到具体语句处理函数：

- `ORIGIN` → `origin_statement`
- `SCALE` → `scale_statement`
- `ROT` → `rot_statement`
- `FOR` → `for_statement`
- `STYLE` → `style_statement`

##### 表达式解析流程

在各语句处理函数中，当需要解析表达式时，调用链如下：

1. `expression` - 处理加法/减法运算
2. `term` - 处理乘法/除法运算
3. `factor` - 处理一元运算
4. `component` - 处理幂运算
5. `atom` - 处理原子表达式

#### 2.3.5 错误处理

##### 语法错误

语法分析器在遇到不符合语法规则的Token序列时会抛出语法错误。

##### 问题案例及解决方案

###### 问题：处理幂运算和自增自减符号时的优先级错误

在处理 `origin is (2**-2, 0);` 这样的表达式时，可能会出现以下错误：

```txt
origin is (2**-2, 0);           // 应该是 2**(-2)=0.25
Syntax parsing failed: Syntax Error：Not a valid atom: '-'
```

在Python中, `2**-2`的结果是0.25, 因此我们的编译器也应该先允许`-2`进行完一个`0-2`的factor一元减运算, 再作为指数参与`2**(-2)`幂运算。

###### 原因分析

![PPT展示的EBNF语法图](./DrawLangCompiler.assets/PPT_EBNF_Grammar.png)

问题出在component的推导文法中。在PPT给出的EBNF文法中，当处理幂运算时，会形成以下的推导:

`Component -> Atom POWER Component -> Atom POWER Component -> Atom POWER Atom [POWER Component]`

也就是说如果出现幂运算, 只允许`CONST_ID`作为指数, 这里的`CONST_ID`只能是1,2,3这种自然数, 如果遇到了-1这种负数, 获取到的token是`-`而不是`CONST_ID`,因此会出现上面的报错

###### 解决方案

修改component函数，将幂运算右侧的解析从component改为factor，允许先进行一元+/-的计算：

```python
def component(lexer: Lexer) -> ExprNode:
    """Component → Atom [ POWER Component ]（右结合）"""
    left_node = atom(lexer)
    global current_token
    while current_token.type == TokenType.POWER:
        op_token = current_token
        match_token(TokenType.POWER, lexer)
        # **右边如果是factor, 允许先进行一元+/-的计算
        right_node = factor(lexer)
        left_node = make_expr_node(op_token.type, left_node, right_node)
    return left_node
```

这样修改后，表达式 `2**-2` 能够被正确解析为 `2**(-2)`，从而解决了该语法错误问题。

#### 2.3.6 样式语句解析

样式语句（StyleStatement）支持设置绘图的颜色、透明度和线条粗细：
STYLE语句方式有三种文法推导：
- `STYLE IS COLOR;`: 设置颜色, 使用`(BLACK, WHITE, RED, GREEN, BLUE, YELLOW)`这些规定好的关键字
- `STYLE IS LINE_WIDTH(CONST_ID);`: 设置线条宽度
- `STYLE IS (COLOR [, OPACITY [, LINE_WIDTH] ]);`: 设置颜色、透明度和线条宽度

```python
def style_value(lexer: Lexer) -> tuple:
    """STYLEVALUE → COLOR | CONST_ID | ( COLOR [, CONST_ID [, CONST_ID] ] )"""
    # 实现三种格式的支持：
    # 1. 单独颜色：STYLE IS RED;
    # 2. 单独线条粗细：STYLE IS 1.5;
    # 3. 复合格式：STYLE IS (RED, 0.5, 2.0);
```

#### 2.3.7 测试验证

通过多个测试文件验证语法分析器的正确性：

- correct_test.txt：验证正确语法的解析
- error_test.txt：验证错误处理机制
- expression_test.txt：验证表达式优先级和结合性
- style_test.txt：验证样式语句解析

### 2.4 语义分析器实现

#### 2.4.1 概述

语义分析器负责处理语法分析器生成的抽象语法树(AST)，执行实际的语义动作，如计算表达式的值、进行坐标变换以及绘制图形。它与语法分析器紧密结合，在解析每个语句时立即执行相应的语义动作。

#### 2.4.2 主要组件

##### SemanticContext 模块

SemanticContext模块负责存储全局绘图上下文和状态变量，是语义分析的核心数据存储。

###### 关键变量：

- `Origin_x`, `Origin_y`：平移原点坐标
- `Rot_ang`：旋转角度（弧度）
- `Scale_x`, `Scale_y`：X轴和Y轴缩放因子
- `Parameter_T`：FOR循环中的参数T值
- `StyleConfig`：绘图样式配置（颜色、透明度、线条宽度） 
    ```python
    StyleConfig = {
    "color": "#000000",    # 线条颜色（默认黑色）
    "opacity": 1.0,        # 透明度（0~1，默认不透明）
    "line_width": 1.0,     # 线条宽度（默认1.0）
    }
    ```
- `CachedPoints`：坐标缓存列表，用于批量绘制
    ```python
    CachedPoints = {
    "x": [],  # 缓存所有变换后的 X 坐标
    "y": []   # 缓存所有变换后的 Y 坐标
    }
    ```
- `AxisRange`：记录所有绘制点的xy坐标范围

###### 关键方法：

- `reset_context()`：重置所有全局参数和缓存，用于清空画布

##### SemanticUtils 模块

SemanticUtils模块包含语义分析的核心功能函数，负责表达式求值、坐标变换和图形绘制。

###### 关键方法：

- `get_expr_value(root: ExprNode) -> float`：深度优先后序遍历语法树，计算表达式值
- `calc_coord(x_expr: ExprNode, y_expr: ExprNode) -> tuple[float, float]`：坐标变换：原始坐标 → 缩放 → 旋转 → 平移
- `cache_points(start_expr: ExprNode, end_expr: ExprNode, step_expr: ExprNode, x_expr: ExprNode, y_expr: ExprNode) -> None`：根据FOR语句参数生成并缓存所有坐标点
- `batch_draw(ax: plt.Axes) -> None`：使用matplotlib批量绘制缓存的坐标点

#### 2.4.3 与语法分析器的集成

语义分析器与语法分析器采用紧密集成的方式，每个语句在语法分析完成后立即执行相应的语义动作。

##### 集成方式

1. 语法分析器的parse函数现在接受一个额外的`ax`参数（matplotlib的坐标轴对象）
2. 在每个语句处理函数中嵌入语义动作：
   - `origin_statement`：计算并设置平移原点
   - `scale_statement`：计算并设置缩放因子
   - `rot_statement`：计算并设置旋转角度
   - `style_statement`：更新样式配置
   - `for_statement`：计算坐标点并绘制图形

##### 数据传递

语义分析器通过以下方式与语法分析器传递数据：

1. 通过共享的`SemanticContext`模块存储和访问全局状态
2. 语法分析器将构建好的表达式语法树传递给语义分析器进行求值
3. 语法分析器将matplotlib的坐标轴对象传递给语义分析器用于绘图

#### 2.4.4 语义动作实现

##### 表达式求值

使用get_expr_value函数对表达式语法树进行深度优先遍历计算：

1. 常数节点：直接返回常数值
2. 参数节点(T)：返回全局变量T的值
3. 函数节点：计算子表达式值后调用函数指针
4. 运算符节点：递归计算左右子树并执行相应运算

##### 坐标变换

通过calc_coord函数实现从数学坐标到屏幕坐标的变换：

1. 计算原始坐标值（基于T的表达式值）
2. 应用缩放变换
3. 应用旋转变换（弧度制，逆时针为正）
4. 应用平移变换（窗口坐标系：Y轴向下，需翻转Y值以符合数学习惯）

##### 图形绘制

图形绘制分为两个阶段：

1. cache_points函数根据FOR语句的参数生成所有坐标点并缓存：
   - 计算循环参数（起始值、结束值、步长）
   - 遍历T值，计算每个点的坐标并存储到缓存中

2. batch_draw函数使用matplotlib批量绘制缓存的点：
   - 从样式配置中获取颜色、线条宽度和透明度
   - 使用matplotlib的plot函数绘制所有点
   - 计算并更新坐标范围信息

#### 2.4.5 坐标范围管理

##### AxisRange的作用

AxisRange用于记录所有绘制点的坐标范围，以便自动调整绘图区域。

##### set_axes_range函数

set_axes_range函数用于自动调整绘图区域以适应所绘制的图形：

1. 在加载脚本后调用，传入从语义分析中收集的坐标范围信息
2. 通过扩展图形的边界（每边增加50个单位）确保整个图形都能完整显示在画布上
3. 刷新画布以显示更新后的视图

#### 2.4.6 错误处理

语义分析器处理各种语义错误：

1. 除零错误：在表达式求值过程中检测并报告除零错误
2. 步长错误：检查FOR语句的步长是否为正数
3. 参数匹配错误：检查FOR语句的起始值、结束值和步长是否匹配

#### 2.4.7 测试验证

通过多个测试文件验证语义分析器的正确性：

- correct_test.txt：验证正确语义的执行

- coverage_test.txt：验证心形图片的绘制

    ![](./DrawLangCompiler.assets/heart.png)

- style_test.txt：验证样式设置的正确性

## 3. AI工具使用

在本次编译器实验开发过程中，我主要使用了两款AI工具：**Doubao**（豆包）和**Lingma**（通义灵码）。这两款工具在不同阶段为我的开发工作提供了有力支持。

### 3.1 AI辅助开发流程

#### 3.1.1 框架代码生成
我通过仔细阅读实验讲解PPT，深入分析每次实验需要完成的具体功能模块，将需求整理成详细的prompt，让AI生成基本的框架代码。在此过程中，我会对比PPT中提供的实现思路，严格审核AI生成的代码结构和逻辑，确保其符合实验要求。

例如，在词法分析器开发阶段，我将TokenDFA的状态转换逻辑和符号表设计要求整理成prompt，让AI生成基础的Lexer类框架和状态转换表，然后再根据PPT中的具体实现细节进行调整和完善。

#### 3.1.2 测试案例生成
为了确保代码的健壮性和覆盖率，我充分利用AI工具生成各种测试案例。通过描述具体的边界条件和异常情况，让AI帮助我设计能够覆盖各种边缘情况的测试用例。

例如，在语法分析器测试中，我让AI生成包含复杂表达式嵌套、运算符优先级混淆、缺少分号等各种语法错误的测试脚本，大大提高了测试的全面性。

#### 3.1.3 代码优化与调试
在AI生成的基础代码之上，我添加了大量的原创性代码，包括原创注释方式，样式语句和错误处理机制等。在调试过程中遇到问题时，我会将错误信息和相关代码片段提供给AI，获得问题分析和解决建议。

#### 3.1.4 代码分析与总结
在完成每个模块的开发和调试后，我会让AI对已完成的代码进行分析和总结，帮助我梳理实现思路，并生成相应的文档说明。

### 3.2 工具使用效果

通过合理使用AI工具，我显著提高了开发效率，能够在五天内完成复杂的编译器功能实现。同时，AI生成的代码质量较高，结构清晰，为我的二次开发和优化提供了良好基础。特别是在处理复杂的语法分析和语义分析逻辑时，AI的帮助让我能够更快地理解和实现相关算法。

## 4. 心得体会

通过本次编译器实验的开发实践，我对编译原理有了更深刻的理解和掌握。在完成实验的过程中，我遇到了许多挑战，同时也收获了很多宝贵的经验。

### 4.1 遇到的主要问题及解决方案

#### 4.1.1 词法分析阶段的问题

**问题1：注释处理的复杂性**
- **问题描述**：在实现多行注释(`/* */`)时，遇到了结束符`*/`由两个字符组成的问题，不能简单地当作单个字符处理。
- **解决方案**：采用前瞻读取策略，在检测到星号(*)字符后，立即读取下一个字符检查是否为斜杠(/)，如果不是则使用`back_char()`方法回退字符，确保不会遗漏注释内容中的星号字符。

**问题2：词法分析错误处理**
- **问题描述**：多行注释如果没有匹配到`*/`就到达文件末尾时，需要正确的错误处理机制。
- **解决方案**：在词法分析遇到多行注释开始符号`/*`时，如果直到文件末尾也没有找到匹配的结束符，则生成`ERRTOKEN`并返回相应的错误信息。

#### 4.1.2 语法分析阶段的问题

**问题3：运算符优先级冲突**
- **问题描述**：在处理`2**-2`这样的表达式时，由于幂运算符右侧只允许原子表达式，导致无法正确解析带有负号的指数。
- **解决方案**：修改`component`函数，将幂运算右侧的解析从`component`改为`factor`，允许先进行一元+/-运算再参与幂运算，从而正确解析此类表达式。

#### 4.1.3 语义分析阶段的问题

**问题4：坐标变换的数学实现**
- **问题描述**：在实现坐标变换时，需要正确处理缩放、旋转和平移的顺序，以及与matplotlib坐标系的差异。
- **解决方案**：严格按照"比例变换→旋转变换→平移变换"的顺序进行坐标变换，并注意处理Y轴方向的差异。

### 4.2 当前做法的优点

1. **模块化设计清晰**：将整个编译器分为词法分析、语法分析和语义分析三个独立模块，每个模块职责明确，便于开发和维护。
2. **良好的扩展性**：通过EBNF文法的扩展，轻松实现了STYLE语句等新功能，证明了架构设计的合理性。
3. **丰富的注释支持**：支持四种不同的注释方式，提高了语言的实用性。

### 4.3 当前做法的不足

1. **错误定位不够精确**：目前的错误报告缺乏具体的行号信息，用户难以快速定位错误位置。
2. **词法分析容错性有待提高**：遇到词法错误时直接返回`ERRTOKEN`，可能导致后续解析失败，缺乏更好的恢复机制。
3. **跨平台兼容性问题**：由于依赖Linux平台的tkinter，限制了程序的运行环境。

