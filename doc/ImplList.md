# 函数绘图语言简化版编译器实现步骤清单
本清单聚焦核心功能，以“可落地、低复杂度”为原则，覆盖从词法分析到图形绘制的全流程，适配实验场景需求。


## 一、前期准备：明确语言规则（1-2小时）
### 1. 确定核心语法要素
| 要素类型  | 具体内容                                                     |
| --------- | ------------------------------------------------------------ |
| 保留字    | ORIGIN、SCALE、ROT、IS、FOR、FROM、TO、STEP、DRAW            |
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
将源程序字符串拆分为「记号（Token）」，如`ROT IS PI/6;`拆为 `<ROT, "ROT">`、`<IS, "IS">`、`<CONST_ID, "PI", 3.14159>`、`<DIV, "/">`、`<CONST_ID, "6", 6.0>`、`<SEMICO, ";")`

### 核心步骤
1. **定义记号结构（用结构体/类表示）**
   ```c
   // C语言示例，Python可简化为字典
   typedef struct Token {
       enum TokenType type;  // 记号类别：ORIGIN/SCALE/CONST_ID等
       char* lexeme;         // 原始字符串（如"PI"、"/"）
       double value;         // 常量值（仅CONST_ID有效）
       double (*func)(double); // 函数指针（仅FUNC有效，如sin）
   } Token;
   ```

2. **编写符号表（区分ID类记号）**
   ```c
   // 存储保留字、常量、函数，用于ID匹配
   struct Token SymbolTable[] = {
       {CONST_ID, "PI", 3.1415926, NULL},
       {CONST_ID, "E", 2.71828, NULL},
       {T, "T", 0.0, NULL},
       {FUNC, "SIN", 0.0, sin},
       {FUNC, "COS", 0.0, cos},
       {ORIGIN, "ORIGIN", 0.0, NULL},
       // 补充其他保留字...
   };
   ```

3. **实现核心扫描函数（GetToken）**
   - 步骤1：跳过空白字符（空格、换行、制表符）
   - 步骤2：识别字符类型，分场景处理：
     - 字母开头：匹配ID/保留字（查符号表）
     - 数字开头：匹配CONST_ID（处理整数/小数，如123、45.6）
     - 运算符/分隔符：匹配+、-、*、/、**、;、(、)、,（注意**需多字符匹配）
   - 步骤3：返回Token，遇到文件结束返回`NONTOKEN`，非法字符返回`ERRTOKEN`

4. **测试词法分析器**
   - 输入测试文件（如`test.dl`），打印每个Token的类型、字符串、值
   - 验证用例：`ROT IS PI/6;` 应输出正确Token序列，无遗漏/错误


## 三、阶段2：实现语法分析器（4-5小时）
### 目标
验证Token流语法正确性，构建「表达式语法树」，如`PI/6`构建为：`DIV节点（左：PI常量节点，右：6常量节点）`

### 核心步骤
1. **改写文法为EBNF（消除左递归/二义性，仅保留核心规则）**
   ```ebnf
   // 程序 = 若干语句+分号
   Program → { Statement SEMICO }
   // 语句 = 原点/缩放/旋转/绘图语句
   Statement → OriginStmt | ScaleStmt | RotStmt | ForStmt
   // 原点语句：ORIGIN IS (表达式,表达式)
   OriginStmt → ORIGIN IS L_BRACKET Expression COMMA Expression R_BRACKET
   // 缩放语句：SCALE IS (表达式,表达式)
   ScaleStmt → SCALE IS L_BRACKET Expression COMMA Expression R_BRACKET
   // 旋转语句：ROT IS 表达式
   RotStmt → ROT IS Expression
   // 绘图语句：FOR T FROM 表达式 TO 表达式 STEP 表达式 DRAW (表达式,表达式)
   ForStmt → FOR T FROM Expression TO Expression STEP Expression DRAW L_BRACKET Expression COMMA Expression R_BRACKET
   // 表达式：优先级从低到高（+- → */ → ** → 原子）
   Expression → Term { (PLUS | MINUS) Term }
   Term → Factor { (MUL | DIV) Factor }
   Factor → Atom [ POWER Factor ]  // POWER（**）右结合
   Atom → CONST_ID | T | FUNC L_BRACKET Expression R_BRACKET | L_BRACKET Expression R_BRACKET
   ```

