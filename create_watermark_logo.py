#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建水印logo图片用于测试图片水印功能
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_watermark_logo():
    """创建一个简单的水印logo"""
    # 创建一个200x80的透明图片
    width, height = 200, 80
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    draw = ImageDraw.Draw(image)
    
    # 绘制一个简单的logo背景
    draw.rounded_rectangle([10, 10, width-10, height-10], 
                          radius=15, fill=(255, 255, 255, 180), 
                          outline=(0, 0, 0, 200), width=2)
    
    # 添加文本
    try:
        # 尝试使用系统字体
        font_paths = [
            '/System/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial.ttf'
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 24)
                break
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # 绘制logo文本
    text = "LOGO"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, font=font, fill=(50, 50, 50, 255))
    
    return image

def main():
    """主函数"""
    # 创建水印logo
    logo = create_watermark_logo()
    
    # 保存为PNG格式（保持透明度）
    logo.save('watermark_logo.png', 'PNG')
    
    print("✅ 水印logo创建完成:")
    print("  - watermark_logo.png")

if __name__ == '__main__':
    main()