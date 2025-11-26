# 函数绘图语言简化版编译器实现步骤清单
本清单聚焦核心功能，以“可落地、低复杂度”为原则，覆盖从词法分析到图形绘制的全流程，适配实验场景需求。


## 一、前期准备：明确语言规则（1-2小时）
### 1. 确定核心语法要素
| 要素类型  | 具体内容                                                     |
| --------- | ------------------------------------------------------------ |
| 保留字    | `ORIGIN`、`SCALE`、`ROT`、`IS`、`FOR`、`FROM`、`TO`、`STEP`、`DRAW` |
| 运算符    | +（加）、-（减）、*（乘）、/（除）、**（幂运算）             |
| 常量/参数 | 数值常量（如3.14、5）、符号常量（PI=3.14159、E=2.71828）、参数T |
| 函数      | sin、cos、tan（仅保留基础三角函数，降低复杂度）              |
| 分隔符    | ;（语句结束）、( )（括号）、,（坐标分隔）                    |
| 注释      | // 单行注释（忽略到行尾）                                    |

### 2. 确定核心语句格式（仅保留4类关键语句）
1. **原点语句**：`ORIGIN IS (表达式, 表达式);`（如`ORIGIN IS (300, 200);`）
2. **缩放语句**：`SCALE IS (表达式, 表达式);`（如`SCALE IS (50, 50);`）
3. **旋转语句**：`ROT IS 表达式;`（如`ROT IS PI/2;`）
4. **绘图语句**：`FOR T FROM 表达式 TO 表达式 STEP 表达式 DRAW (表达式, 表达式);`（如`FOR T FROM 0 TO 2*PI STEP PI/50 DRAW (cos(T), sin(T));`）

### 3. 确定语义规则（固定核心逻辑）
- 图形变换顺序：**比例变换 → 旋转变换 → 平移变换**（实验固定规则，无需灵活配置）
- 默认值：原点(0,0)、缩放(1,1)、旋转0（不旋转）
- 坐标体系：屏幕左上角为原点，x向右增，y向下增（匹配`matplotlib`默认坐标系）


## 二、阶段1：实现词法分析器（3-4小时）
### 目标
将源程序字符串拆分为记号（Token），使用Python字典/类存储Token信息。

### 核心步骤
1. **定义Token数据结构**
   ```python
   from dataclasses import dataclass
   
   @dataclass
   class Token:
       type: str  # 记号类别：'ORIGIN'/'SCALE'/'CONST_ID'等
       lexeme: str  # 原始字符串
       value: float = None  # 常量值（仅CONST_ID有效）
       func: callable = None  # 函数（仅FUNC有效）
   ```

2. **实现符号表（字典形式）**
   ```python
   import math
   
   SYMBOL_TABLE = {
       'PI': Token('CONST_ID', 'PI', math.pi),
       'E': Token('CONST_ID', 'E', math.e),
       'T': Token('T', 'T'),
       'SIN': Token('FUNC', 'SIN', func=math.sin),
       'COS': Token('FUNC', 'COS', func=math.cos),
       'TAN': Token('FUNC', 'TAN', func=math.tan),
       'ORIGIN': Token('ORIGIN', 'ORIGIN'),
       'SCALE': Token('SCALE', 'SCALE'),
       'ROT': Token('ROT', 'ROT'),
       'IS': Token('IS', 'IS'),
       'FOR': Token('FOR', 'FOR'),
       'FROM': Token('FROM', 'FROM'),
       'TO': Token('TO', 'TO'),
       'STEP': Token('STEP', 'STEP'),
       'DRAW': Token('DRAW', 'DRAW')
   }
   ```

