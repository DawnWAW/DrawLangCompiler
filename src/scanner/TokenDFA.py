from src.scanner.TokenType import TokenType

def is_letter(ch: str) -> bool:
    """判断字符是否为字母（含下划线，因正规式letter=[a-zA-Z_]）"""
    return ch.isalpha() or ch == "_"

def is_digit(ch: str) -> bool:
    """判断字符是否为数字"""
    return ch.isdigit()

# ---------------------------
# DFA状态转移表：(当前状态, 输入字符类型) -> 下一状态
# 字符类型：0=字母, 1=数字, 2=., 3=*, 4=/, 5=-, 6=+, 7=;, 8=(, 9=), 10=,, 11=其他, 12=#
# ---------------------------
TRANSITION_TABLE = {
    # 初态0的转移
    (0, 0): 1,    # 字母 -> 状态1（ID）
    (0, 1): 2,    # 数字 -> 状态2（CONST_ID）
    (0, 2): -1,   # 单独. -> 错误
    (0, 3): 4,    # * -> 状态4（待判断是MUL还是POWER）
    (0, 4): 6,    # / -> 状态6（DIV）
    (0, 5): 7,    # - -> 状态7（MINUS）
    (0, 6): 8,    # + -> 状态8（PLUS）
    (0, 12): 9,   # # -> 状态9（COMMENT）
    (0, 7): 10,   # ; -> 状态10（SEMICO）
    (0, 8): 11,   # ( -> 状态11（L_BRACKET）
    (0, 9): 12,   # ) -> 状态12（R_BRACKET）
    (0, 10): 13,  # , -> 状态13（COMMA）
    # 状态1（ID）的转移：字母/数字继续，其他终止
    (1, 0): 1,
    (1, 1): 1,
    # 状态2（CONST_ID-纯数字）的转移
    (2, 1): 2,    # 继续数字 -> 保持状态2
    (2, 2): 3,    # . -> 状态3（带小数点）
    # 状态3（CONST_ID-带小数点）的转移
    (3, 1): 3,    # 小数点后接数字 -> 保持状态3
    # 状态4（*）的转移：再遇* -> POWER，其他终止
    (4, 3): 5,    # * -> 状态5（POWER）
    # 状态6（/）的转移：再遇/ -> COMMENT,
    (6, 4): 9,    # / -> 状态9（COMMENT）
    # 状态6（/）的转移：再遇* -> COMMENT_START,
    (6, 3): 14,   # * -> 状态14（COMMENT_START）
    # 状态7（-）的转移：再遇- -> COMMENT
    (7, 5): 9,    # - -> 状态9（COMMENT）
}

# ---------------------------
# DFA终态表：状态 -> 对应的记号类别（非终态无条目）
# ---------------------------
FINAL_STATE_TABLE = {
    1: TokenType.ID,       # ID
    2: TokenType.CONST_ID, # CONST_ID（纯数字）
    3: TokenType.CONST_ID, # CONST_ID（带小数点）
    4: TokenType.MUL,      # MUL（单个*）
    5: TokenType.POWER,    # POWER（**）
    6: TokenType.DIV,      # DIV（/）
    7: TokenType.MINUS,    # MINUS（-）
    8: TokenType.PLUS,     # PLUS（+）
    9: TokenType.COMMENT,  # COMMENT（//或--或#）
    10: TokenType.SEMICO,  # SEMICO（;）
    11: TokenType.L_BRACKET,# L_BRACKET（(）
    12: TokenType.R_BRACKET,# R_BRACKET（)）
    13: TokenType.COMMA,   # COMMA（,）
    14: TokenType.COMMENT_START, # COMMENT_START（/*）
}

def get_char_type(ch: str) -> int:
    """将字符映射为字符类型编码（对应TRANSITION_TABLE的第二个参数）"""
    if is_letter(ch):
        return 0
    elif is_digit(ch):
        return 1
    elif ch == ".":
        return 2
    elif ch == "*":
        return 3
    elif ch == "/":
        return 4
    elif ch == "-":
        return 5
    elif ch == "+":
        return 6
    elif ch == ";":
        return 7
    elif ch == "(":
        return 8
    elif ch == ")":
        return 9
    elif ch == ",":
        return 10
    elif ch == "#":
        return 12
    else:
        return 11  # 其他字符(空格也会到这里)