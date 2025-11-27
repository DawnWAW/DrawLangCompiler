# 原创性工作说明

## 修改点1：#号单行注释支持
### 修改点说明：
增加了对Python风格的单行注释（#）的支持，丰富了注释语法的多样性。

### 修改的方式（代码的解释）：
1. 在 [TokenDFA.py](../src/scanner/TokenDFA.py) 中添加了字符类型12来表示#号字符
    ```python
    elif ch == "#":
        return 12
    ```
2. 增加了从初始状态0到状态9的转移规则，当遇到#号时识别为[COMMENT](../src/scanner/TokenType.py)
3. 复用了现有的单行注释处理逻辑，在[Lexer.py](../src/scanner/Lexer.py)的主循环中通过continue跳过注释内容到行尾

## 修改点2：多行注释支持
### 修改点说明：
增加了对C语言风格的多行注释（`/* */`）的支持，使词法分析器能够正确识别和跳过多行注释内容。

### 修改的方式：
1. 在 [TokenType.py](../src/scanner/TokenType.py) 中新增了[COMMENT_START](../src/scanner/TokenType.py)枚举类型
2. 在 [TokenDFA.py](../src/scanner/TokenDFA.py) 中扩展了状态转移表，增加了状态14[COMMENT_START](../src/scanner/TokenDFA.py)
3. 增加了从状态6（/）到状态14的转移，状态6`/`情况下再遇到`*`时识别为[COMMENT_START](../src/scanner/TokenType.py)
4. 在 [Lexer.py](../src/scanner/Lexer.py) 中添加了专门处理[COMMENT_START](../src/scanner/TokenType.py)的逻辑，循环读取字符直到遇到[*/](../Compiler_c/README.TXT)结束符
   ```python
   elif token.type == TokenType.COMMENT_START:
    # 多行注释开始，跳过到结束符 */
    while True:
        comment_char = self.get_char()
        if comment_char == "":  # 文件结束
            break
        if comment_char == "*":
            # 检查下一个字符是否为 /
            next_char = self.get_char()
            if next_char == "/":
                # 找到结束符 */
                break
            else:
                # 不是结束符，回退字符
                self.back_char()
    continue  # 继续进入循环，获取下一个记号
   ```
   直接用代码识别多行注释结尾, 而不是继续通过状态转移直到多行注释结束, 避免了过多无用的状态转移

### 修改中遇到的问题及解决方案：
#### 问题1：多行注释的结束符[*/](../Compiler_c/README.TXT)是两个字符组成的序列，不能简单地当作单个字符处理
- 解决方案：在检测到星号(*)字符后，立即读取下一个字符检查是否为斜杠(/)，如果不是则使用[back_char()](../src/scanner/Lexer.py)方法回退字符，确保不会遗漏注释内容中的星号字符
#### 问题2: 多行注释如果没有匹配到`*/`，直到文末也没有报错
- 解决方案: 在词法分析遇到多行注释符开始符号`/*`时，如果直到文末也没有匹配到, 则判定为ERRTOKEN
  ```python
   elif token.type == TokenType.COMMENT_START:
   # 多行注释开始，跳过到结束符 */
   while True:
     comment_char = self.get_char()
     if comment_char == "":  # 文件结束
         token.type = TokenType.ERRTOKEN
         token.lexeme = "Unterminated comment"
         return token
  ```
