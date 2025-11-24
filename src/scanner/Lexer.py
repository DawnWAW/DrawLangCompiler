from src.scanner.TokenDFA import *
from src.scanner.Token import *
from src.scanner.TokenType import TokenType


class Lexer:
    def __init__(self, file_path: str):
        self.file = open(file_path, "r", encoding="utf-8", errors="ignore")  # 打开源文件
        self.current_char: str = ""  # 当前读取的字符
        self.position: int = 0  # 当前字符位置（用于错误提示）

    def get_char(self) -> str:
        """读取下一个字符，统一转为大写（大小写不敏感）"""
        self.current_char = self.file.read(1).upper()
        self.position += 1
        return self.current_char

    def back_char(self) -> None:
        """回退一个字符（文件结束或换行不回退）"""
        if self.current_char != "" and self.current_char != "\n":
            self.file.seek(self.file.tell() - 1)
            self.position -= 1
            self.current_char = ""

    def pre_process(self) -> str:
        """预处理：跳过所有空白字符，返回第一个非空白字符"""
        while True:
            ch = self.get_char()
            if ch == "":  # 文件结束
                return ""
            if not ch.isspace():  # 非空白字符，返回
                return ch

    def get_token(self) -> Token | None:
        """核心函数：识别并返回一个记号"""
        token = Token()
        while True:
            # 步骤1：预处理，跳过空白字符
            first_char = self.pre_process()
            if first_char == "":  # 文件结束
                token.type = TokenType.NONTOKEN
                return token

            # 步骤2：DFA状态转移，扫描记号
            current_state = 0  # 初态
            token.lexeme = first_char  # 初始化记号文本
            char_type = get_char_type(first_char)
            current_state = TRANSITION_TABLE.get((current_state, char_type), -1) # 根据状态转移表获取下一个状态

            if current_state == -1:  # 初态转移失败（非法字符）
                token.type = TokenType.ERRTOKEN
                token.lexeme = first_char
                return token

            # 继续扫描后续字符，直到无法转移
            while True:
                next_char = self.get_char()
                if next_char == "":  # 文件结束，终止扫描
                    break
                next_char_type = get_char_type(next_char)
                next_state = TRANSITION_TABLE.get((current_state, next_char_type), -1)
                if next_state == -1:  # 无法转移，回退字符
                    self.back_char()
                    break
                # 可以转移，更新状态和记号文本
                current_state = next_state
                token.lexeme += next_char

            # 步骤3：后处理，根据终态确定记号类型
            token.type = FINAL_STATE_TABLE.get(current_state, TokenType.ERRTOKEN)
            if token.type == TokenType.ERRTOKEN:
                # 非终态，标记为非法记号
                token.lexeme = token.lexeme  # 保留非法文本
                return token
            elif token.type == TokenType.ID:
                # 查符号表，细分ID类型
                token = lookup_symbol(token.lexeme)
                return token
            elif token.type == TokenType.CONST_ID:
                # 转换为数值
                try:
                    token.value = float(token.lexeme)
                except ValueError:
                    token.type = TokenType.ERRTOKEN
                return token
            elif token.type == TokenType.COMMENT:
                # 跳过注释到行尾，重新扫描下一个记号
                while True:
                    comment_char = self.get_char()
                    if comment_char == "" or comment_char == "\n":
                        break
                continue  # 重新进入循环，获取下一个记号
            else:
                # 其他记号（运算符、分隔符、保留字）直接返回
                return token

    def close(self) -> None:
        """关闭文件"""
        self.file.close()