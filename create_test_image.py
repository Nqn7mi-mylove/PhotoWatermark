#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试图片用于验证水印功能
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """创建一个简单的测试图片"""
    # 创建一个800x600的彩色图片
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='lightblue')
    
    # 添加一些装饰性内容
    draw = ImageDraw.Draw(image)
    
    # 绘制一些几何图形
    draw.rectangle([100, 100, 300, 200], fill='red', outline='darkred', width=3)
    draw.ellipse([400, 150, 600, 350], fill='green', outline='darkgreen', width=3)
    draw.polygon([(200, 400), (300, 300), (400, 400), (350, 500), (250, 500)], 
                fill='yellow', outline='orange', width=3)
    
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
                font = ImageFont.truetype(font_path, 36)
                break
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2 - 100, 50), "测试图片", font=font, fill='darkblue')
    draw.text((width//2 - 150, height - 80), "Photo Watermark Test", font=font, fill='darkblue')
    
    return image

def main():
    """主函数"""
    # 创建测试图片
    test_image = create_test_image()
    
    # 保存为不同格式
    test_image.save('test_image.jpg', 'JPEG', quality=95)
    test_image.save('test_image.png', 'PNG')
    
    print("✅ 测试图片创建完成:")
    print("  - test_image.jpg")
    print("  - test_image.png")

if __name__ == '__main__':
    main()