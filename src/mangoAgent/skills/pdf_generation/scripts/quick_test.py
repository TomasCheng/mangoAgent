#!/usr/bin/env python3
"""
快速测试脚本
验证中文PDF生成功能是否正常工作
"""

import os
import sys
import tempfile

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chinese_pdf_generation():
    """测试中文PDF生成"""
    print("测试中文PDF生成功能")
    print("=" * 50)
    
    try:
        from chinese_pdf_generator import ChinesePDFGenerator
        
        # 创建测试内容
        test_content = """# 中文PDF生成测试

## 测试目的
验证ReportLab中文乱码问题是否已解决。

## 测试内容
- 中文字符显示
- 字体自动检测
- Markdown解析
- PDF生成

## 测试结果
如果这个PDF能正确显示中文，说明问题已解决。

## 代码块测试
```python
# 测试代码
def test_function():
    return "测试成功！"
```

## 结束
测试完成。
"""
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_md = f.name
        
        temp_pdf = temp_md.replace('.md', '.pdf')
        
        print(f"创建测试文件: {temp_md}")
        
        # 测试生成器
        generator = ChinesePDFGenerator()
        print(f"使用字体: {generator.font_name}")
        
        # 生成PDF
        success = generator.convert_markdown_to_pdf(
            input_file=temp_md,
            output_file=temp_pdf,
            title="中文PDF测试",
            author="测试系统"
        )
        
        # 检查结果
        if success and os.path.exists(temp_pdf):
            file_size = os.path.getsize(temp_pdf)
            print(f"\n✓ 测试成功！")
            print(f"  PDF文件: {temp_pdf}")
            print(f"  文件大小: {file_size:,} 字节")
            
            # 检查文件类型
            import subprocess
            try:
                result = subprocess.run(['file', temp_pdf], capture_output=True, text=True)
                if 'PDF' in result.stdout:
                    print(f"  ✓ 有效的PDF文件")
                else:
                    print(f"  ⚠ 文件类型异常: {result.stdout.strip()}")
            except:
                print(f"  ⚠ 无法验证文件类型")
            
            # 清理临时文件
            os.remove(temp_md)
            print(f"  ✓ 已清理临时文件")
            
            # 询问是否保留PDF
            keep = input("\n是否保留测试PDF文件？(y/n): ").lower().strip()
            if keep == 'y':
                new_name = "chinese_pdf_test_result.pdf"
                os.rename(temp_pdf, new_name)
                print(f"  PDF已保存为: {new_name}")
            else:
                os.remove(temp_pdf)
                print(f"  ✓ 已清理PDF文件")
            
            return True
        else:
            print(f"\n✗ 测试失败")
            # 清理临时文件
            if os.path.exists(temp_md):
                os.remove(temp_md)
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
            return False
            
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        print("请确保reportlab已安装: pip install reportlab")
        return False
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return False

def check_dependencies():
    """检查依赖"""
    print("\n检查依赖:")
    
    dependencies = [
        ('reportlab', 'PDF生成库'),
        ('os', '系统库'),
        ('sys', '系统库'),
        ('datetime', '时间库')
    ]
    
    all_ok = True
    for module, description in dependencies:
        try:
            if module == 'reportlab':
                import reportlab
                version = reportlab.__version__
                print(f"  ✓ {module}: {description} (版本: {version})")
            else:
                __import__(module)
                print(f"  ✓ {module}: {description}")
        except ImportError:
            print(f"  ✗ {module}: {description} - 未安装")
            all_ok = False
    
    return all_ok

def main():
    """主测试函数"""
    print("中文PDF生成功能测试")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n⚠ 缺少依赖，请先安装:")
        print("  pip install reportlab")
        return
    
    print("\n" + "=" * 50)
    
    # 运行测试
    if test_chinese_pdf_generation():
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("中文PDF生成功能正常工作")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ 测试失败")
        print("请检查错误信息")
        print("=" * 50)
        sys.exit(1)

if __name__ == '__main__':
    main()