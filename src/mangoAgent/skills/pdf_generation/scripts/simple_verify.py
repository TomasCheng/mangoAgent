#!/usr/bin/env python3
"""
简单验证脚本
检查PDF生成技能的基本功能
"""

import os
import sys

def check_script_structure():
    """检查脚本结构"""
    print("检查PDF生成技能脚本结构")
    print("=" * 50)
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(scripts_dir)
    
    required_files = [
        'chinese_pdf_generator.py',
        'example_usage.py',
        'quick_test.py'
    ]
    
    print("脚本目录:", scripts_dir)
    print("\n找到的文件:")
    for file in sorted(files):
        if file.endswith('.py'):
            print(f"  ✓ {file}")
    
    print("\n检查必要文件:")
    all_present = True
    for req_file in required_files:
        if req_file in files:
            print(f"  ✓ {req_file}")
        else:
            print(f"  ✗ {req_file} - 缺失")
            all_present = False
    
    return all_present

def check_dependencies():
    """检查依赖"""
    print("\n检查Python依赖:")
    
    try:
        import reportlab
        print(f"  ✓ reportlab - 版本: {reportlab.__version__}")
        return True
    except ImportError:
        print("  ✗ reportlab - 未安装")
        print("    安装命令: pip install reportlab")
        return False

def check_fonts():
    """检查中文字体"""
    print("\n检查系统中文字体:")
    
    font_paths = [
        # macOS
        ('/System/Library/Fonts/PingFang.ttc', 'PingFang (macOS)'),
        ('/System/Library/Fonts/STHeiti Light.ttc', 'STHeiti (macOS)'),
        # Windows
        ('C:/Windows/Fonts/simhei.ttf', 'SimHei (Windows)'),
        ('C:/Windows/Fonts/simsun.ttc', 'SimSun (Windows)'),
        # Linux
        ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WenQuanYi (Linux)'),
    ]
    
    found_fonts = []
    for path, name in font_paths:
        if os.path.exists(path):
            found_fonts.append(name)
            print(f"  ✓ {name}")
        else:
            print(f"  - {name} (未找到)")
    
    if found_fonts:
        print(f"\n找到 {len(found_fonts)} 种中文字体")
        return True
    else:
        print("\n⚠ 未找到中文字体，PDF可能无法正确显示中文")
        print("  建议安装系统字体或使用Arial/Helvetica")
        return False

def test_import():
    """测试导入功能"""
    print("\n测试脚本导入:")
    
    try:
        # 添加当前目录到路径
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, scripts_dir)
        
        # 测试导入主生成器
        from chinese_pdf_generator import ChinesePDFGenerator
        print("  ✓ 成功导入 ChinesePDFGenerator")
        
        # 创建实例
        generator = ChinesePDFGenerator()
        print(f"  ✓ 创建生成器实例，使用字体: {generator.font_name}")
        
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False

def main():
    """主验证函数"""
    print("PDF生成技能验证")
    print("=" * 50)
    
    # 检查脚本结构
    structure_ok = check_script_structure()
    
    # 检查依赖
    deps_ok = check_dependencies()
    
    # 检查字体
    fonts_ok = check_fonts()
    
    # 测试导入
    import_ok = test_import()
    
    print("\n" + "=" * 50)
    print("验证结果:")
    
    if all([structure_ok, deps_ok, import_ok]):
        print("✅ 基本验证通过")
        print("\n下一步:")
        print("1. 运行测试: python quick_test.py")
        print("2. 查看示例: python example_usage.py")
        print("3. 生成PDF: python chinese_pdf_generator.py input.md output.pdf")
    else:
        print("❌ 验证失败")
        
        if not deps_ok:
            print("\n问题: 缺少依赖")
            print("解决: pip install reportlab")
        
        if not import_ok:
            print("\n问题: 脚本导入失败")
            print("解决: 检查Python路径和脚本结构")
    
    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()