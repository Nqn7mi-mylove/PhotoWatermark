#!/usr/bin/env python3
"""
Photo Watermark Tool - 主入口文件
版本: 4.0
支持GUI和命令行两种模式
"""

import sys
import argparse

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Photo Watermark Tool')
    parser.add_argument('input', nargs='?', help='输入图片文件或目录')
    parser.add_argument('-o', '--output', help='输出文件或目录')
    parser.add_argument('--text', default='Sample Watermark', help='水印文本')
    parser.add_argument('--font-size', type=int, default=30, help='字体大小')
    parser.add_argument('--color', default='white', help='字体颜色')
    parser.add_argument('--position', default='bottom-right', help='水印位置')
    parser.add_argument('--opacity', type=int, default=80, help='透明度 (0-100)')
    parser.add_argument('--gui', action='store_true', help='强制启动GUI模式')
    
    args = parser.parse_args()
    
    # 如果没有参数或指定了GUI模式，启动GUI
    if not args.input or args.gui:
        print("启动现代化图形界面...")
        try:
            # 导入现代GUI
            from watermark_gui_modern import ModernPhotoWatermarkGUI
            app = ModernPhotoWatermarkGUI()
            app.run()
        except ImportError as e:
            print(f"现代GUI导入失败: {e}")
            print("请确保所有依赖已正确安装")
            return 1
        except Exception as e:
            print(f"GUI启动失败: {e}")
            return 1
    else:
        # 命令行模式
        print("启动命令行模式...")
        try:
            from photo_watermark import PhotoWatermark, parse_color
            
            # 创建水印处理器
            watermark = PhotoWatermark(
                font_size=args.font_size,
                font_color=parse_color(args.color),
                position=args.position,
                opacity=args.opacity
            )
            
            # 处理图片
            if args.output:
                watermark.process_image(args.input, args.output)
            else:
                watermark.process_directory(args.input)
                
            print("处理完成!")
            
        except ImportError as e:
            print(f"导入错误: {e}")
            print("请确保所有依赖已正确安装")
            return 1
        except Exception as e:
            print(f"处理错误: {e}")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())