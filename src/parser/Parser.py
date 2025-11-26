from src.scanner.Lexer import Lexer
from src.scanner.TokenType import TokenType
from src.scanner.Token import Token
from src.parser.ExprNode import ExprNode

# 全局变量：当前扫描到的记号
current_token: Token = None
# 全局参数 T：所有 T 节点绑定此变量
global_T = 0.0

def fetch_token(lexer: Lexer) -> None:
    """获取下一个记号，更新 current_token"""
    global current_token
    current_token = lexer.get_token()
    if current_token.type == TokenType.ERRTOKEN:
        raise SyntaxError(f"Invalid character encountered: '{current_token.lexeme}'")


def match_token(expected_type: TokenType, lexer: Lexer) -> None:
    """匹配预期记号，不匹配则抛出语法错误"""
    global current_token
    if current_token.type != expected_type:
        raise SyntaxError(
            f"Syntax Error：Expect {expected_type.value}，got '{current_token.lexeme}'"
        )
    # 匹配成功，获取下一个记号
    fetch_token(lexer)

def make_expr_node(op_code: TokenType, *args) -> ExprNode:
    """创建语法树节点（工厂函数）"""
    node = ExprNode(op_code)
    if op_code == TokenType.CONST_ID:
        # 常数节点：args 为 (常量值)
        node.const_val = args[0]
    elif op_code == TokenType.T:
        # 参数节点：绑定全局 T
        node.param_ptr = lambda: global_T  # 使用 lambda 模拟指针
    elif op_code == TokenType.FUNC:
        # 函数节点：args 为 (函数指针, 子节点)
        node.func_ptr = args[0]
        node.child = args[1]
    else:
        # 二元运算节点：args 为 (左子节点, 右子节点)
        node.left = args[0]
        node.right = args[1]
    return node

# --- 递归下降子程序 ---

def atom(lexer: Lexer) -> ExprNode:
    """Atom → CONST_ID | T | FUNC ( Expression ) | ( Expression )"""
    global current_token
    token = current_token
    if token.type == TokenType.CONST_ID:
        # CONST_ID
        node = make_expr_node(TokenType.CONST_ID, token.value)
        match_token(TokenType.CONST_ID, lexer)
        return node
    elif token.type == TokenType.T:
        # T
        node = make_expr_node(TokenType.T)
        match_token(TokenType.T, lexer)
        return node
    elif token.type == TokenType.FUNC:
        # FUNC ( Expression )
        func_ptr = token.func_ptr
        match_token(TokenType.FUNC, lexer)
        match_token(TokenType.L_BRACKET, lexer)
        expr_node = expression(lexer)
        match_token(TokenType.R_BRACKET, lexer)
        return make_expr_node(TokenType.FUNC, func_ptr, expr_node)
    elif token.type == TokenType.L_BRACKET:
        # ( Expression )
        match_token(TokenType.L_BRACKET, lexer)
        expr_node = expression(lexer)
        match_token(TokenType.R_BRACKET, lexer)
        return expr_node
    else:
        # 无效记号
        raise SyntaxError(f"Syntax Error：Not a valid atom: '{token.lexeme}'")

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

def factor(lexer: Lexer) -> ExprNode:
    """Factor → ( PLUS | MINUS ) Factor | Component（一元运算）"""
    global current_token
    token = current_token
    if token.type in (TokenType.PLUS, TokenType.MINUS):
        op_token = token
        match_token(op_token.type, lexer)
        factor_node = factor(lexer)
        zero_node = make_expr_node(TokenType.CONST_ID, 0.0)
        return make_expr_node(op_token.type, zero_node, factor_node)
    else:
        return component(lexer)

def term(lexer: Lexer) -> ExprNode:
    """Term → Factor { ( MUL | DIV ) Factor }（左结合）"""
    left_node = factor(lexer)
    global current_token
    while current_token.type in (TokenType.MUL, TokenType.DIV):
        op_token = current_token
        match_token(op_token.type, lexer)
        right_node = factor(lexer)
        left_node = make_expr_node(op_token.type, left_node, right_node)
    return left_node