2. **定义语法树节点结构**
   ```c
   typedef struct ExprNode {
       enum NodeType type;  // 节点类型：CONST/T/FUNC/OP（运算）
       union {
           double const_val;          // 常量值（CONST节点）
           double* parm_ptr;          // 参数T指针（T节点）
           struct {                   // 函数节点（FUNC）
               double (*func)(double);
               struct ExprNode* child;
           } func_node;
           struct {                   // 运算节点（OP：+/-/*//**）
               enum OpType op;
               struct ExprNode* left;
               struct ExprNode* right;
           } op_node;
       } content;
   } ExprNode;
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
   - 输入合法语句，打印语法树结构（如先序遍历输出节点类型）
   - 验证错误场景：缺少分号、括号不匹配、FOR语句缺STEP，应提示错误位置


## 四、阶段3：实现语义分析与绘图（3-4小时）
### 目标
计算语法树值，处理坐标变换，最终绘制图形（核心是“解释执行”）

### 核心步骤
1. **定义全局状态变量（存储图形参数）**
   ```c
   double OriginX = 0.0, OriginY = 0.0;  // 原点坐标
   double ScaleX = 1.0, ScaleY = 1.0;    // 缩放比例
   double RotAng = 0.0;                  // 旋转角度（弧度）
   double Parameter = 0.0;               // 参数T的当前值
   ```

2. **实现表达式求值函数（GetExprVal）**
   - 逻辑：深度优先后序遍历语法树，递归计算每个节点值
   ```c
   double GetExprVal(ExprNode* root) {
       if (root == NULL) return 0.0;
       switch (root->type) {
           case CONST: return root->content.const_val;
           case T: return *root->content.parm_ptr;  // 取Parameter当前值
           case FUNC: return (*root->content.func_node.func)(GetExprVal(root->content.func_node.child));
           case OP: {
               double left = GetExprVal(root->content.op_node.left);
               double right = GetExprVal(root->content.op_node.right);
               switch (root->content.op_node.op) {
                   case PLUS: return left + right;
                   case MINUS: return left - right;
                   // 补充*/**运算...
               }
           }
       }
   }
   ```

3. **实现坐标变换函数（CalcScreenCoord）**
   - 逻辑：按“比例→旋转→平移”顺序，将原始坐标转为屏幕坐标
   ```c
   void CalcScreenCoord(ExprNode* x_expr, ExprNode* y_expr, double* screen_x, double* screen_y) {
       // 1. 计算原始坐标
       double x = GetExprVal(x_expr) * ScaleX;
       double y = GetExprVal(y_expr) * ScaleY;
       // 2. 旋转变换（逆时针）
       double temp = x * cos(RotAng) + y * sin(RotAng);
       y = y * cos(RotAng) - x * sin(RotAng);
       x = temp;
       // 3. 平移变换
       *screen_x = x + OriginX;
       *screen_y = y + OriginY;
   }
   ```

4. **实现绘图逻辑（分语句处理）**
   - 原点/缩放/旋转语句：更新全局变量（如`OriginX = GetExprVal(x_expr)`）
   - FOR绘图语句：循环遍历T的取值范围，计算每个点坐标并绘制
     ```c
     void ProcessForStmt(ExprNode* start, ExprNode* end, ExprNode* step, ExprNode* x_expr, ExprNode* y_expr) {
         double s = GetExprVal(start);
         double e = GetExprVal(end);
         double st = GetExprVal(step);
         for (Parameter = s; Parameter <= e; Parameter += st) {
             double sx, sy;
             CalcScreenCoord(x_expr, y_expr, &sx, &sy);
             DrawPixel((int)sx, (int)sy);  // 调用绘图库接口（如matplotlib的scatter）
         }
     }
     ```

5. **集成绘图库（以Python matplotlib为例）**
   - 初始化画布：`plt.figure(figsize=(8,6))`，设置坐标轴范围
   - 实现`DrawPixel`：用`plt.scatter(sx, sy, s=2, c='red')`绘制点
   - 最后调用`plt.show()`显示图形


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
1. 源代码文件（按模块拆分）
   - `scanner.c/scanner.h`：词法分析器
   - `parser.c/parser.h`：语法分析器
   - `semantic.c/semantic.h`：语义分析与绘图
   - `main.c`：主程序（初始化→调用分析器→绘图）
2. 测试用例文件（3-5个，覆盖合法/错误场景）
3. 运行说明（编译命令、运行步骤、效果截图）


通过以上步骤，可在12-18小时内完成简化版编译器，核心功能完整且符合实验要求。若需扩展（如支持更多函数、颜色设置），可在该基础上逐步添加模块。