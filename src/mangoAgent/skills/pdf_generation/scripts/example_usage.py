#!/usr/bin/env python3
"""
中文PDF生成器使用示例
展示如何解决ReportLab中文乱码问题
"""

import os
import sys

# 添加当前目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chinese_pdf_generator import ChinesePDFGenerator

def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("中文PDF生成器 - 基本使用示例")
    print("=" * 60)
    
    # 创建生成器（自动检测字体）
    generator = ChinesePDFGenerator()
    
    # 示例Markdown内容
    markdown_content = """# 中文测试文档

## 概述
这是一个测试中文PDF生成功能的文档。

## 功能特点
- 支持中文显示
- 自动检测系统字体
- 处理Markdown格式
- 生成专业PDF

## 代码示例
```python
# 这是一个Python代码示例
def hello_world():
    print("你好，世界！")
    
hello_world()
```

## 注意事项
1. 确保系统有中文字体
2. 使用UTF-8编码保存文件
3. 测试生成的PDF文件

## 总结
中文PDF生成已成功解决乱码问题。
"""
    
    # 保存为临时文件
    temp_file = "temp_chinese_test.md"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"创建测试文件: {temp_file}")
    
    # 转换为PDF
    output_file = "chinese_test_output.pdf"
    success = generator.convert_markdown_to_pdf(
        input_file=temp_file,
        output_file=output_file,
        title="中文测试文档",
        author="Mango Agent"
    )
    
    # 清理临时文件
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    if success:
        print(f"\n✓ 示例完成！")
        print(f"  输出文件: {output_file}")
        print(f"  文件大小: {os.path.getsize(output_file):,} 字节")
    else:
        print("\n✗ 示例失败")

def example_custom_font():
    """自定义字体示例"""
    print("\n" + "=" * 60)
    print("自定义字体示例")
    print("=" * 60)
    
    # 指定字体（如果知道系统字体路径）
    font_options = [
        # macOS
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        # Windows
        'C:/Windows/Fonts/simhei.ttf',
        # 通用
        'Arial',
        'Helvetica'
    ]
    
    for font_path in font_options:
        if font_path in ['Arial', 'Helvetica'] or os.path.exists(font_path):
            print(f"尝试字体: {font_path}")
            try:
                generator = ChinesePDFGenerator(font_name=font_path)
                print(f"  ✓ 可以使用")
                break
            except Exception as e:
                print(f"  ✗ 不可用: {e}")
                continue
    
    print("\n提示: 如果不指定字体，生成器会自动检测最佳字体")

def example_batch_conversion():
    """批量转换示例"""
    print("\n" + "=" * 60)
    print("批量转换示例")
    print("=" * 60)
    
    # 创建生成器
    generator = ChinesePDFGenerator()
    
    # 假设有多个Markdown文件
    files_to_convert = [
        ("document1.md", "用户手册"),
        ("document2.md", "技术文档"),
        ("document3.md", "API参考")
    ]
    
    print("批量转换流程:")
    for input_file, title in files_to_convert:
        output_file = input_file.replace('.md', '.pdf')
        print(f"  • {input_file} -> {output_file} ({title})")
    
    print("\n代码示例:")
    print("""
# 批量转换代码
generator = ChinesePDFGenerator()

for input_file, title in files_to_convert:
    if os.path.exists(input_file):
        output_file = input_file.replace('.md', '.pdf')
        generator.convert_markdown_to_pdf(
            input_file=input_file,
            output_file=output_file,
            title=title
        )
    """)

def troubleshooting_guide():
    """故障排除指南"""
    print("\n" + "=" * 60)
    print("故障排除指南")
    print("=" * 60)
    
    common_issues = [
        {
            "issue": "中文显示为方框或乱码",
            "cause": "字体未正确注册或系统缺少中文字体",
            "solution": "1. 检查系统字体\n2. 指定字体路径\n3. 使用标准字体如Arial"
        },
        {
            "issue": "文件读取失败",
            "cause": "文件编码不是UTF-8",
            "solution": "1. 确保文件使用UTF-8编码\n2. 使用支持多种编码的读取方法"
        },
        {
            "issue": "PDF生成缓慢",
            "cause": "文件过大或字体复杂",
            "solution": "1. 分割大文件\n2. 使用简单字体\n3. 优化内容"
        },
        {
            "issue": "特殊字符显示异常",
            "cause": "字体不支持某些Unicode字符",
            "solution": "1. 使用支持更广字符集的字体\n2. 替换或省略特殊字符"
        }
    ]
    
    for i, issue in enumerate(common_issues, 1):
        print(f"{i}. {issue['issue']}")
        print(f"   原因: {issue['cause']}")
        print(f"   解决: {issue['solution']}")
        print()

def main():
    """主函数"""
    print("中文PDF生成解决方案")
    print("=" * 60)
    
    # 运行示例
    example_basic_usage()
    example_custom_font()
    example_batch_conversion()
    troubleshooting_guide()
    
    print("=" * 60)
    print("使用说明:")
    print("1. 基本使用: python chinese_pdf_generator.py input.md output.pdf")
    print("2. 指定标题: python chinese_pdf_generator.py input.md output.pdf --title '文档标题'")
    print("3. 指定字体: python chinese_pdf_generator.py input.md output.pdf --font '/path/to/font.ttf'")
    print("4. 查看帮助: python chinese_pdf_generator.py --help")
    print("=" * 60)

if __name__ == '__main__':
    main()