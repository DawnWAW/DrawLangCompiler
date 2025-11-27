from src.scanner.Lexer import Lexer
from src.scanner.TokenType import TokenType
from collections import defaultdict

def test_lexer(file_path: str):
    """测试词法分析器"""
    try:
        lexer = Lexer(file_path)
        print("="*80)
        print(f"测试文件：{file_path}")
        print("="*80)
        print(f"{'类型':<15} {'文本':<10} {'值':<12} {'函数指针'}")
        print("-"*80)
        
        # 记录各种类型的TOKEN数量
        token_counts = defaultdict(int)
        
        while True:
            token = lexer.get_token()
            if token.type == TokenType.NONTOKEN:
                break
            print(token)
            # 统计TOKEN类型数量
            token_counts[token.type.name] += 1
            
        lexer.close()
        print("="*80)
        
        # 输出统计结果
        print("TOKEN类型统计:")
        for token_type, count in sorted(token_counts.items()):
            print(f"  {token_type}: {count}")
        print(f"  总计: {sum(token_counts.values())}")
        
        print("测试完成！")
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在！")
    except Exception as e:
        print(f"错误：{str(e)}")

# 运行测试（需提前创建测试文件）
if __name__ == "__main__":
    test_lexer("../correct_test.txt")
    test_lexer("../error_test.txt")
    test_lexer("../mixed_test.txt")
    test_lexer("../comment_test.txt")
    test_lexer("../style_test.txt")