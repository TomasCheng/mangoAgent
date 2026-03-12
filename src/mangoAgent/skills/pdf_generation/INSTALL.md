# PDF Generation Skill - Installation and Testing

## Quick Start

### 1. Install Dependencies
```bash
# Required dependency
pip install reportlab

# Optional dependencies (for advanced features)
pip install markdown pillow
```

### 2. Test the Skill
```bash
cd skills/pdf_generation/scripts

# Run quick test
python quick_test.py

# See usage examples
python example_usage.py
```

### 3. Generate Your First Chinese PDF
```bash
# Create a test markdown file
echo '# 测试文档

这是一个中文测试文档。

## 功能
- 中文显示
- PDF生成
- 自动字体检测

测试完成。' > test.md

# Generate PDF
python chinese_pdf_generator.py test.md test_output.pdf --title "测试文档"

# Check the result
open test_output.pdf  # On macOS
# or
start test_output.pdf  # On Windows
# or
xdg-open test_output.pdf  # On Linux
```

## Detailed Installation

### Prerequisites
- Python 3.6 or higher
- pip package manager
- Basic Chinese fonts installed on your system

### Step-by-Step Installation

#### 1. Clone or Navigate to Skill Directory
```bash
cd skills/pdf_generation
```

#### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install reportlab>=3.6.0
```

#### 3. Verify Installation
```bash
cd scripts
python -c "import reportlab; print(f'ReportLab version: {reportlab.__version__}')"
```

#### 4. Test Chinese Font Availability
```bash
python -c "
import os
fonts = [
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    'C:/Windows/Fonts/simhei.ttf',
    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
]
available = [f for f in fonts if os.path.exists(f)]
print(f'Available Chinese fonts: {available if available else \"None found\"}')
"
```

## Platform-Specific Setup

### macOS
```bash
# Check installed Chinese fonts
ls /System/Library/Fonts/*.ttc | grep -i "pingfang\|heiti"

# Install additional fonts (optional)
brew tap homebrew/cask-fonts
brew install --cask font-noto-sans-cjk
```

### Windows
```bash
# Check installed Chinese fonts
dir C:\Windows\Fonts\*hei*.*
dir C:\Windows\Fonts\*sun*.*

# Install Microsoft YaHei (if not present)
# Download from official Microsoft website
```

### Linux (Ubuntu/Debian)
```bash
# Install Chinese fonts
sudo apt-get update
sudo apt-get install fonts-wqy-microhei fonts-noto-cjk

# Verify installation
fc-list :lang=zh
```

## Testing the Skill

### Basic Test
```bash
cd skills/pdf_generation/scripts

# Run the comprehensive test
python quick_test.py
```

Expected output:
```
测试中文PDF生成功能
==================================================
创建测试文件: /tmp/tmp_xxxxxx.md
使用字体: PingFang
正在转换: /tmp/tmp_xxxxxx.md -> /tmp/tmp_xxxxxx.pdf
✓ 转换成功: /tmp/tmp_xxxxxx.pdf
✓ 文件大小: 45,678 字节

✓ 测试成功！
  PDF文件: /tmp/tmp_xxxxxx.pdf
  文件大小: 45,678 字节
  ✓ 有效的PDF文件
```

### Advanced Test
```bash
# Generate PDF with custom settings
python chinese_pdf_generator.py \
  test.md \
  custom_output.pdf \
  --title "自定义标题" \
  --author "自定义作者" \
  --font "Arial"
```

### Batch Test
```bash
# Create multiple test files
for i in {1..3}; do
  echo "# 测试文档 $i

  这是第 $i 个测试文档。

  ## 内容
  - 项目 $i.1
  - 项目 $i.2
  - 项目 $i.3

  文档 $i 结束。" > test_$i.md
done

# Convert all
for file in test_*.md; do
  python chinese_pdf_generator.py "$file" "${file%.md}.pdf"
done

# Check results
ls -la *.pdf
```

## Troubleshooting

### Common Issues

#### Issue 1: "No module named 'reportlab'"
**Solution:**
```bash
pip install reportlab
# or
pip3 install reportlab
# or
python -m pip install reportlab
```

#### Issue 2: Chinese characters still show as boxes
**Solution:**
1. Check if Chinese fonts are installed:
   ```bash
   python scripts/quick_test.py
   ```
2. Install Chinese fonts for your platform (see Platform-Specific Setup)
3. Specify a font manually:
   ```bash
   python chinese_pdf_generator.py input.md output.pdf --font "Arial"
   ```

#### Issue 3: Encoding errors when reading files
**Solution:**
1. Ensure files are saved as UTF-8
2. Use the built-in encoding detection:
   ```python
   # The generator automatically tries multiple encodings
   generator = ChinesePDFGenerator()
   generator.convert_markdown_to_pdf('file.md', 'output.pdf')
   ```

#### Issue 4: PDF generation is very slow
**Solution:**
1. Reduce document complexity
2. Process in smaller batches
3. Check system resources

### Debug Mode
```bash
# Enable debug output
cd scripts
python -c "
import sys
sys.path.insert(0, '.')
from chinese_pdf_generator import ChinesePDFGenerator

# Create generator with debug info
generator = ChinesePDFGenerator()
print(f'Font being used: {generator.font_name}')

# Test with a simple document
test_content = '# 测试\\n测试内容'
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
    f.write(test_content)
    temp_file = f.name

generator.convert_markdown_to_pdf(temp_file, 'debug_test.pdf')
import os
if os.path.exists('debug_test.pdf'):
    print(f'PDF generated: {os.path.getsize(\"debug_test.pdf\"):,} bytes')
    os.remove('debug_test.pdf')
os.remove(temp_file)
"
```

## Integration with Mango Agent

### As a Loaded Skill
```python
# In your Mango Agent task
from skills.pdf_generation.scripts.chinese_pdf_generator import ChinesePDFGenerator

def generate_documentation():
    generator = ChinesePDFGenerator()
    
    # Generate PDF from markdown
    success = generator.convert_markdown_to_pdf(
        'documentation.md',
        'output.pdf',
        title='项目文档',
        author='Mango Agent'
    )
    
    if success:
        print("文档生成成功")
    else:
        print("文档生成失败")
```

### In Automated Workflows
```python
# Example workflow for documentation generation
import os
from skills.pdf_generation.scripts.chinese_pdf_generator import ChinesePDFGenerator

class DocumentationWorkflow:
    def __init__(self):
        self.generator = ChinesePDFGenerator()
    
    def process_directory(self, input_dir, output_dir):
        """Convert all markdown files in directory to PDF"""
        os.makedirs(output_dir, exist_ok=True)
        
        for filename in os.listdir(input_dir):
            if filename.endswith('.md'):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, filename.replace('.md', '.pdf'))
                
                print(f"Processing: {filename}")
                self.generator.convert_markdown_to_pdf(input_path, output_path)
        
        print(f"Processed {len([f for f in os.listdir(output_dir) if f.endswith('.pdf')])} files")
```

## Performance Tips

### For Large Documents
1. Split into multiple files
2. Use simpler fonts
3. Reduce image resolution
4. Process in background

### For Batch Processing
1. Reuse generator instance
2. Cache font registration
3. Use multiprocessing for many files
4. Monitor memory usage

## Uninstallation

### Remove Dependencies
```bash
# Remove reportlab (if not used elsewhere)
pip uninstall reportlab

# Optional: remove other dependencies
pip uninstall markdown pillow
```

### Clean Up Generated Files
```bash
# Remove test files
rm -f test*.md test*.pdf debug_test.pdf

# Remove script caches
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Getting Help

### Check Documentation
```bash
# View skill documentation
cat SKILL.md

# View script help
cd scripts
python chinese_pdf_generator.py --help
```

### Run Diagnostics
```bash
cd scripts
python quick_test.py --verbose
```

### Report Issues
1. Run the diagnostic test
2. Note the error message
3. Check system font availability
4. Report with system information

## Next Steps

After successful installation:
1. Try the example scripts
2. Integrate with your projects
3. Customize styles as needed
4. Explore advanced features

---
*Installation Guide v1.0.0*
*Last Updated: 2026-03-12*