import math
from src.scanner.TokenType import TokenType

class Token:
    def __init__(self):
        self.type: TokenType = TokenType.ERRTOKEN  # 记号类别
        self.lexeme: str = ""  # 原始输入字符串
        self.value: float = 0.0  # 常数的值（仅CONST_ID有效）
        self.func_ptr = None  # 函数指针（仅FUNC有效）

    def __str__(self):
        # 便于打印测试结果
        func_addr = hex(id(self.func_ptr)) if self.func_ptr else "None"
        value_str = f"{self.value:10.6f}" if isinstance(self.value, (int, float)) else f"{self.value}"
        return (f"TOKEN_TYPE: {self.type.value:12} | TEXT: {self.lexeme:8} | "
                f"VALUE:  {value_str} | FUNC_PTR: {func_addr}")

# STYLE颜色映射表
COLOR_MAP = {
    'RED': '#FF0000',
    'BLUE': '#0000FF',
    'GREEN': '#00FF00',
    'YELLOW': '#FFFF00',
    'BLACK': '#000000',
    'WHITE': '#FFFFFF'
}

# 符号表：(lexeme, token_type, value, func_ptr)
SYMBOL_TABLE = [
    # 常数名（CONST_ID）
    ("PI", TokenType.CONST_ID, math.pi, None),
    ("E", TokenType.CONST_ID, math.e, None),
    # 参数（T）
    ("T", TokenType.T, 0.0, None),
    # 函数（FUNC）：映射到Python内置数学函数
    ("SIN", TokenType.FUNC, 0.0, math.sin),
    ("COS", TokenType.FUNC, 0.0, math.cos),
    ("TAN", TokenType.FUNC, 0.0, math.tan),
    ("SQRT", TokenType.FUNC, 0.0, math.sqrt),
    ("EXP", TokenType.FUNC, 0.0, math.exp),
    ("LN", TokenType.FUNC, 0.0, math.log),
    # 保留字
    ("ORIGIN", TokenType.ORIGIN, 0.0, None),
    ("SCALE", TokenType.SCALE, 0.0, None),
    ("ROT", TokenType.ROT, 0.0, None),
    ("STYLE", TokenType.STYLE, 0.0, None),
    ("IS", TokenType.IS, 0.0, None),
    ("FOR", TokenType.FOR, 0.0, None),
    ("FROM", TokenType.FROM, 0.0, None),
    ("TO", TokenType.TO, 0.0, None),
    ("STEP", TokenType.STEP, 0.0, None),
    ("DRAW", TokenType.DRAW, 0.0, None),
    # 颜色
    ("RED", TokenType.COLOR, COLOR_MAP['RED'], None),
    ("BLUE", TokenType.COLOR, COLOR_MAP['BLUE'], None),
    ("GREEN", TokenType.COLOR, COLOR_MAP['GREEN'], None),
    ("YELLOW", TokenType.COLOR, COLOR_MAP['YELLOW'], None),
    ("BLACK", TokenType.COLOR, COLOR_MAP['BLACK'], None),
    ("WHITE", TokenType.COLOR, COLOR_MAP['WHITE'], None),
]

def lookup_symbol(lexeme: str) -> Token:
    """根据lexeme查询符号表，返回对应的Token"""
    lexeme_upper = lexeme.upper()  # 大小写不敏感
    for sym_lex, sym_type, sym_val, sym_func in SYMBOL_TABLE:
        if sym_lex == lexeme_upper:
            token = Token()
            token.type = sym_type
            token.lexeme = lexeme
            token.value = sym_val
            token.func_ptr = sym_func
            return token
    # 未找到：返回ID类型（理论上不会触发，因所有合法ID均在符号表中）
    token = Token()
    token.type = TokenType.ID
    token.lexeme = lexeme
    return token


if __name__ == "__main__":
    # 测试
    print("SYMBOL_TABLE：")
    for symbol in SYMBOL_TABLE:
        print(lookup_symbol(symbol[0]).__str__())
