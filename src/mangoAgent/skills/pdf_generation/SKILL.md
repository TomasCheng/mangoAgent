# PDF Generation Skill

## Overview
This skill provides comprehensive PDF generation capabilities with special focus on solving Chinese character encoding issues in ReportLab. It includes ready-to-use scripts and best practices for generating professional PDF documents from various sources.

## Key Features

### 1. Chinese Character Support
- **Automatic font detection** for Chinese characters
- **Multi-platform support** (macOS, Windows, Linux)
- **Encoding handling** with UTF-8 as default
- **Fallback mechanisms** for missing fonts

### 2. Document Generation
- Markdown to PDF conversion
- Professional styling and formatting
- Table of contents support
- Page headers and footers
- Code block highlighting

### 3. Ready-to-Use Scripts
All scripts are available in the `scripts/` directory:

## Available Scripts

### 1. `chinese_pdf_generator.py` - Main Generator
The core script that solves Chinese character encoding issues in ReportLab.

**Usage:**
```bash
# Basic usage
python chinese_pdf_generator.py input.md output.pdf

# With custom title and author
python chinese_pdf_generator.py input.md output.pdf --title "文档标题" --author "作者"

# With specific font
python chinese_pdf_generator.py input.md output.pdf --font "/path/to/font.ttf"
```

**Key Features:**
- Automatic Chinese font detection
- Support for multiple encodings (UTF-8, GBK, GB2312, Big5)
- Professional document styling
- Error handling and fallbacks

### 2. `example_usage.py` - Usage Examples
Demonstrates various usage patterns and best practices.

**Run:**
```bash
python example_usage.py
```

**Shows:**
- Basic usage patterns
- Custom font configuration
- Batch conversion examples
- Troubleshooting guide

### 3. `quick_test.py` - Quick Verification
Tests if the PDF generation works correctly with Chinese characters.

**Run:**
```bash
python quick_test.py
```

**Verifies:**
- Dependencies are installed
- Chinese fonts are available
- PDF generation works
- Output quality

## Problem Solved: Chinese Character Encoding

### The Problem
When using ReportLab to generate PDFs with Chinese content, characters often appear as:
- Empty boxes □□□
- Garbled text ���
- Missing characters

### Root Causes
1. **Default Font Issue**: ReportLab uses Helvetica by default, which doesn't support Chinese characters
2. **Font Registration**: Chinese fonts need to be explicitly registered
3. **Encoding Mismatch**: File encoding may not be UTF-8

### The Solution

#### 1. Font Detection and Registration
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Detect and register Chinese fonts
font_paths = [
    # macOS
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    # Windows
    'C:/Windows/Fonts/simhei.ttf',
    # Linux
    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
]

for font_path in font_paths:
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
        break
```

#### 2. Style Configuration with Chinese Font
```python
from reportlab.lib.styles import ParagraphStyle

chinese_style = ParagraphStyle(
    'ChineseNormal',
    fontName='ChineseFont',  # Use registered Chinese font
    fontSize=12,
    leading=18,
    firstLineIndent=24  # Chinese paragraph indentation
)
```

#### 3. Encoding Handling
```python
def read_file_with_encoding(filepath):
    """Try multiple encodings for Chinese files"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Cannot read file with any encoding: {encodings}")
```

## Best Practices

### 1. Font Management
- Always check if Chinese fonts exist on the system
- Provide fallback to standard fonts (Arial, Helvetica)
- Log which font is being used for debugging

### 2. Encoding Strategy
- Use UTF-8 as the primary encoding
- Support common Chinese encodings (GBK, GB2312)
- Handle encoding errors gracefully

### 3. Performance Optimization
- Cache font registration
- Batch process multiple files
- Optimize PDF generation for large documents

### 4. Error Handling
- Catch and report font registration errors
- Handle missing files gracefully
- Provide meaningful error messages

## Platform-Specific Notes

### macOS
- Uses PingFang or STHeiti fonts by default
- Fonts are located in `/System/Library/Fonts/`
- Excellent Chinese typography support

### Windows
- Uses SimHei or SimSun fonts
- Fonts are in `C:/Windows/Fonts/`
- Good Chinese support with proper fonts installed

### Linux
- Uses WenQuanYi or Noto fonts
- May require additional font packages
- Check `/usr/share/fonts/` for available fonts

## Common Issues and Solutions

### Issue 1: Chinese characters show as boxes
**Solution:** Ensure Chinese fonts are properly registered and used in styles.

### Issue 2: File encoding errors
**Solution:** Use the `read_file_with_encoding()` function that tries multiple encodings.

### Issue 3: PDF generation is slow
**Solution:** 
- Cache font objects
- Reduce document complexity
- Process in batches if possible

### Issue 4: Font not found on system
**Solution:** 
- Install Chinese font packages
- Use standard fonts as fallback
- Provide clear installation instructions

## Integration with Mango Agent

### As a Skill
```python
from skills.pdf_generation.scripts.chinese_pdf_generator import ChinesePDFGenerator

# Use in Mango Agent tasks
generator = ChinesePDFGenerator()
generator.convert_markdown_to_pdf('document.md', 'output.pdf')
```

### In Workflows
1. **Documentation Generation**: Automatically generate PDF documentation
2. **Report Creation**: Create Chinese reports from data
3. **Content Publishing**: Convert markdown content to printable PDFs

## Testing

### Run Tests
```bash
# Test basic functionality
cd skills/pdf_generation/scripts
python quick_test.py

# See usage examples
python example_usage.py
```

### Expected Results
- PDF files should open without errors
- Chinese characters should display correctly
- Document formatting should be professional
- File sizes should be reasonable (100-500KB for typical documents)

## Dependencies

### Required
```bash
pip install reportlab
```

### Optional (for advanced features)
```bash
pip install markdown       # For markdown parsing
pip install pillow         # For image support
```

## Contributing

### Adding New Features
1. Add new scripts to `scripts/` directory
2. Update this SKILL.md document
3. Add tests for new functionality
4. Ensure backward compatibility

### Reporting Issues
1. Describe the problem clearly
2. Include system information
3. Provide sample files if possible
4. Suggest possible solutions

## Version History

### v1.0.0 (Current)
- Initial release with Chinese character support
- Automatic font detection
- Ready-to-use scripts
- Comprehensive documentation

### Planned Features
- Image support in PDFs
- Advanced markdown parsing
- Template system
- Batch processing GUI

## License
This skill is part of the Mango Agent project. See main project for license details.

## Support
For issues with Chinese PDF generation:
1. Check font installation on your system
2. Verify file encoding is UTF-8
3. Run the quick test script
4. Consult the troubleshooting guide in `example_usage.py`

---
*Last Updated: 2026-03-12*
*Maintainer: Mango Agent Team*