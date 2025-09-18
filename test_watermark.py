#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证水印程序功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from photo_watermark import PhotoWatermark, parse_color


def create_test_image(output_path, size=(800, 600), color=(100, 150, 200)):
    """
    创建测试图片
    
    Args:
        output_path (str): 输出路径
        size (tuple): 图片尺寸
        color (tuple): 背景颜色
    """
    image = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(image)
    
    # 绘制一些简单的图形作为测试内容
    draw.rectangle([50, 50, size[0]-50, size[1]-50], outline=(255, 255, 255), width=3)
    draw.ellipse([size[0]//4, size[1]//4, 3*size[0]//4, 3*size[1]//4], 
                outline=(255, 255, 0), width=2)
    
    # 添加一些文字
    draw.text((size[0]//2-50, size[1]//2), "TEST IMAGE", fill=(255, 255, 255))
    
    image.save(output_path, quality=95)
    print(f"创建测试图片: {output_path}")


def test_color_parsing():
    """测试颜色解析功能"""
    print("\n=== 测试颜色解析功能 ===")
    
    test_cases = [
        ("white", (255, 255, 255)),
        ("black", (0, 0, 0)),
        ("red", (255, 0, 0)),
        ("255,0,0", (255, 0, 0)),
        ("128,128,128", (128, 128, 128)),
        ("invalid_color", (255, 255, 255)),  # 应该返回默认白色
    ]
    
    for color_input, expected in test_cases:
        result = parse_color(color_input)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{color_input}' -> {result} (期望: {expected})")


def test_position_calculation():
    """测试位置计算功能"""
    print("\n=== 测试位置计算功能 ===")
    
    watermark = PhotoWatermark()
    image_size = (800, 600)
    text_size = (100, 30)
    
    positions = [
        'top-left', 'top-center', 'top-right',
        'center-left', 'center', 'center-right',
        'bottom-left', 'bottom-center', 'bottom-right'
    ]
    
    for position in positions:
        x, y = watermark.calculate_text_position(image_size, text_size, position)
        print(f"位置 '{position}': ({x}, {y})")


def test_watermark_functionality():
    """测试水印功能"""
    print("\n=== 测试水印功能 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建测试图片
        test_images = []
        for i in range(3):
            img_path = temp_path / f"test_image_{i+1}.jpg"
            create_test_image(str(img_path), color=(100+i*50, 150-i*30, 200+i*20))
            test_images.append(img_path)
        
        # 测试不同的水印配置
        configs = [
            {"font_size": 30, "font_color": (255, 255, 255), "position": "bottom-right"},
            {"font_size": 40, "font_color": (255, 0, 0), "position": "top-left"},
            {"font_size": 25, "font_color": (0, 255, 0), "position": "center"},
        ]
        
        for i, config in enumerate(configs):
            print(f"\n--- 测试配置 {i+1}: {config} ---")
            
            watermark = PhotoWatermark(**config)
            
            # 处理目录
            success_count, total_count = watermark.process_directory(str(temp_path))
            
            status = "✅" if success_count == total_count else "❌"
            print(f"{status} 处理结果: {success_count}/{total_count}")
            
            # 检查输出目录
            output_dir = temp_path / f"{temp_path.name}_watermark"
            if output_dir.exists():
                output_files = list(output_dir.glob("*.jpg"))
                print(f"输出文件数量: {len(output_files)}")
                
                # 清理输出目录以便下次测试
                shutil.rmtree(output_dir)
            else:
                print("❌ 输出目录未创建")


def test_exif_handling():
    """测试EXIF处理功能"""
    print("\n=== 测试EXIF处理功能 ===")
    
    watermark = PhotoWatermark()
    
    # 创建临时测试图片
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        create_test_image(temp_file.name)
        
        # 测试EXIF时间提取（这个图片没有EXIF信息，应该返回None）
        date_str = watermark.get_exif_datetime(temp_file.name)
        
        if date_str is None:
            print("✅ 正确处理无EXIF信息的图片")
        else:
            print(f"❌ 意外获得日期: {date_str}")
        
        # 清理临时文件
        os.unlink(temp_file.name)


def main():
    """主测试函数"""
    print("PhotoWatermark 功能测试")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_color_parsing()
        test_position_calculation()
        test_exif_handling()
        test_watermark_functionality()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