3. **实现扫描函数（get_token）**
   - 使用正则表达式简化匹配逻辑（Python优势）
   ```python
   import re
   
   # 正则匹配模式：按优先级排序
   TOKEN_PATTERNS = [
       ('NUMBER', r'\d+\.?\d*|\.\d+'),  # 数字常量
       ('ID', r'[A-Za-z]+'),  # 标识符
       ('POWER', r'\*\*'),  # 幂运算
       ('MUL', r'\*'),
       ('DIV', r'/'),
       ('PLUS', r'\+'),
       ('MINUS', r'-'),
       ('L_BRACKET', r'\('),
       ('R_BRACKET', r'\)'),
       ('COMMA', r','),
       ('SEMICO', r';'),
       ('WHITESPACE', r'[ \t\n]+'),  # 空白字符
       ('COMMENT', r'//.*')  # 注释
   ]
   pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_PATTERNS)
   
   def get_token(source_code, pos):
       # 从pos位置开始扫描并返回下一个Token及新位置
       match = re.match(pattern, source_code[pos:])
       if not match:
           return Token('ERRTOKEN', source_code[pos]), pos + 1
       token_type = match.lastgroup
       lexeme = match.group()
       pos += len(lexeme)
       
       if token_type == 'WHITESPACE' or token_type == 'COMMENT':
           return get_token(source_code, pos)  # 跳过空白和注释
       elif token_type == 'ID':
           upper_lex = lexeme.upper()
           return SYMBOL_TABLE.get(upper_lex, Token('ID', lexeme)), pos
       elif token_type == 'NUMBER':
           return Token('CONST_ID', lexeme, float(lexeme)), pos
       else:
           return Token(token_type, lexeme), pos
   ```

4. **测试词法分析器**
   ```python
   def test_lexer(source_code):
       pos = 0
       while pos < len(source_code):
           token, pos = get_token(source_code, pos)
           if token.type == 'ERRTOKEN':
               print(f"错误：非法字符 {token.lexeme}")
               break
           print(f"<{token.type}, {token.lexeme}, {token.value or ''}>")
   ```


## 三、阶段2：实现语法分析器（4-5小时）
### 目标
验证Token流语法正确性，构建表达式抽象语法树（AST）。

### 核心步骤
1. **定义AST节点类**
   ```python
   class ExprNode:
       def __init__(self, node_type, **kwargs):
           self.type = node_type  # 'CONST'/'T'/'FUNC'/'OP'
           self.attrs = kwargs
   
       def __repr__(self):
           return f"ExprNode({self.type}, {self.attrs})"
   ```

2. **实现递归下降分析器**
   ```python
   class Parser:
       def __init__(self, source_code):
           self.source = source_code
           self.pos = 0
           self.current_token, self.pos = get_token(source_code, 0)
   
       def match(self, expected_type):
           # 匹配预期Token类型，不匹配则报错
           if self.current_token.type == expected_type:
               self.current_token, self.pos = get_token(self.source, self.pos)
           else:
               raise SyntaxError(f"预期 {expected_type}，但得到 {self.current_token.type}")
   
       def parse_program(self):
           # 程序 = 若干语句+分号
           while self.current_token.type != 'NONTOKEN':
               self.parse_statement()
               self.match('SEMICO')
   
       def parse_statement(self):
           # 语句 = 原点/缩放/旋转/绘图语句
           if self.current_token.type == 'ORIGIN':
               self.parse_origin_stmt()
           elif self.current_token.type == 'SCALE':
               self.parse_scale_stmt()
           elif self.current_token.type == 'ROT':
               self.parse_rot_stmt()
           elif self.current_token.type == 'FOR':
               self.parse_for_stmt()
           else:
               raise SyntaxError(f"未知语句类型：{self.current_token.type}")
   
       # 其他解析方法：parse_origin_stmt/parse_scale_stmt/parse_rot_stmt/parse_for_stmt
       # 表达式解析方法：parse_expression/parse_term/parse_factor/parse_atom（遵循EBNF规则）
   ```

3. **实现递归下降子程序（关键函数）**

   | 函数名       | 功能                                                         |
   | ------------ | ------------------------------------------------------------ |
   | Program()    | 循环调用Statement()和MatchToken(SEMICO)，处理所有语句        |
   | Statement()  | 根据当前Token类型，调用OriginStmt()/ScaleStmt()等子函数      |
   | Expression() | 处理加减运算，调用Term()，循环匹配+/-并构建运算节点          |
   | Term()       | 处理乘除运算，调用Factor()，循环匹配*/并构建运算节点         |
   | Factor()     | 处理幂运算，调用Atom()，匹配**并构建右结合运算节点           |
   | Atom()       | 处理原子（常量/T/函数/括号表达式），构建叶子节点或递归调用Expression() |
   | MatchToken() | 验证当前Token是否符合预期，符合则获取下一个Token，否则报错   |

