from src.scanner.TokenType import TokenType


class ExprNode:
    """语法树节点类"""

    def __init__(self, op_code: TokenType):
        self.op_code = op_code  # 记号类型（如 PLUS、CONST_ID、FUNC 等）
        self.left = None  # 左子节点（二元运算用）
        self.right = None  # 右子节点（二元运算用）
        self.child = None  # 子节点（函数调用/一元运算用）
        self.const_val = 0.0  # 常数值（CONST_ID 用）
        self.param_ptr = None  # 参数指针（T 用，绑定全局参数 T）
        self.func_ptr = None  # 函数指针（FUNC 用）

    def __str__(self, indent: int = 0) -> str:
        """递归打印语法树"""
        indent_str = "  " * indent
        if self.op_code == TokenType.CONST_ID:
            return f"{indent_str}{self.op_code.value}: {self.const_val:.6f}"
        elif self.op_code == TokenType.T:
            return f"{indent_str}{self.op_code.value}"
        elif self.op_code == TokenType.FUNC:
            func_name = getattr(self.func_ptr, '__name__', 'unknown_func')
            return f"{indent_str}{func_name}(\n{self.child.__str__(indent + 1)}\n{indent_str})"
        else:
            res = f"{indent_str}{self.op_code.value}\n"
            if self.left:
                res += self.left.__str__(indent + 1) + "\n"
            if self.right:
                res += self.right.__str__(indent + 1)
            return res