def expression(lexer: Lexer) -> ExprNode:
    """Expression → Term { ( PLUS | MINUS ) Term }（左结合）"""
    left_node = term(lexer)
    global current_token
    # + - 都符合下一步
    while current_token.type in (TokenType.PLUS, TokenType.MINUS):
        op_token = current_token
        match_token(op_token.type, lexer)
        # 创建右节点
        right_node = term(lexer)
        # 将已有的左右节点整合为一颗子树, 作为新的左节点返回
        left_node = make_expr_node(op_token.type, left_node, right_node)
    return left_node

def origin_statement(lexer: Lexer) -> None:
    """OriginStatment → ORIGIN IS ( Expression , Expression )"""
    match_token(TokenType.ORIGIN, lexer)
    match_token(TokenType.IS, lexer)
    match_token(TokenType.L_BRACKET, lexer)
    x_expr = expression(lexer)
    match_token(TokenType.COMMA, lexer)
    y_expr = expression(lexer)
    match_token(TokenType.R_BRACKET, lexer)
    # (测试用)打印树
    print(f"parsed: ORIGIN IS ({x_expr}, {y_expr})")

def scale_statement(lexer: Lexer) -> None:
    """ScaleStatment → SCALE IS ( Expression , Expression )"""
    match_token(TokenType.SCALE, lexer)
    match_token(TokenType.IS, lexer)
    match_token(TokenType.L_BRACKET, lexer)
    x_scale = expression(lexer)
    match_token(TokenType.COMMA, lexer)
    y_scale = expression(lexer)
    match_token(TokenType.R_BRACKET, lexer)
    # (测试用)打印树
    print(f"parsed: SCALE IS ({x_scale}, {y_scale})")

def rot_statement(lexer: Lexer) -> None:
    """RotStatment → ROT IS Expression"""
    match_token(TokenType.ROT, lexer)
    match_token(TokenType.IS, lexer)
    rot_expr = expression(lexer)
    # (测试用)打印树
    print(f"parsed: ROT IS {rot_expr}")

def for_statement(lexer: Lexer) -> None:
    """ForStatment → FOR T FROM Expression TO Expression STEP Expression DRAW ( Expression , Expression )"""
    global global_T
    match_token(TokenType.FOR, lexer)
    match_token(TokenType.T, lexer)
    match_token(TokenType.FROM, lexer)
    start_expr = expression(lexer)
    match_token(TokenType.TO, lexer)
    end_expr = expression(lexer)
    match_token(TokenType.STEP, lexer)
    step_expr = expression(lexer)
    match_token(TokenType.DRAW, lexer)
    match_token(TokenType.L_BRACKET, lexer)
    x_expr = expression(lexer)
    match_token(TokenType.COMMA, lexer)
    y_expr = expression(lexer)
    match_token(TokenType.R_BRACKET, lexer)
    # (测试用)打印树
    print(f"parsed: FOR T FROM {start_expr} TO {end_expr} STEP {step_expr} DRAW ({x_expr}, {y_expr})")

def statement(lexer: Lexer) -> None:
    """Statement → OriginStatment | ScaleStatment | RotStatment | ForStatment"""
    global current_token
    token_type = current_token.type
    if token_type == TokenType.ORIGIN:
        origin_statement(lexer)
    elif token_type == TokenType.SCALE:
        scale_statement(lexer)
    elif token_type == TokenType.ROT:
        rot_statement(lexer)
    elif token_type == TokenType.FOR:
        for_statement(lexer)
    # TODO: StyleStatement 原创点
    # elif token_type == TokenType.STYLE;
    #     style_statement(lexer)
    else:
        raise SyntaxError(f"Syntax Error: Invalid statement starting with '{current_token.lexeme}'")

def program(lexer: Lexer) -> None:
    """Program → { Statement ; }（0 个或多个语句，以分号结束）"""
    global current_token
    # 初始化：获取第一个记号
    fetch_token(lexer)
    while current_token.type != TokenType.NONTOKEN:
        # 解析一个语句
        statement(lexer)
        # 匹配语句结束符分号
        match_token(TokenType.SEMICO, lexer)

    print("\nParsing completed: No syntax errors found")

def parse(file_path: str) -> None:
    """Parser 入口：初始化 Lexer，启动语法分析"""
    # 初始化词法分析器
    lexer = Lexer(file_path)
    try:
        # 启动语法分析
        program(lexer)
    except SyntaxError as e:
        print(f"\nSyntax parsing failed: {e}")
    finally:
        # 关闭文件
        lexer.close()