4. **测试语法分析器**
   - 可视化AST结构（使用递归打印）
   ```python
   def print_ast(node, indent=0):
       print(' ' * indent + f"{node.type}: {node.attrs}")
       if node.type == 'OP':
           print_ast(node.attrs['left'], indent + 4)
           print_ast(node.attrs['right'], indent + 4)
       elif node.type == 'FUNC':
           print_ast(node.attrs['child'], indent + 4)
   ```


## 四、阶段3：实现语义分析与绘图（3-4小时）
### 目标
计算AST值，处理坐标变换，使用matplotlib绘制图形。

### 核心步骤
1. **定义全局状态管理**
   ```python
   class GraphicsState:
       def __init__(self):
           self.origin = (0.0, 0.0)
           self.scale = (1.0, 1.0)
           self.rot = 0.0
           self.parameter = 0.0  # 当前T值
   
   state = GraphicsState()
   ```

2. **实现表达式求值函数**
   ```python
   def evaluate(node):
       if node.type == 'CONST':
           return node.attrs['value']
       elif node.type == 'T':
           return state.parameter
       elif node.type == 'FUNC':
           return node.attrs['func'](evaluate(node.attrs['child']))
       elif node.type == 'OP':
           left_val = evaluate(node.attrs['left'])
           right_val = evaluate(node.attrs['right'])
           op = node.attrs['op']
           if op == 'PLUS':
               return left_val + right_val
           elif op == 'MINUS':
               return left_val - right_val
           # 补充其他运算符实现...
   ```

3. **坐标变换与绘图**
   ```python
   import matplotlib.pyplot as plt
   
   class Drawer:
       def __init__(self):
           self.fig, self.ax = plt.subplots(figsize=(8, 6))
           self.points = []
   
       def transform(self, x, y):
           # 比例→旋转→平移变换
           x_scaled = x * state.scale[0]
           y_scaled = y * state.scale[1]
           
           # 旋转变换
           x_rot = x_scaled * math.cos(state.rot) + y_scaled * math.sin(state.rot)
           y_rot = y_scaled * math.cos(state.rot) - x_scaled * math.sin(state.rot)
           
           # 平移变换
           return x_rot + state.origin[0], y_rot + state.origin[1]
   
       def draw_pixel(self, x, y):
           self.points.append(self.transform(x, y))
   
       def render(self):
           # 批量绘制所有点
           if self.points:
               xs, ys = zip(*self.points)
               self.ax.scatter(xs, ys, s=1, c='red')
           plt.show()
   ```


## 五、阶段4：测试与优化（2-3小时）
### 1. 编写核心测试用例
| 测试场景      | 用例示例                                                     |
| ------------- | ------------------------------------------------------------ |
| 基础图形-直线 | `ORIGIN IS (200,200); FOR T FROM 0 TO 100 STEP 1 DRAW (T, T);` |
| 基础图形-圆   | `ORIGIN IS (300,300); SCALE IS (50,50); FOR T FROM 0 TO 2*PI STEP PI/50 DRAW (cos(T), sin(T));` |
| 旋转图形      | `ROT IS PI/4;`（加在圆的用例前，验证旋转效果）               |
| 错误场景-词法 | 输入`ROT IS PI/全角逗号6;`（验证非法字符报错）               |
| 错误场景-语法 | 输入`FOR T FROM 0 TO 100 DRAW (T,0);`（缺STEP，验证语法错误） |

### 2. 简化优化（降低复杂度）
- 暂不支持嵌套表达式（如`sin(cos(T))`），仅支持单层函数（如`sin(T)`）
- 忽略复杂错误恢复，遇到错误直接退出并提示位置
- 绘图效率优化：批量收集坐标点，最后一次性绘制（减少绘图库调用次数）


## 六、交付物清单
1. 源代码文件
   - `lexer.py`：词法分析器
   - `parser.py`：语法分析器
   - `interpreter.py`：语义分析与绘图逻辑
   - `main.py`：主程序入口

2. 测试用例（Python脚本形式）
3. 运行说明（含pip安装依赖：`pip install matplotlib`）


该方案保留核心功能逻辑，充分利用Python的正则表达式、面向对象特性和matplotlib库简化实现，总耗时可控制在10-15小时，更适合快速开发验证。