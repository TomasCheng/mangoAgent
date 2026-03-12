#!/usr/bin/env python3
"""
中文PDF生成器 - 解决ReportLab中文乱码问题
专门处理中文内容的PDF生成，支持系统字体自动检测
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

class ChinesePDFGenerator:
    """
    中文PDF生成器
    解决ReportLab默认字体不支持中文的问题
    自动检测系统字体，支持macOS、Windows、Linux
    """
    
    def __init__(self, font_name=None):
        """
        初始化中文PDF生成器
        
        Args:
            font_name: 指定字体名称，如果为None则自动检测
        """
        self.font_name = font_name or self._detect_chinese_font()
        self._register_fonts()
        self.styles = self._create_styles()
        
    def _detect_chinese_font(self):
        """
        自动检测系统中文字体
        
        Returns:
            可用的中文字体名称
        """
        # 常见的中文字体路径
        font_paths = [
            # macOS 字体
            ('/System/Library/Fonts/PingFang.ttc', 'PingFang'),
            ('/System/Library/Fonts/STHeiti Light.ttc', 'STHeiti-Light'),
            ('/System/Library/Fonts/STHeiti Medium.ttc', 'STHeiti-Medium'),
            ('/Library/Fonts/Arial Unicode.ttf', 'Arial-Unicode'),
            
            # Windows 字体
            ('C:/Windows/Fonts/simhei.ttf', 'SimHei'),
            ('C:/Windows/Fonts/simsun.ttc', 'SimSun'),
            ('C:/Windows/Fonts/msyh.ttc', 'Microsoft-YaHei'),
            
            # Linux 字体
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WenQuanYi-MicroHei'),
            ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK'),
            
            # 通用字体（最后尝试）
            ('Arial', 'Arial'),
            ('Helvetica', 'Helvetica'),
        ]
        
        for font_path, font_name in font_paths:
            if font_path in ['Arial', 'Helvetica']:
                # 标准字体，总是可用
                print(f"使用标准字体: {font_name}")
                return font_name
                
            if os.path.exists(font_path):
                try:
                    # 尝试注册字体
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✓ 检测到中文字体: {font_name} ({font_path})")
                    return font_name
                except Exception as e:
                    print(f"⚠ 字体注册失败 {font_path}: {e}")
                    continue
        
        print("⚠ 未找到中文字体，使用默认Helvetica（可能不支持所有中文）")
        return 'Helvetica'
    
    def _register_fonts(self):
        """注册字体"""
        try:
            # 如果字体名是路径，需要注册
            if self.font_name in ['PingFang', 'STHeiti-Light', 'STHeiti-Medium', 
                                 'SimHei', 'SimSun', 'Microsoft-YaHei',
                                 'WenQuanYi-MicroHei', 'NotoSansCJK']:
                # 这些字体已经在_detect_chinese_font中注册过了
                pass
            elif self.font_name == 'Arial-Unicode':
                pdfmetrics.registerFont(TTFont('Arial-Unicode', '/Library/Fonts/Arial Unicode.ttf'))
            elif self.font_name not in ['Arial', 'Helvetica']:
                # 尝试作为路径处理
                if os.path.exists(self.font_name):
                    pdfmetrics.registerFont(TTFont('CustomChinese', self.font_name))
                    self.font_name = 'CustomChinese'
        except Exception as e:
            print(f"字体注册警告: {e}")
    
    def _create_styles(self):
        """创建中文样式"""
        styles = getSampleStyleSheet()
        
        # 标题样式
        title_style = ParagraphStyle(
            'ChineseTitle',
            parent=styles['Title'],
            fontName=self.font_name,
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50'),
            leading=32
        )
        
        # 一级标题
        h1_style = ParagraphStyle(
            'ChineseH1',
            parent=styles['Heading1'],
            fontName=self.font_name,
            fontSize=22,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#EBF5FB'),
            borderColor=colors.HexColor('#3498DB'),
            borderWidth=1,
            borderPadding=10,
            leading=26
        )
        
        # 二级标题
        h2_style = ParagraphStyle(
            'ChineseH2',
            parent=styles['Heading2'],
            fontName=self.font_name,
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#34495E'),
            leading=22
        )
        
        # 三级标题
        h3_style = ParagraphStyle(
            'ChineseH3',
            parent=styles['Heading3'],
            fontName=self.font_name,
            fontSize=16,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#2C3E50'),
            leading=20
        )
        
        # 正文样式
        normal_style = ParagraphStyle(
            'ChineseNormal',
            parent=styles['Normal'],
            fontName=self.font_name,
            fontSize=12,
            spaceAfter=8,
            leading=18,
            alignment=TA_JUSTIFY,
            firstLineIndent=24
        )
        
        # 列表样式
        list_style = ParagraphStyle(
            'ChineseList',
            parent=styles['Normal'],
            fontName=self.font_name,
            fontSize=12,
            spaceAfter=6,
            leftIndent=20,
            leading=18
        )
        
        # 代码样式（使用等宽字体）
        code_style = ParagraphStyle(
            'ChineseCode',
            parent=styles['Code'],
            fontName='Courier',
            fontSize=11,
            backColor=colors.HexColor('#F8F9FA'),
            borderColor=colors.HexColor('#E9ECEF'),
            borderWidth=1,
            borderPadding=10,
            leftIndent=15,
            rightIndent=15,
            spaceAfter=10,
            spaceBefore=10,
            leading=16
        )
        
        # 页脚样式
        footer_style = ParagraphStyle(
            'ChineseFooter',
            parent=styles['Normal'],
            fontName=self.font_name,
            fontSize=10,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER
        )
        
        return {
            'title': title_style,
            'h1': h1_style,
            'h2': h2_style,
            'h3': h3_style,
            'normal': normal_style,
            'list': list_style,
            'code': code_style,
            'footer': footer_style
        }
    
    def convert_markdown_to_pdf(self, input_file, output_file, title=None, author=None):
        """
        将Markdown文件转换为PDF
        
        Args:
            input_file: 输入Markdown文件路径
            output_file: 输出PDF文件路径
            title: 文档标题（可选）
            author: 作者（可选）
            
        Returns:
            bool: 是否成功
        """
        print(f"正在转换: {input_file} -> {output_file}")
        print(f"使用字体: {self.font_name}")
        
        # 读取文件（支持多种编码）
        content = self._read_file_with_encoding(input_file)
        if content is None:
            return False
        
        # 解析Markdown
        parsed = self._parse_markdown(content)
        
        # 创建PDF文档
        doc_title = title or os.path.basename(input_file).replace('.md', '')
        doc_author = author or "Mango Agent"
        
        doc = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=doc_title,
            author=doc_author
        )
        
        # 构建内容
        story = self._build_story(parsed, doc_title)
        
        # 生成PDF
        try:
            doc.build(story)
            file_size = os.path.getsize(output_file)
            print(f"✓ 转换成功: {output_file}")
            print(f"✓ 文件大小: {file_size:,} 字节")
            return True
        except Exception as e:
            print(f"✗ PDF生成失败: {e}")
            return False
    
    def _read_file_with_encoding(self, filepath):
        """使用多种编码尝试读取文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"文件读取错误 ({encoding}): {e}")
                continue
        
        print(f"✗ 无法读取文件: {filepath}，尝试了编码: {encodings}")
        return None
    
    def _parse_markdown(self, content):
        """解析Markdown内容"""
        lines = content.split('\n')
        parsed = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                parsed.append(('empty', ''))
                i += 1
                continue
            
            # 处理标题
            if line.startswith('# '):
                parsed.append(('h1', line[2:]))
                i += 1
            elif line.startswith('## '):
                parsed.append(('h2', line[3:]))
                i += 1
            elif line.startswith('### '):
                parsed.append(('h3', line[4:]))
                i += 1
            # 处理代码块
            elif line.startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1
                parsed.append(('code', '\n'.join(code_lines)))
            # 处理列表
            elif line.startswith('- ') or line.startswith('* '):
                list_items = []
                while i < len(lines) and (lines[i].startswith('- ') or lines[i].startswith('* ')):
                    list_items.append(lines[i][2:])
                    i += 1
                parsed.append(('list', list_items))
            # 处理普通段落
            else:
                paragraph_lines = []
                while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('-') and not lines[i].startswith('```'):
                    paragraph_lines.append(lines[i])
                    i += 1
                if paragraph_lines:
                    paragraph_text = ' '.join(paragraph_lines)
                    parsed.append(('paragraph', paragraph_text))
            
            if i < len(lines) and not lines[i].strip():
                i += 1
        
        return parsed
    
    def _build_story(self, parsed, title):
        """构建PDF内容"""
        story = []
        
        # 添加标题
        story.append(Paragraph(title, self.styles['title']))
        story.append(Spacer(1, 0.3*inch))
        
        # 处理解析后的内容
        for element_type, content in parsed:
            if element_type == 'empty':
                story.append(Spacer(1, 12))
            elif element_type == 'h1':
                story.append(Paragraph(content, self.styles['h1']))
                story.append(Spacer(1, 10))
            elif element_type == 'h2':
                story.append(Paragraph(content, self.styles['h2']))
                story.append(Spacer(1, 8))
            elif element_type == 'h3':
                story.append(Paragraph(content, self.styles['h3']))
                story.append(Spacer(1, 6))
            elif element_type == 'code':
                story.append(Paragraph("代码示例:", self.styles['h3']))
                story.append(Paragraph(f'<font name="Courier">{content}</font>', self.styles['code']))
                story.append(Spacer(1, 12))
            elif element_type == 'list':
                for item in content:
                    story.append(Paragraph(f"• {item}", self.styles['list']))
                story.append(Spacer(1, 10))
            elif element_type == 'paragraph':
                story.append(Paragraph(content, self.styles['normal']))
                story.append(Spacer(1, 10))
        
        # 添加文档信息
        story.append(PageBreak())
        story.append(Paragraph("文档信息", self.styles['h1']))
        story.append(Spacer(1, 20))
        
        info_text = f"""
        文档生成信息：
        
        • 生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
        • 文档版本：1.0.0
        • 生成系统：Mango Agent
        • 使用字体：{self.font_name}
        • 文件格式：PDF
        
        本文档支持中文显示，使用系统字体确保兼容性。
        """
        
        story.append(Paragraph(info_text, self.styles['normal']))
        
        return story

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='中文Markdown转PDF工具')
    parser.add_argument('input', help='输入Markdown文件')
    parser.add_argument('output', help='输出PDF文件')
    parser.add_argument('--title', help='文档标题')
    parser.add_argument('--author', help='文档作者')
    parser.add_argument('--font', help='指定字体名称或路径')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在 - {args.input}")
        sys.exit(1)
    
    # 创建生成器
    generator = ChinesePDFGenerator(font_name=args.font)
    
    # 转换文件
    success = generator.convert_markdown_to_pdf(
        input_file=args.input,
        output_file=args.output,
        title=args.title,
        author=args.author
    )
    
    if success:
        print("=" * 50)
        print("转换完成！")
        print("=" * 50)
        sys.exit(0)
    else:
        print("=" * 50)
        print("转换失败")
        print("=" * 50)
        sys.exit(1)

if __name__ == '__main__':
    main()