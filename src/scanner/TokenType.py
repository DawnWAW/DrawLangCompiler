from enum import Enum

class TokenType(Enum):
    # 保留字（一字一码）
    ORIGIN = "ORIGIN"    # 坐标平移语句标识
    SCALE = "SCALE"      # 比例设置语句标识
    ROT = "ROT"          # 角度旋转语句标识
    IS = "IS"            # 赋值关键字
    FOR = "FOR"          # 循环绘图语句标识
    FROM = "FROM"        # 循环起始关键字
    TO = "TO"            # 循环结束关键字
    STEP = "STEP"        # 循环步长关键字
    DRAW = "DRAW"        # 绘图关键字
    # 其他记号类别
    T = "T"              # 唯一参数
    ID = "ID"            # 未匹配的标识符（后续查符号表）
    COMMENT = "COMMENT"  # 注释
    COMMENT_START = "COMMENT_START"  # 多行注释开始
    CONST_ID = "CONST_ID"# 常数（字面量或PI/E）
    FUNC = "FUNC"        # 函数（Sin/Cos等）
    # 运算符
    PLUS = "+"           # 加法
    MINUS = "-"          # 减法/负号
    MUL = "*"            # 乘法
    DIV = "/"            # 除法
    POWER = "**"         # 幂运算（右结合）
    # 分隔符
    SEMICO = ";"         # 语句结束符
    L_BRACKET = "("      # 左括号
    R_BRACKET = ")"      # 右括号
    COMMA = ","          # 分隔符
    # 特殊记号
    NONTOKEN = "NONTOKEN"# 源程序结束
    ERRTOKEN = "ERRTOKEN"# 非法输入