#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本：创建示例图片并展示水印功能
"""

import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import subprocess
import sys


def create_demo_images(output_dir):
    """
    创建带有模拟EXIF信息的演示图片
    
    Args:
        output_dir (Path): 输出目录
    """
    # 创建不同类型的演示图片
    images_info = [
        {"name": "landscape.jpg", "size": (1200, 800), "color": (135, 206, 235), "text": "Beautiful Landscape"},
        {"name": "portrait.jpg", "size": (600, 800), "color": (255, 182, 193), "text": "Portrait Photo"},
        {"name": "sunset.jpg", "size": (1000, 600), "color": (255, 140, 0), "text": "Amazing Sunset"},
    ]
    
    created_files = []
    
    for i, info in enumerate(images_info):
        # 创建图片
        image = Image.new('RGB', info["size"], info["color"])
        draw = ImageDraw.Draw(image)
        
        # 绘制装饰性内容
        width, height = info["size"]
        
        # 绘制边框
        draw.rectangle([10, 10, width-10, height-10], outline=(255, 255, 255), width=5)
        
        # 绘制渐变效果（简单模拟）
        for y in range(height//4, 3*height//4, 2):
            alpha = int(255 * (y - height//4) / (height//2))
            color = tuple(max(0, c - alpha//3) for c in info["color"])
            draw.line([(width//4, y), (3*width//4, y)], fill=color, width=1)
        
        # 添加文字
        try:
            # 尝试使用较大的字体
            font = ImageFont.load_default()
            text_bbox = draw.textbbox((0, 0), info["text"], font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = (width - text_width) // 2
            text_y = height // 2 - text_height // 2
            
            # 添加文字背景
            draw.rectangle([text_x-10, text_y-5, text_x+text_width+10, text_y+text_height+5], 
                         fill=(0, 0, 0, 128))
            draw.text((text_x, text_y), info["text"], fill=(255, 255, 255), font=font)
            
        except Exception:
            # 如果字体加载失败，使用简单文字
            draw.text((width//2-50, height//2), info["text"], fill=(255, 255, 255))
        
        # 保存图片
        file_path = output_dir / info["name"]
        image.save(str(file_path), quality=95)
        created_files.append(file_path)
        print(f"创建演示图片: {file_path}")
    
    return created_files


def run_watermark_demo(demo_dir):
    """
    运行水印演示
    
    Args:
        demo_dir (Path): 演示目录
    """
    print("\n" + "="*60)
    print("PhotoWatermark 演示")
    print("="*60)
    
    # 不同的演示配置
    demo_configs = [
        {
            "name": "默认配置 (白色, 右下角, 30px)",
            "args": []
        },
        {
            "name": "红色大字体 (左上角, 40px)",
            "args": ["--font-size", "40", "--color", "red", "--position", "top-left"]
        },
        {
            "name": "绿色居中 (25px)",
            "args": ["--font-size", "25", "--color", "0,255,0", "--position", "center"]
        },
        {
            "name": "黄色底部居中 (35px)",
            "args": ["--font-size", "35", "--color", "yellow", "--position", "bottom-center"]
        }
    ]
    
    for i, config in enumerate(demo_configs, 1):
        print(f"\n--- 演示 {i}: {config['name']} ---")
        
        # 构建命令
        cmd = ["python3", "photo_watermark.py", str(demo_dir)] + config["args"] + ["--verbose"]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 运行命令
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                print("✅ 执行成功")
                # 显示部分输出
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines[-3:]:  # 显示最后几行
                    if line.strip():
                        print(f"   {line}")
            else:
                print("❌ 执行失败")
                print(f"错误信息: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 执行异常: {e}")
        
        # 检查输出目录
        output_dir = demo_dir / f"{demo_dir.name}_watermark"
        if output_dir.exists():
            output_files = list(output_dir.glob("*.jpg"))
            print(f"   生成文件: {len(output_files)} 个")
            
            # 重命名输出目录以避免冲突
            new_name = f"{demo_dir.name}_watermark_demo_{i}"
            new_output_dir = demo_dir / new_name
            output_dir.rename(new_output_dir)
            print(f"   输出目录重命名为: {new_name}")


def main():
    """主演示函数"""
    print("PhotoWatermark 演示程序")
    print("这个演示将创建示例图片并展示不同的水印效果")
    
    # 创建临时演示目录
    demo_base_dir = Path("demo_photos")
    demo_base_dir.mkdir(exist_ok=True)
    
    try:
        # 创建演示图片
        print(f"\n在目录 {demo_base_dir} 中创建演示图片...")
        created_files = create_demo_images(demo_base_dir)
        
        print(f"成功创建 {len(created_files)} 个演示图片")
        
        # 运行水印演示
        run_watermark_demo(demo_base_dir)
        
        print("\n" + "="*60)
        print("演示完成！")
        print(f"请查看 {demo_base_dir} 目录中的结果")
        print("原始图片和各种水印效果的图片都保存在相应的子目录中")
        print("="*60)
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
