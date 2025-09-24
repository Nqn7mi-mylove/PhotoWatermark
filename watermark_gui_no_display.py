#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhotoWatermark - 命令行交互式界面
解决macOS GUI兼容性问题的替代方案
"""

import os
import sys
from pathlib import Path
import json
from photo_watermark import PhotoWatermark, parse_color
from template_manager import TemplateManager

class InteractiveWatermarkTool:
    def __init__(self):
        self.template_manager = TemplateManager()
        
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "="*50)
        print("📸 PhotoWatermark - 交互式水印工具")
        print("="*50)
        print("1. 添加文本水印")
        print("2. 添加图片水印")
        print("3. 使用模板")
        print("4. 管理模板")
        print("5. 批量处理")
        print("0. 退出")
        print("-"*50)
        
    def get_input_file(self):
        """获取输入文件"""
        while True:
            file_path = input("请输入图片文件路径: ").strip()
            if not file_path:
                print("❌ 文件路径不能为空")
                continue
            
            # 处理相对路径
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
                
            if os.path.exists(file_path):
                return file_path
            else:
                print(f"❌ 文件不存在: {file_path}")
                
    def get_output_file(self, input_file):
        """获取输出文件"""
        default_output = self.generate_default_output(input_file)
        output = input(f"输出文件路径 (默认: {default_output}): ").strip()
        return output if output else default_output
        
    def generate_default_output(self, input_file):
        """生成默认输出文件名"""
        path = Path(input_file)
        return str(path.parent / f"{path.stem}_watermarked{path.suffix}")
        
    def add_text_watermark(self):
        """添加文本水印"""
        print("\n📝 添加文本水印")
        print("-"*30)
        
        input_file = self.get_input_file()
        output_file = self.get_output_file(input_file)
        
        text = input("水印文字: ").strip()
        if not text:
            print("❌ 水印文字不能为空")
            return
            
        # 可选参数
        font_size = input("字体大小 (默认: 30): ").strip()
        font_size = int(font_size) if font_size.isdigit() else 30
        
        color = input("颜色 (默认: white): ").strip() or "white"
        
        print("位置选项:")
        print("1. top-left    2. top-center    3. top-right")
        print("4. center-left 5. center        6. center-right")
        print("7. bottom-left 8. bottom-center 9. bottom-right")
        
        position_map = {
            '1': 'top-left', '2': 'top-center', '3': 'top-right',
            '4': 'center-left', '5': 'center', '6': 'center-right',
            '7': 'bottom-left', '8': 'bottom-center', '9': 'bottom-right'
        }
        
        pos_choice = input("选择位置 (默认: 9-bottom-right): ").strip()
        position = position_map.get(pos_choice, 'bottom-right')
        
        opacity = input("透明度 0-100 (默认: 80): ").strip()
        opacity = int(opacity) if opacity.isdigit() and 0 <= int(opacity) <= 100 else 80
        
        format_choice = input("输出格式 JPEG/PNG (默认: JPEG): ").strip().upper()
        output_format = format_choice if format_choice in ['JPEG', 'PNG'] else 'JPEG'
        
        try:
            # 解析颜色
            font_color = parse_color(color)
            
            # 创建水印处理器
            watermark = PhotoWatermark(
                font_size=font_size,
                font_color=font_color,
                position=position,
                opacity=opacity,
                output_format=output_format
            )
            
            result = watermark.add_watermark(
                image_path=input_file,
                output_path=output_file,
                watermark_text=text
            )
            
            if result:
                print(f"✅ 水印添加成功! 输出文件: {output_file}")
            else:
                print("❌ 水印添加失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            
    def add_image_watermark(self):
        """添加图片水印"""
        print("\n🖼️  添加图片水印")
        print("-"*30)
        
        input_file = self.get_input_file()
        
        print("请选择水印图片:")
        watermark_file = self.get_input_file()
        
        output_file = self.get_output_file(input_file)
        
        # 位置选择
        print("位置选项:")
        print("1. top-left    2. top-center    3. top-right")
        print("4. center-left 5. center        6. center-right")
        print("7. bottom-left 8. bottom-center 9. bottom-right")
        
        position_map = {
            '1': 'top-left', '2': 'top-center', '3': 'top-right',
            '4': 'center-left', '5': 'center', '6': 'center-right',
            '7': 'bottom-left', '8': 'bottom-center', '9': 'bottom-right'
        }
        
        pos_choice = input("选择位置 (默认: 9-bottom-right): ").strip()
        position = position_map.get(pos_choice, 'bottom-right')
        
        opacity = input("透明度 0-100 (默认: 80): ").strip()
        opacity = int(opacity) if opacity.isdigit() and 0 <= int(opacity) <= 100 else 80
        
        format_choice = input("输出格式 JPEG/PNG (默认: JPEG): ").strip().upper()
        output_format = format_choice if format_choice in ['JPEG', 'PNG'] else 'JPEG'
        
        try:
            # 解析颜色 (虽然图片水印不需要，但保持一致性)
            font_color = parse_color("white")
            
            # 创建水印处理器
            watermark = PhotoWatermark(
                position=position,
                opacity=opacity,
                output_format=output_format
            )
            
            result = watermark.add_watermark(
                image_path=input_file,
                output_path=output_file,
                watermark_image_path=watermark_file
            )
            
            if result:
                print(f"✅ 图片水印添加成功! 输出文件: {output_file}")
            else:
                print("❌ 图片水印添加失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            
    def use_template(self):
        """使用模板"""
        print("\n📋 使用模板")
        print("-"*30)
        
        templates = self.template_manager.list_templates()
        if not templates:
            print("❌ 没有可用的模板")
            return
            
        print("可用模板:")
        for i, (name, config) in enumerate(templates.items(), 1):
            print(f"{i}. {name}")
            print(f"   字体: {config.get('font_size', 30)}px, "
                  f"颜色: {config.get('color', 'white')}, "
                  f"位置: {config.get('position', 'bottom-right')}")
            
        choice = input("选择模板编号: ").strip()
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(templates):
            print("❌ 无效的选择")
            return
            
        template_name = list(templates.keys())[int(choice) - 1]
        
        input_file = self.get_input_file()
        output_file = self.get_output_file(input_file)
        
        try:
            # 使用模板创建水印处理器
            watermark = PhotoWatermark.from_template(template_name)
            if not watermark:
                print(f"❌ 模板 '{template_name}' 不存在或加载失败")
                return
                
            result = watermark.process_image(
                input_path=input_file,
                output_path=output_file
            )
            
            if result:
                print(f"✅ 模板应用成功! 输出文件: {output_file}")
            else:
                print("❌ 模板应用失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            
    def manage_templates(self):
        """管理模板"""
        print("\n⚙️  模板管理")
        print("-"*30)
        print("1. 查看所有模板")
        print("2. 保存新模板")
        print("3. 删除模板")
        print("0. 返回主菜单")
        
        choice = input("请选择: ").strip()
        
        if choice == '1':
            self.list_templates()
        elif choice == '2':
            self.save_template()
        elif choice == '3':
            self.delete_template()
        elif choice == '0':
            return
        else:
            print("❌ 无效的选择")
            
    def list_templates(self):
        """列出所有模板"""
        templates = self.template_manager.list_templates()
        if not templates:
            print("📝 没有保存的模板")
            return
            
        print("\n📋 已保存的模板:")
        for name, config in templates.items():
            print(f"\n🏷️  {name}")
            for key, value in config.items():
                print(f"   {key}: {value}")
                
    def save_template(self):
        """保存新模板"""
        print("\n💾 保存新模板")
        
        name = input("模板名称: ").strip()
        if not name:
            print("❌ 模板名称不能为空")
            return
            
        font_size = input("字体大小 (默认: 30): ").strip()
        font_size = int(font_size) if font_size.isdigit() else 30
        
        color = input("颜色 (默认: white): ").strip() or "white"
        
        print("位置选项:")
        print("1. top-left    2. top-center    3. top-right")
        print("4. center-left 5. center        6. center-right")
        print("7. bottom-left 8. bottom-center 9. bottom-right")
        
        position_map = {
            '1': 'top-left', '2': 'top-center', '3': 'top-right',
            '4': 'center-left', '5': 'center', '6': 'center-right',
            '7': 'bottom-left', '8': 'bottom-center', '9': 'bottom-right'
        }
        
        pos_choice = input("选择位置 (默认: 9-bottom-right): ").strip()
        position = position_map.get(pos_choice, 'bottom-right')
        
        opacity = input("透明度 0-100 (默认: 80): ").strip()
        opacity = int(opacity) if opacity.isdigit() and 0 <= int(opacity) <= 100 else 80
        
        format_choice = input("输出格式 JPEG/PNG (默认: JPEG): ").strip().upper()
        output_format = format_choice if format_choice in ['JPEG', 'PNG'] else 'JPEG'
        
        try:
            self.template_manager.save_template(
                name=name,
                font_size=font_size,
                color=color,
                position=position,
                opacity=opacity,
                output_format=output_format
            )
            print(f"✅ 模板 '{name}' 保存成功!")
            
        except Exception as e:
            print(f"❌ 保存模板失败: {e}")
            
    def delete_template(self):
        """删除模板"""
        templates = self.template_manager.list_templates()
        if not templates:
            print("❌ 没有可删除的模板")
            return
            
        print("\n🗑️  删除模板")
        print("可用模板:")
        for i, name in enumerate(templates.keys(), 1):
            print(f"{i}. {name}")
            
        choice = input("选择要删除的模板编号: ").strip()
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(templates):
            print("❌ 无效的选择")
            return
            
        template_name = list(templates.keys())[int(choice) - 1]
        
        confirm = input(f"确认删除模板 '{template_name}'? (y/N): ").strip().lower()
        if confirm == 'y':
            try:
                self.template_manager.delete_template(template_name)
                print(f"✅ 模板 '{template_name}' 删除成功!")
            except Exception as e:
                print(f"❌ 删除模板失败: {e}")
        else:
            print("❌ 取消删除")
            
    def batch_process(self):
        """批量处理"""
        print("\n📁 批量处理")
        print("-"*30)
        
        input_dir = input("输入目录路径: ").strip()
        if not os.path.isdir(input_dir):
            print("❌ 目录不存在")
            return
            
        output_dir = input("输出目录路径: ").strip()
        if not output_dir:
            output_dir = os.path.join(input_dir, "watermarked")
            
        text = input("水印文字: ").strip()
        if not text:
            print("❌ 水印文字不能为空")
            return
            
        try:
            # 使用命令行工具进行批量处理
            import subprocess
            cmd = [
                sys.executable, "photo_watermark.py",
                input_dir,
                "--output-dir", output_dir,
                "--text", text,
                "--verbose"
            ]
            
            print("🔄 开始批量处理...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 批量处理完成!")
                print(result.stdout)
            else:
                print("❌ 批量处理失败:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            
    def run(self):
        """运行主程序"""
        print("🎉 欢迎使用 PhotoWatermark 交互式工具!")
        print("这是GUI版本的替代方案，解决macOS兼容性问题。")
        
        while True:
            try:
                self.show_menu()
                choice = input("请选择操作 (0-5): ").strip()
                
                if choice == '0':
                    print("👋 感谢使用 PhotoWatermark!")
                    break
                elif choice == '1':
                    self.add_text_watermark()
                elif choice == '2':
                    self.add_image_watermark()
                elif choice == '3':
                    self.use_template()
                elif choice == '4':
                    self.manage_templates()
                elif choice == '5':
                    self.batch_process()
                else:
                    print("❌ 无效的选择，请输入 0-5")
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序已退出")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    app = InteractiveWatermarkTool()
    app.run()