from src.parser.Parser import parse

def test_parser(file_path: str):
    """测试语法分析器"""
    try:
        print("="*80)
        print(f"测试文件：{file_path}")
        print("="*80)
        
        # 调用语法分析器
        parse(file_path)
        
        print("="*80)
        print("测试完成！\n")
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在！\n")
    except Exception as e:
        print(f"错误：{str(e)}\n")

# 运行测试（需提前创建测试文件）
if __name__ == "__main__":
    test_parser("../correct_test.txt")
    test_parser("../error_test.txt")
    test_parser("../mixed_test.txt")
    test_parser("../comment_test.txt")
    test_parser("../expression_test.txt")