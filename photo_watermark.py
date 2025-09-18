#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark Tool
为图片添加基于EXIF拍摄时间的水印
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PhotoWatermark:
    """图片水印处理类"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    
    # 水印位置映射
    POSITION_MAP = {
        'top-left': 'top_left',
        'top-center': 'top_center', 
        'top-right': 'top_right',
        'center-left': 'center_left',
        'center': 'center',
        'center-right': 'center_right',
        'bottom-left': 'bottom_left',
        'bottom-center': 'bottom_center',
        'bottom-right': 'bottom_right'
    }
    
    def __init__(self, font_size=30, font_color=(255, 255, 255), position='bottom-right'):
        """
        初始化水印处理器
        
        Args:
            font_size (int): 字体大小
            font_color (tuple): 字体颜色 RGB
            position (str): 水印位置
        """
        self.font_size = font_size
        self.font_color = font_color
        self.position = position
        
    def get_exif_datetime(self, image_path):
        """
        从图片EXIF信息中提取拍摄时间
        
        Args:
            image_path (str): 图片路径
            
        Returns:
            str: 格式化的日期字符串 (YYYY-MM-DD) 或 None
        """
        try:
            with Image.open(image_path) as image:
                exif_data = image._getexif()
                
                if exif_data is not None:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        # 查找拍摄时间相关的标签
                        if tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                            try:
                                # 解析时间格式: "YYYY:MM:DD HH:MM:SS"
                                dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                                return dt.strftime("%Y-%m-%d")
                            except ValueError:
                                logger.warning(f"无法解析时间格式: {value}")
                                continue
                                
                logger.warning(f"未找到EXIF时间信息: {image_path}")
                return None
                
        except Exception as e:
            logger.error(f"读取EXIF信息失败 {image_path}: {e}")
            return None
    
    def calculate_text_position(self, image_size, text_size, position):
        """
        计算文本在图片上的位置
        
        Args:
            image_size (tuple): 图片尺寸 (width, height)
            text_size (tuple): 文本尺寸 (width, height)
            position (str): 位置标识
            
        Returns:
            tuple: 文本位置坐标 (x, y)
        """
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        # 边距
        margin = 20
        
        position_coords = {
            'top_left': (margin, margin),
            'top_center': ((img_width - text_width) // 2, margin),
            'top_right': (img_width - text_width - margin, margin),
            'center_left': (margin, (img_height - text_height) // 2),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
            'center_right': (img_width - text_width - margin, (img_height - text_height) // 2),
            'bottom_left': (margin, img_height - text_height - margin),
            'bottom_center': ((img_width - text_width) // 2, img_height - text_height - margin),
            'bottom_right': (img_width - text_width - margin, img_height - text_height - margin)
        }
        
        return position_coords.get(self.POSITION_MAP.get(position, 'bottom_right'), 
                                 position_coords['bottom_right'])
    
    def add_watermark(self, image_path, output_path, watermark_text):
        """
        为图片添加水印
        
        Args:
            image_path (str): 输入图片路径
            output_path (str): 输出图片路径
            watermark_text (str): 水印文本
            
        Returns:
            bool: 是否成功
        """
        try:
            with Image.open(image_path) as image:
                # 转换为RGBA模式以支持透明度
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # 创建透明图层用于绘制水印
                watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(watermark_layer)
                
                # 尝试加载字体
                try:
                    # 在macOS上尝试使用系统字体
                    font_paths = [
                        '/System/Library/Fonts/Arial.ttf',
                        '/System/Library/Fonts/Helvetica.ttc',
                        '/Library/Fonts/Arial.ttf'
                    ]
                    
                    font = None
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            font = ImageFont.truetype(font_path, self.font_size)
                            break
                    
                    if font is None:
                        font = ImageFont.load_default()
                        logger.warning("使用默认字体")
                        
                except Exception as e:
                    font = ImageFont.load_default()
                    logger.warning(f"加载字体失败，使用默认字体: {e}")
                
                # 获取文本尺寸
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算文本位置
                x, y = self.calculate_text_position(
                    image.size, 
                    (text_width, text_height), 
                    self.position
                )
                
                # 添加半透明背景
                background_color = (0, 0, 0, 128)  # 半透明黑色背景
                padding = 10
                draw.rectangle([
                    x - padding, y - padding,
                    x + text_width + padding, y + text_height + padding
                ], fill=background_color)
                
                # 绘制文本
                draw.text((x, y), watermark_text, font=font, fill=(*self.font_color, 255))
                
                # 合并图层
                watermarked = Image.alpha_composite(image, watermark_layer)
                
                # 如果原图不是RGBA，转换回原格式
                if Image.open(image_path).mode != 'RGBA':
                    watermarked = watermarked.convert('RGB')
                
                # 保存图片
                watermarked.save(output_path, quality=95)
                logger.info(f"水印添加成功: {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"添加水印失败 {image_path}: {e}")
            return False
    
    def process_directory(self, input_dir):
        """
        处理目录中的所有图片
        
        Args:
            input_dir (str): 输入目录路径
            
        Returns:
            tuple: (成功数量, 总数量)
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            logger.error(f"目录不存在: {input_dir}")
            return 0, 0
        
        if not input_path.is_dir():
            logger.error(f"路径不是目录: {input_dir}")
            return 0, 0
        
        # 创建输出目录
        output_dir = input_path / f"{input_path.name}_watermark"
        output_dir.mkdir(exist_ok=True)
        
        # 查找所有图片文件
        image_files = []
        for ext in self.SUPPORTED_FORMATS:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not image_files:
            logger.warning(f"目录中未找到支持的图片文件: {input_dir}")
            return 0, 0
        
        logger.info(f"找到 {len(image_files)} 个图片文件")
        
        success_count = 0
        
        for image_file in image_files:
            logger.info(f"处理图片: {image_file.name}")
            
            # 获取EXIF时间信息
            date_str = self.get_exif_datetime(str(image_file))
            
            if date_str is None:
                # 如果没有EXIF时间信息，使用文件修改时间
                mtime = datetime.fromtimestamp(image_file.stat().st_mtime)
                date_str = mtime.strftime("%Y-%m-%d")
                logger.info(f"使用文件修改时间: {date_str}")
            else:
                logger.info(f"使用EXIF拍摄时间: {date_str}")
            
            # 生成输出文件路径
            output_file = output_dir / image_file.name
            
            # 添加水印
            if self.add_watermark(str(image_file), str(output_file), date_str):
                success_count += 1
        
        logger.info(f"处理完成: {success_count}/{len(image_files)} 个文件成功")
        return success_count, len(image_files)


