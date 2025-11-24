from src.scanner.Lexer import Lexer
from src.scanner.TokenType import TokenType

def test_lexer(file_path: str):
    """测试词法分析器"""
    try:
        lexer = Lexer(file_path)
        print("="*80)
        print(f"测试文件：{file_path}")
        print("="*80)
        print(f"{'类型':<15} {'文本':<10} {'值':<12} {'函数指针'}")
        print("-"*80)
        while True:
            token = lexer.get_token()
            if token.type == TokenType.NONTOKEN:
                break
            print(token)
        lexer.close()
        print("="*80)
        print("测试完成！")
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在！")
    except Exception as e:
        print(f"错误：{str(e)}")

# 运行测试（需提前创建测试文件）
if __name__ == "__main__":
    test_lexer("correct_test.txt")
    test_lexer("error_test.txt")
    test_lexer("mixed_test.txt")