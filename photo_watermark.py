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

# 导入模板管理器
try:
    from template_manager import TemplateManager
    TEMPLATE_SUPPORT = True
except ImportError:
    TEMPLATE_SUPPORT = False
    logger.warning("模板管理功能不可用")


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
    
    def __init__(self, font_size=30, font_color=(255, 255, 255), position='bottom-right', 
                 opacity=80, output_format='JPEG', jpeg_quality=95):
        """
        初始化水印处理器
        
        Args:
            font_size (int): 字体大小
            font_color (tuple): 字体颜色 RGB
            position (str): 水印位置
            opacity (int): 透明度 (0-100)
            output_format (str): 输出格式 ('JPEG' 或 'PNG')
            jpeg_quality (int): JPEG质量 (1-100)
        """
        self.font_size = font_size
        self.font_color = font_color
        self.position = position
        self.opacity = opacity
        self.output_format = output_format
        self.jpeg_quality = jpeg_quality
    
    @classmethod
    def from_template(cls, template_name):
        """
        从模板创建水印处理器
        
        Args:
            template_name (str): 模板名称
            
        Returns:
            PhotoWatermark: 水印处理器实例，如果模板不存在返回None
        """
        if not TEMPLATE_SUPPORT:
            logger.error("模板功能不可用")
            return None
        
        manager = TemplateManager()
        config = manager.load_template(template_name)
        
        if config is None:
            return None
        
        return cls(
            font_size=config.get('font_size', 30),
            font_color=config.get('font_color', (255, 255, 255)),
            position=config.get('position', 'bottom-right'),
            opacity=config.get('opacity', 80),
            output_format=config.get('output_format', 'JPEG'),
            jpeg_quality=config.get('jpeg_quality', 95)
        )
        
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
    
    def add_text_watermark(self, image, watermark_text):
        """
        为图片添加文本水印
        
        Args:
            image (PIL.Image): 图片对象
            watermark_text (str): 水印文本
            
        Returns:
            PIL.Image: 添加水印后的图片
        """
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
        
        # 计算透明度
        alpha = int(255 * self.opacity / 100)
        
        # 添加半透明背景
        background_color = (0, 0, 0, alpha // 2)  # 半透明黑色背景
        padding = 10
        draw.rectangle([
            x - padding, y - padding,
            x + text_width + padding, y + text_height + padding
        ], fill=background_color)
        
        # 绘制文本
        draw.text((x, y), watermark_text, font=font, fill=(*self.font_color, alpha))
        
        # 合并图层
        watermarked = Image.alpha_composite(image, watermark_layer)
        return watermarked
    
    def add_image_watermark(self, image, watermark_image_path, scale=0.2):
        """
        为图片添加图片水印
        
        Args:
            image (PIL.Image): 原图片对象
            watermark_image_path (str): 水印图片路径
            scale (float): 水印缩放比例
            
        Returns:
            PIL.Image: 添加水印后的图片
        """
        try:
            with Image.open(watermark_image_path) as watermark_img:
                # 转换为RGBA模式以支持透明度
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                if watermark_img.mode != 'RGBA':
                    watermark_img = watermark_img.convert('RGBA')
                
                # 缩放水印图片
                wm_width = int(watermark_img.width * scale)
                wm_height = int(watermark_img.height * scale)
                watermark_img = watermark_img.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
                
                # 设置透明度
                alpha = int(255 * self.opacity / 100)
                watermark_img.putalpha(alpha)
                
                # 计算位置
                x, y = self.calculate_text_position(image.size, (wm_width, wm_height), self.position)
                
                # 粘贴水印
                image.paste(watermark_img, (x, y), watermark_img)
                
        except Exception as e:
            logger.error(f"添加图片水印失败: {e}")
        
        return image
    
    def add_watermark(self, image_path, output_path, watermark_text=None, watermark_image_path=None):
        """
        为图片添加水印
        
        Args:
            image_path (str): 输入图片路径
            output_path (str): 输出图片路径
            watermark_text (str): 水印文本
            watermark_image_path (str): 水印图片路径
            
        Returns:
            bool: 是否成功
        """
        try:
            with Image.open(image_path) as image:
                watermarked = image.copy()
                
                # 添加文本水印
                if watermark_text:
                    watermarked = self.add_text_watermark(watermarked, watermark_text)
                
                # 添加图片水印
                if watermark_image_path and os.path.exists(watermark_image_path):
                    watermarked = self.add_image_watermark(watermarked, watermark_image_path)
                
                # 保存图片
                self.save_image(watermarked, output_path)
                logger.info(f"水印添加成功: {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"添加水印失败 {image_path}: {e}")
            return False
    
    def save_image(self, image, output_path):
        """
        保存图片
        
        Args:
            image (PIL.Image): 图片对象
            output_path (str): 输出路径
        """
        # 根据输出格式保存
        if self.output_format.upper() == 'PNG':
            # PNG格式保持透明度
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            image.save(output_path, 'PNG')
        else:
            # JPEG格式转换为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(output_path, 'JPEG', quality=self.jpeg_quality)
    
    def process_image(self, input_path, output_path, custom_text=None, watermark_image_path=None):
        """
        处理单个图片
        
        Args:
            input_path (str): 输入图片路径
            output_path (str): 输出图片路径
            custom_text (str): 自定义水印文本
            watermark_image_path (str): 水印图片路径
            
        Returns:
            bool: 是否成功
        """
        if not os.path.exists(input_path):
            logger.error(f"输入文件不存在: {input_path}")
            return False
        
        # 检查文件格式
        file_ext = Path(input_path).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            logger.warning(f"不支持的文件格式: {file_ext}")
            return False
        
        # 确定水印文本
        if custom_text:
            watermark_text = custom_text
        else:
            # 尝试从EXIF获取日期
            exif_date = self.get_exif_datetime(input_path)
            if exif_date:
                watermark_text = exif_date
            else:
                # 使用文件修改时间
                mod_time = datetime.fromtimestamp(os.path.getmtime(input_path))
                watermark_text = mod_time.strftime("%Y-%m-%d")
        
        return self.add_watermark(input_path, output_path, watermark_text, watermark_image_path)

    def process_directory(self, input_dir, output_dir=None, custom_text=None, watermark_image_path=None):
        """
        批量处理目录中的图片
        
        Args:
            input_dir (str): 输入目录路径
            output_dir (str): 输出目录路径，如果为None则在输入目录下创建_watermark子目录
            custom_text (str): 自定义水印文本
            watermark_image_path (str): 水印图片路径
            
        Returns:
            tuple: (成功数量, 总数量)
        """
        input_path = Path(input_dir)
        
        if not input_path.exists() or not input_path.is_dir():
            logger.error(f"输入目录不存在或不是目录: {input_dir}")
            return 0, 0
        
        # 确定输出目录
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = input_path / f"{input_path.name}_watermark"
        
        # 创建输出目录
        output_path.mkdir(exist_ok=True)
        logger.info(f"输出目录: {output_path}")
        
        # 查找所有支持的图片文件
        image_files = []
        for ext in self.SUPPORTED_FORMATS:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not image_files:
            logger.warning(f"在目录 {input_dir} 中未找到支持的图片文件")
            return 0, 0
        
        logger.info(f"找到 {len(image_files)} 个图片文件")
        
        success_count = 0
        for image_file in image_files:
            try:
                # 生成输出文件名
                if self.output_format.upper() == 'PNG':
                    output_file = output_path / f"{image_file.stem}.png"
                else:
                    output_file = output_path / f"{image_file.stem}.jpg"
                
                # 处理图片
                if self.process_image(str(image_file), str(output_file), custom_text, watermark_image_path):
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"处理文件失败 {image_file}: {e}")
        
        logger.info(f"处理完成: {success_count}/{len(image_files)} 个文件成功")
        return success_count, len(image_files)


def parse_color(color_str):
    """
    解析颜色字符串
    
    Args:
        color_str (str): 颜色字符串，可以是颜色名称或RGB格式
        
    Returns:
        tuple: RGB颜色值
    """
    # 预定义颜色
    color_map = {
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
    
    # 检查是否为预定义颜色
    if color_str.lower() in color_map:
        return color_map[color_str.lower()]
    
    # 尝试解析RGB格式 "R,G,B"
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
  %(prog)s input.jpg -o output.jpg --text "My Watermark"
  %(prog)s input_dir/ --output-dir output_dir/ --format PNG
  %(prog)s input.jpg -o output.jpg --template "默认水印"

支持的位置:
  top-left, top-center, top-right
  center-left, center, center-right  
  bottom-left, bottom-center, bottom-right

支持的颜色:
  颜色名称: white, black, red, green, blue, yellow, cyan, magenta, gray
  RGB格式: "255,255,255" (用逗号分隔的RGB值)
        """
    )
    
    parser.add_argument('input', help='输入图片文件或目录路径')
    parser.add_argument('-o', '--output', help='输出文件或目录路径')
    parser.add_argument('--output-dir', help='输出目录路径（用于批量处理）')
    parser.add_argument('--text', help='自定义水印文本（覆盖EXIF日期）')
    parser.add_argument('--image-watermark', help='水印图片路径')
    parser.add_argument('--template', help='使用保存的水印模板')
    parser.add_argument('--font-size', '-s', type=int, default=30, help='字体大小 (默认: 30)')
    parser.add_argument('--color', '-c', default='white', help='字体颜色，支持颜色名称或RGB格式 "R,G,B" (默认: white)')
    parser.add_argument('--position', '-p', 
                       choices=['top-left', 'top-center', 'top-right',
                               'center-left', 'center', 'center-right',
                               'bottom-left', 'bottom-center', 'bottom-right'],
                       default='bottom-right', help='水印位置 (默认: bottom-right)')
    parser.add_argument('--opacity', type=int, default=80, help='透明度 0-100 (默认: 80)')
    parser.add_argument('--format', choices=['JPEG', 'PNG'], default='JPEG', help='输出格式 (默认: JPEG)')
    parser.add_argument('--quality', type=int, default=95, help='JPEG质量 1-100 (默认: 95)')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')
    
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
        position=args.position,
        opacity=args.opacity,
        output_format=args.format,
        jpeg_quality=args.quality
    )
    
    input_path = Path(args.input)
    
    try:
        if input_path.is_file():
            # 处理单个文件
            if args.output:
                output_path = args.output
            else:
                # 生成默认输出文件名
                if args.format == 'PNG':
                    output_path = input_path.with_suffix('.png').with_name(f"{input_path.stem}_watermark.png")
                else:
                    output_path = input_path.with_suffix('.jpg').with_name(f"{input_path.stem}_watermark.jpg")
            
            success = watermark.process_image(
                str(input_path), 
                str(output_path), 
                args.text,
                args.image_watermark
            )
            
            if success:
                print(f"✅ 处理完成: {output_path}")
            else:
                print("❌ 处理失败")
                sys.exit(1)
                
        elif input_path.is_dir():
            # 处理目录
            output_dir = args.output_dir or args.output
            success_count, total_count = watermark.process_directory(
                str(input_path), 
                output_dir,
                args.text,
                args.image_watermark
            )
            
            print(f"✅ 批量处理完成: {success_count}/{total_count} 个文件成功")
            
            if success_count == 0:
                sys.exit(1)
        else:
            print(f"❌ 输入路径不存在: {args.input}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