def parse_color(color_str):
    """
    解析颜色字符串
    
    Args:
        color_str (str): 颜色字符串，支持格式：
                        - "255,255,255" (RGB)
                        - "white", "black", "red" 等颜色名称
    
    Returns:
        tuple: RGB颜色元组
    """
    # 预定义颜色
    color_names = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128)
    }
    
    color_str = color_str.lower().strip()
    
    # 检查是否是颜色名称
    if color_str in color_names:
        return color_names[color_str]
    
    # 尝试解析RGB格式
    try:
        rgb_values = [int(x.strip()) for x in color_str.split(',')]
        if len(rgb_values) == 3 and all(0 <= x <= 255 for x in rgb_values):
            return tuple(rgb_values)
    except ValueError:
        pass
    
    # 默认返回白色
    logger.warning(f"无法解析颜色 '{color_str}'，使用默认白色")
    return (255, 255, 255)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='为图片添加基于EXIF拍摄时间的水印',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s /path/to/photos
  %(prog)s /path/to/photos --font-size 40 --color red --position top-left
  %(prog)s /path/to/photos --font-size 25 --color "255,0,0" --position center

支持的位置:
  top-left, top-center, top-right
  center-left, center, center-right  
  bottom-left, bottom-center, bottom-right

支持的颜色:
  颜色名称: white, black, red, green, blue, yellow, cyan, magenta, gray
  RGB格式: "255,255,255" (用逗号分隔的RGB值)
        """
    )
    
    parser.add_argument(
        'directory',
        help='包含图片的目录路径'
    )
    
    parser.add_argument(
        '--font-size', '-s',
        type=int,
        default=30,
        help='字体大小 (默认: 30)'
    )
    
    parser.add_argument(
        '--color', '-c',
        type=str,
        default='white',
        help='字体颜色，支持颜色名称或RGB格式 "R,G,B" (默认: white)'
    )
    
    parser.add_argument(
        '--position', '-p',
        type=str,
        default='bottom-right',
        choices=list(PhotoWatermark.POSITION_MAP.keys()),
        help='水印位置 (默认: bottom-right)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 解析颜色
    font_color = parse_color(args.color)
    
    # 创建水印处理器
    watermark = PhotoWatermark(
        font_size=args.font_size,
        font_color=font_color,
        position=args.position
    )
    
    # 处理图片
    try:
        success_count, total_count = watermark.process_directory(args.directory)
        
        if total_count == 0:
            print("未找到可处理的图片文件")
            sys.exit(1)
        elif success_count == total_count:
            print(f"✅ 所有 {total_count} 个图片文件处理成功")
            sys.exit(0)
        else:
            print(f"⚠️  {success_count}/{total_count} 个图片文件处理成功")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
