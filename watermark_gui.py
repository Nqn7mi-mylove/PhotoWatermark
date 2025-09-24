#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark GUI Application
图片水印工具的图形用户界面
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from pathlib import Path
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFont
from typing import List, Dict, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 尝试导入customtkinter，如果失败则使用标准tkinter
try:
    import customtkinter as ctk
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    USE_CUSTOM_TKINTER = True
except ImportError:
    USE_CUSTOM_TKINTER = False
    logger.warning("CustomTkinter not available, using standard tkinter")


class WatermarkConfig:
    """水印配置类"""
    
    def __init__(self):
        self.text = "Sample Watermark"
        self.font_family = "Arial"
        self.font_size = 30
        self.font_bold = False
        self.font_italic = False
        self.color = (255, 255, 255)  # RGB
        self.opacity = 80  # 0-100
        self.position = "bottom-right"
        self.rotation = 0  # 角度
        self.shadow = False
        self.stroke = False
        self.stroke_width = 2
        self.stroke_color = (0, 0, 0)
        
        # 图片水印相关
        self.image_path = ""
        self.image_scale = 1.0
        self.image_opacity = 80
        
        # 位置偏移
        self.offset_x = 20
        self.offset_y = 20
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'text': self.text,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_bold': self.font_bold,
            'font_italic': self.font_italic,
            'color': self.color,
            'opacity': self.opacity,
            'position': self.position,
            'rotation': self.rotation,
            'shadow': self.shadow,
            'stroke': self.stroke,
            'stroke_width': self.stroke_width,
            'stroke_color': self.stroke_color,
            'image_path': self.image_path,
            'image_scale': self.image_scale,
            'image_opacity': self.image_opacity,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y
        }
    
    def from_dict(self, data: Dict):
        """从字典加载"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class ImageItem:
    """图片项目类"""
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.name = self.path.name
        self.size = None
        self.thumbnail = None
        self.processed = False
        
        try:
            with Image.open(self.path) as img:
                self.size = img.size
                # 创建缩略图
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                self.thumbnail = ImageTk.PhotoImage(img)
        except Exception as e:
            logger.error(f"Failed to load image {self.path}: {e}")
            self.thumbnail = None


class WatermarkPreview:
    """水印预览类"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.image = None
        self.photo = None
        self.watermark_items = []
        
    def update_preview(self, image_item: ImageItem, config: WatermarkConfig):
        """更新预览"""
        if not image_item or not image_item.path.exists():
            return
            
        try:
            # 加载原图
            with Image.open(image_item.path) as img:
                # 转换为RGB模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 缩放图片以适应预览区域
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width, canvas_height = 600, 400
                
                img_ratio = img.width / img.height
                canvas_ratio = canvas_width / canvas_height
                
                if img_ratio > canvas_ratio:
                    new_width = canvas_width - 20
                    new_height = int(new_width / img_ratio)
                else:
                    new_height = canvas_height - 20
                    new_width = int(new_height * img_ratio)
                
                preview_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 添加水印
                watermarked_img = self._add_watermark(preview_img, config)
                
                # 转换为PhotoImage
                self.photo = ImageTk.PhotoImage(watermarked_img)
                
                # 清除画布并显示图片
                self.canvas.delete("all")
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
                
        except Exception as e:
            logger.error(f"Failed to update preview: {e}")
            
    def _add_watermark(self, img: Image.Image, config: WatermarkConfig) -> Image.Image:
        """添加水印到图片"""
        # 创建副本
        watermarked = img.copy()
        
        if config.text:
            watermarked = self._add_text_watermark(watermarked, config)
        
        if config.image_path and Path(config.image_path).exists():
            watermarked = self._add_image_watermark(watermarked, config)
            
        return watermarked
    
    def _add_text_watermark(self, img: Image.Image, config: WatermarkConfig) -> Image.Image:
        """添加文本水印"""
        # 创建透明图层
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 设置字体
        try:
            font_style = ""
            if config.font_bold and config.font_italic:
                font_style = "bold italic"
            elif config.font_bold:
                font_style = "bold"
            elif config.font_italic:
                font_style = "italic"
                
            if font_style:
                font_name = f"{config.font_family} {font_style}"
            else:
                font_name = config.font_family
                
            font = ImageFont.truetype(font_name, config.font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), config.text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        x, y = self._calculate_position(img.size, (text_width, text_height), config.position, config.offset_x, config.offset_y)
        
        # 设置颜色和透明度
        alpha = int(255 * config.opacity / 100)
        color = (*config.color, alpha)
        
        # 绘制描边
        if config.stroke:
            stroke_color = (*config.stroke_color, alpha)
            for dx in range(-config.stroke_width, config.stroke_width + 1):
                for dy in range(-config.stroke_width, config.stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), config.text, font=font, fill=stroke_color)
        
        # 绘制阴影
        if config.shadow:
            shadow_color = (0, 0, 0, alpha // 2)
            draw.text((x + 2, y + 2), config.text, font=font, fill=shadow_color)
        
        # 绘制主文本
        draw.text((x, y), config.text, font=font, fill=color)
        
        # 旋转文本图层
        if config.rotation != 0:
            overlay = overlay.rotate(config.rotation, expand=True)
        
        # 合并图层
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        result = Image.alpha_composite(img, overlay)
        return result.convert('RGB')
    
    def _add_image_watermark(self, img: Image.Image, config: WatermarkConfig) -> Image.Image:
        """添加图片水印"""
        try:
            with Image.open(config.image_path) as watermark_img:
                # 缩放水印图片
                wm_width = int(watermark_img.width * config.image_scale)
                wm_height = int(watermark_img.height * config.image_scale)
                watermark_img = watermark_img.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
                
                # 设置透明度
                if watermark_img.mode != 'RGBA':
                    watermark_img = watermark_img.convert('RGBA')
                
                alpha = int(255 * config.image_opacity / 100)
                watermark_img.putalpha(alpha)
                
                # 计算位置
                x, y = self._calculate_position(img.size, (wm_width, wm_height), config.position, config.offset_x, config.offset_y)
                
                # 旋转水印
                if config.rotation != 0:
                    watermark_img = watermark_img.rotate(config.rotation, expand=True)
                
                # 合并图片
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                img.paste(watermark_img, (x, y), watermark_img)
                
        except Exception as e:
            logger.error(f"Failed to add image watermark: {e}")
        
        return img
    
    def _calculate_position(self, img_size: Tuple[int, int], item_size: Tuple[int, int], 
                          position: str, offset_x: int, offset_y: int) -> Tuple[int, int]:
        """计算水印位置"""
        img_width, img_height = img_size
        item_width, item_height = item_size
        
        position_map = {
            'top-left': (offset_x, offset_y),
            'top-center': ((img_width - item_width) // 2, offset_y),
            'top-right': (img_width - item_width - offset_x, offset_y),
            'center-left': (offset_x, (img_height - item_height) // 2),
            'center': ((img_width - item_width) // 2, (img_height - item_height) // 2),
            'center-right': (img_width - item_width - offset_x, (img_height - item_height) // 2),
            'bottom-left': (offset_x, img_height - item_height - offset_y),
            'bottom-center': ((img_width - item_width) // 2, img_height - item_height - offset_y),
            'bottom-right': (img_width - item_width - offset_x, img_height - item_height - offset_y)
        }
        
        return position_map.get(position, position_map['bottom-right'])


class PhotoWatermarkGUI:
    """图片水印GUI主类"""
    
    def __init__(self):
        if USE_CUSTOM_TKINTER:
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()
        
        self.root.title("Photo Watermark Tool")
        self.root.geometry("1200x800")
        
        # 数据
        self.image_items: List[ImageItem] = []
        self.current_image_index = 0
        self.config = WatermarkConfig()
        self.templates: Dict[str, Dict] = {}
        self.output_directory = ""
        
        # GUI组件
        self.image_listbox = None
        self.preview_canvas = None
        self.preview = None
        
        # 加载模板
        self.load_templates()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 图片列表和控制
        left_panel = ctk.CTkFrame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 右侧面板 - 预览和设置
        right_panel = ctk.CTkFrame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)
        
    def create_left_panel(self, parent):
        """创建左侧面板"""
        # 标题
        title_label = ctk.CTkLabel(parent, text="图片列表", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(10, 5))
        
        # 导入按钮框架
        import_frame = ctk.CTkFrame(parent)
        import_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 导入按钮
        import_btn = ctk.CTkButton(import_frame, text="导入图片", command=self.import_images)
        import_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        import_folder_btn = ctk.CTkButton(import_frame, text="导入文件夹", command=self.import_folder)
        import_folder_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        clear_btn = ctk.CTkButton(import_frame, text="清空", command=self.clear_images)
        clear_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 图片列表框架
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Treeview用于显示图片列表
        columns = ('name', 'size', 'status')
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        self.image_tree.heading('name', text='文件名')
        self.image_tree.heading('size', text='尺寸')
        self.image_tree.heading('status', text='状态')
        
        # 设置列宽
        self.image_tree.column('name', width=150)
        self.image_tree.column('size', width=80)
        self.image_tree.column('status', width=60)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=scrollbar.set)
        
        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.image_tree.bind('<<TreeviewSelect>>', self.on_image_select)
        
        # 导出设置框架
        export_frame = ctk.CTkFrame(parent)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        export_label = ctk.CTkLabel(export_frame, text="导出设置", font=ctk.CTkFont(size=14, weight="bold"))
        export_label.pack(pady=5)
        
        # 输出目录
        output_dir_frame = ctk.CTkFrame(export_frame)
        output_dir_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(output_dir_frame, text="输出目录:").pack(anchor=tk.W)
        
        dir_select_frame = ctk.CTkFrame(output_dir_frame)
        dir_select_frame.pack(fill=tk.X, pady=2)
        
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ctk.CTkEntry(dir_select_frame, textvariable=self.output_dir_var, state="readonly")
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        select_dir_btn = ctk.CTkButton(dir_select_frame, text="选择", width=60, command=self.select_output_directory)
        select_dir_btn.pack(side=tk.RIGHT)
        
        # 输出格式
        format_frame = ctk.CTkFrame(export_frame)
        format_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(format_frame, text="输出格式:").pack(anchor=tk.W)
        self.output_format_var = tk.StringVar(value="JPEG")
        format_combo = ctk.CTkComboBox(format_frame, values=["JPEG", "PNG"], variable=self.output_format_var)
        format_combo.pack(fill=tk.X, pady=2)
        
        # 文件命名
        naming_frame = ctk.CTkFrame(export_frame)
        naming_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(naming_frame, text="文件命名:").pack(anchor=tk.W)
        self.naming_var = tk.StringVar(value="suffix")
        naming_combo = ctk.CTkComboBox(naming_frame, values=["保留原名", "添加前缀", "添加后缀"], variable=self.naming_var)
        naming_combo.pack(fill=tk.X, pady=2)
        
        self.naming_text_var = tk.StringVar(value="_watermarked")
        naming_entry = ctk.CTkEntry(naming_frame, textvariable=self.naming_text_var, placeholder_text="前缀/后缀文本")
        naming_entry.pack(fill=tk.X, pady=2)
        
        # JPEG质量设置
        quality_frame = ctk.CTkFrame(export_frame)
        quality_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(quality_frame, text="JPEG质量:").pack(anchor=tk.W)
        self.quality_var = tk.IntVar(value=95)
        quality_slider = ctk.CTkSlider(quality_frame, from_=1, to=100, variable=self.quality_var)
        quality_slider.pack(fill=tk.X, pady=2)
        
        quality_label = ctk.CTkLabel(quality_frame, textvariable=self.quality_var)
        quality_label.pack()
        
        # 导出按钮
        export_btn = ctk.CTkButton(export_frame, text="导出所有图片", command=self.export_all_images)
        export_btn.pack(pady=10)
        
    def create_right_panel(self, parent):
        """创建右侧面板"""
        # 预览区域
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 10))
        
        preview_label = ctk.CTkLabel(preview_frame, text="预览", font=ctk.CTkFont(size=16, weight="bold"))
        preview_label.pack(pady=5)
        
        # 预览画布
        canvas_frame = ctk.CTkFrame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg='white', width=600, height=400)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 创建预览对象
        self.preview = WatermarkPreview(self.preview_canvas)
        
        # 设置区域
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(fill=tk.X, pady=(0, 0))
        
        self.create_settings_panel(settings_frame)
        
    def create_settings_panel(self, parent):
        """创建设置面板"""
        # 创建标签页
        tabview = ctk.CTkTabview(parent)
        tabview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文本水印标签页
        text_tab = tabview.add("文本水印")
        self.create_text_watermark_tab(text_tab)
        
        # 图片水印标签页
        image_tab = tabview.add("图片水印")
        self.create_image_watermark_tab(image_tab)
        
        # 位置设置标签页
        position_tab = tabview.add("位置设置")
        self.create_position_tab(position_tab)
        
        # 模板管理标签页
        template_tab = tabview.add("模板管理")
        self.create_template_tab(template_tab)
        
    def create_text_watermark_tab(self, parent):
        """创建文本水印设置标签页"""
        # 滚动框架
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 水印文本
        text_frame = ctk.CTkFrame(scroll_frame)
        text_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(text_frame, text="水印文本:").pack(anchor=tk.W, padx=5, pady=2)
        self.text_var = tk.StringVar(value=self.config.text)
        text_entry = ctk.CTkEntry(text_frame, textvariable=self.text_var)
        text_entry.pack(fill=tk.X, padx=5, pady=2)
        text_entry.bind('<KeyRelease>', self.on_text_change)
        
        # 字体设置
        font_frame = ctk.CTkFrame(scroll_frame)
        font_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(font_frame, text="字体设置", font=ctk.CTkFont(weight="bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # 字体族
        ctk.CTkLabel(font_frame, text="字体:").pack(anchor=tk.W, padx=5)
        self.font_family_var = tk.StringVar(value=self.config.font_family)
        font_combo = ctk.CTkComboBox(font_frame, values=["Arial", "Times New Roman", "Helvetica", "Courier"], 
                                   variable=self.font_family_var, command=self.on_font_change)
        font_combo.pack(fill=tk.X, padx=5, pady=2)
        
        # 字体大小
        ctk.CTkLabel(font_frame, text="字体大小:").pack(anchor=tk.W, padx=5)
        self.font_size_var = tk.IntVar(value=self.config.font_size)
        font_size_slider = ctk.CTkSlider(font_frame, from_=10, to=100, variable=self.font_size_var, command=self.on_font_size_change)
        font_size_slider.pack(fill=tk.X, padx=5, pady=2)
        
        font_size_label = ctk.CTkLabel(font_frame, textvariable=self.font_size_var)
        font_size_label.pack(padx=5)
        
        # 字体样式
        style_frame = ctk.CTkFrame(font_frame)
        style_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.bold_var = tk.BooleanVar(value=self.config.font_bold)
        bold_check = ctk.CTkCheckBox(style_frame, text="粗体", variable=self.bold_var, command=self.on_style_change)
        bold_check.pack(side=tk.LEFT, padx=5)
        
        self.italic_var = tk.BooleanVar(value=self.config.font_italic)
        italic_check = ctk.CTkCheckBox(style_frame, text="斜体", variable=self.italic_var, command=self.on_style_change)
        italic_check.pack(side=tk.LEFT, padx=5)
        
        # 颜色设置
        color_frame = ctk.CTkFrame(scroll_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(color_frame, text="颜色设置", font=ctk.CTkFont(weight="bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        color_select_frame = ctk.CTkFrame(color_frame)
        color_select_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(color_select_frame, text="文字颜色:").pack(side=tk.LEFT, padx=5)
        self.color_btn = ctk.CTkButton(color_select_frame, text="选择颜色", width=100, command=self.select_text_color)
        self.color_btn.pack(side=tk.RIGHT, padx=5)
        
        # 透明度
        ctk.CTkLabel(color_frame, text="透明度:").pack(anchor=tk.W, padx=5)
        self.opacity_var = tk.IntVar(value=self.config.opacity)
        opacity_slider = ctk.CTkSlider(color_frame, from_=0, to=100, variable=self.opacity_var, command=self.on_opacity_change)
        opacity_slider.pack(fill=tk.X, padx=5, pady=2)
        
        opacity_label = ctk.CTkLabel(color_frame, textvariable=self.opacity_var)
        opacity_label.pack(padx=5)
        
        # 效果设置
        effect_frame = ctk.CTkFrame(scroll_frame)
        effect_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(effect_frame, text="效果设置", font=ctk.CTkFont(weight="bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        self.shadow_var = tk.BooleanVar(value=self.config.shadow)
        shadow_check = ctk.CTkCheckBox(effect_frame, text="阴影", variable=self.shadow_var, command=self.on_effect_change)
        shadow_check.pack(anchor=tk.W, padx=5, pady=2)
        
        self.stroke_var = tk.BooleanVar(value=self.config.stroke)
        stroke_check = ctk.CTkCheckBox(effect_frame, text="描边", variable=self.stroke_var, command=self.on_effect_change)
        stroke_check.pack(anchor=tk.W, padx=5, pady=2)
        
        # 描边设置
        stroke_settings_frame = ctk.CTkFrame(effect_frame)
        stroke_settings_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(stroke_settings_frame, text="描边宽度:").pack(anchor=tk.W, padx=5)
        self.stroke_width_var = tk.IntVar(value=self.config.stroke_width)
        stroke_width_slider = ctk.CTkSlider(stroke_settings_frame, from_=1, to=10, variable=self.stroke_width_var, command=self.on_stroke_width_change)
        stroke_width_slider.pack(fill=tk.X, padx=5, pady=2)
        
        stroke_color_btn = ctk.CTkButton(stroke_settings_frame, text="描边颜色", command=self.select_stroke_color)
        stroke_color_btn.pack(pady=2)
        
    def create_image_watermark_tab(self, parent):
        """创建图片水印设置标签页"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 图片选择
        image_frame = ctk.CTkFrame(scroll_frame)
        image_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(image_frame, text="水印图片:").pack(anchor=tk.W, padx=5, pady=2)
        
        image_select_frame = ctk.CTkFrame(image_frame)
        image_select_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.watermark_image_var = tk.StringVar(value=self.config.image_path)
        image_entry = ctk.CTkEntry(image_select_frame, textvariable=self.watermark_image_var, state="readonly")
        image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        select_image_btn = ctk.CTkButton(image_select_frame, text="选择", width=60, command=self.select_watermark_image)
        select_image_btn.pack(side=tk.RIGHT)
        
        # 缩放设置
        scale_frame = ctk.CTkFrame(scroll_frame)
        scale_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(scale_frame, text="缩放比例:").pack(anchor=tk.W, padx=5)
        self.image_scale_var = tk.DoubleVar(value=self.config.image_scale)
        scale_slider = ctk.CTkSlider(scale_frame, from_=0.1, to=2.0, variable=self.image_scale_var, command=self.on_image_scale_change)
        scale_slider.pack(fill=tk.X, padx=5, pady=2)
        
        scale_label = ctk.CTkLabel(scale_frame, text=f"{self.config.image_scale:.1f}")
        scale_label.pack(padx=5)
        
        # 透明度设置
        image_opacity_frame = ctk.CTkFrame(scroll_frame)
        image_opacity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(image_opacity_frame, text="透明度:").pack(anchor=tk.W, padx=5)
        self.image_opacity_var = tk.IntVar(value=self.config.image_opacity)
        image_opacity_slider = ctk.CTkSlider(image_opacity_frame, from_=0, to=100, variable=self.image_opacity_var, command=self.on_image_opacity_change)
        image_opacity_slider.pack(fill=tk.X, padx=5, pady=2)
        
        image_opacity_label = ctk.CTkLabel(image_opacity_frame, textvariable=self.image_opacity_var)
        image_opacity_label.pack(padx=5)
        
    def create_position_tab(self, parent):
        """创建位置设置标签页"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 预设位置
        position_frame = ctk.CTkFrame(scroll_frame)
        position_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(position_frame, text="预设位置", font=ctk.CTkFont(weight="bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # 九宫格位置按钮
        grid_frame = ctk.CTkFrame(position_frame)
        grid_frame.pack(padx=5, pady=5)
        
        positions = [
            ['top-left', 'top-center', 'top-right'],
            ['center-left', 'center', 'center-right'],
            ['bottom-left', 'bottom-center', 'bottom-right']
        ]
        
        position_names = {
            'top-left': '左上', 'top-center': '上中', 'top-right': '右上',
            'center-left': '左中', 'center': '正中', 'center-right': '右中',
            'bottom-left': '左下', 'bottom-center': '下中', 'bottom-right': '右下'
        }
        
        self.position_var = tk.StringVar(value=self.config.position)
        
        for i, row in enumerate(positions):
            row_frame = ctk.CTkFrame(grid_frame)
            row_frame.pack(pady=2)
            for j, pos in enumerate(row):
                btn = ctk.CTkRadioButton(row_frame, text=position_names[pos], 
                                       variable=self.position_var, value=pos, 
                                       command=self.on_position_change)
                btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 偏移设置
        offset_frame = ctk.CTkFrame(scroll_frame)
        offset_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(offset_frame, text="偏移设置", font=ctk.CTkFont(weight="bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # X偏移
        ctk.CTkLabel(offset_frame, text="水平偏移:").pack(anchor=tk.W, padx=5)
        self.offset_x_var = tk.IntVar(value=self.config.offset_x)
        offset_x_slider = ctk.CTkSlider(offset_frame, from_=0, to=200, variable=self.offset_x_var, command=self.on_offset_change)
        offset_x_slider.pack(fill=tk.X, padx=5, pady=2)
        
        offset_x_label = ctk.CTkLabel(offset_frame, textvariable=self.offset_x_var)
        offset_x_label.pack(padx=5)
        
        # Y偏移
        ctk.CTkLabel(offset_frame, text="垂直偏移:").pack(anchor=tk.W, padx=5)
        self.offset_y_var = tk.IntVar(value=self.config.offset_y)
        offset_y_slider = ctk.CTkSlider(offset_frame, from_=0, to=200, variable=self.offset_y_var, command=self.on_offset_change)
        offset_y_slider.pack(fill=tk.X, padx=5, pady=2)
        
        offset_y_label = ctk.CTkLabel(offset_frame, textvariable=self.offset_y_var)
        offset_y_label.pack(padx=5)
        
        # 旋转设置
        rotation_frame = ctk.CTkFrame(scroll_frame)
        rotation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(rotation_frame, text="旋转角度:").pack(anchor=tk.W, padx=5)
        self.rotation_var = tk.IntVar(value=self.config.rotation)
        rotation_slider = ctk.CTkSlider(rotation_frame, from_=-180, to=180, variable=self.rotation_var, command=self.on_rotation_change)
        rotation_slider.pack(fill=tk.X, padx=5, pady=2)
        
        rotation_label = ctk.CTkLabel(rotation_frame, textvariable=self.rotation_var)
        rotation_label.pack(padx=5)
        
    def create_template_tab(self, parent):
        """创建模板管理标签页"""
        # 模板列表
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(list_frame, text="已保存的模板", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # 模板列表框
        self.template_listbox = tk.Listbox(list_frame, height=8)
        self.template_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 更新模板列表
        self.update_template_list()
        
        # 按钮框架
        btn_frame = ctk.CTkFrame(list_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        load_btn = ctk.CTkButton(btn_frame, text="加载模板", command=self.load_template)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ctk.CTkButton(btn_frame, text="保存当前设置", command=self.save_template)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ctk.CTkButton(btn_frame, text="删除模板", command=self.delete_template)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
    def bind_events(self):
        """绑定事件"""
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 简化拖拽支持 - 使用tkinter的基本拖拽
        self.preview_canvas.bind("<Button-1>", self.on_canvas_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
    def on_canvas_click(self, event):
        """画布点击事件"""
        pass
        
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        pass
        
    def on_drop(self, event):
        """处理拖拽文件"""
        files = event.data.split()
        for file_path in files:
            file_path = file_path.strip('{}')  # 移除可能的大括号
            if os.path.isfile(file_path):
                self.add_image(file_path)
            elif os.path.isdir(file_path):
                self.add_images_from_directory(file_path)
        
    def import_images(self):
        """导入图片文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=file_types
        )
        
        for file_path in files:
            self.add_image(file_path)
            
    def import_folder(self):
        """导入文件夹"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if folder_path:
            self.add_images_from_directory(folder_path)
            
    def add_image(self, file_path: str):
        """添加单个图片"""
        try:
            # 检查文件格式
            ext = Path(file_path).suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                return
                
            # 检查是否已存在
            for item in self.image_items:
                if item.path == Path(file_path):
                    return
                    
            # 创建图片项目
            image_item = ImageItem(file_path)
            self.image_items.append(image_item)
            
            # 更新列表显示
            self.update_image_list()
            
            # 如果是第一张图片，自动选择
            if len(self.image_items) == 1:
                self.current_image_index = 0
                self.update_preview()
                
        except Exception as e:
            logger.error(f"Failed to add image {file_path}: {e}")
            
    def add_images_from_directory(self, dir_path: str):
        """从目录添加图片"""
        supported_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        for file_path in Path(dir_path).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_exts:
                self.add_image(str(file_path))
                
    def clear_images(self):
        """清空图片列表"""
        self.image_items.clear()
        self.current_image_index = 0
        self.update_image_list()
        self.preview_canvas.delete("all")
        
    def update_image_list(self):
        """更新图片列表显示"""
        # 清空现有项目
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
            
        # 添加图片项目
        for i, item in enumerate(self.image_items):
            size_str = f"{item.size[0]}x{item.size[1]}" if item.size else "未知"
            status = "已处理" if item.processed else "待处理"
            
            self.image_tree.insert('', 'end', values=(item.name, size_str, status))
            
    def on_image_select(self, event):
        """图片选择事件"""
        selection = self.image_tree.selection()
        if selection:
            index = self.image_tree.index(selection[0])
            self.current_image_index = index
            self.update_preview()
            
    def update_preview(self):
        """更新预览"""
        if self.image_items and 0 <= self.current_image_index < len(self.image_items):
            current_item = self.image_items[self.current_image_index]
            self.preview.update_preview(current_item, self.config)
            
    def select_output_directory(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_directory = directory
            self.output_dir_var.set(directory)
            
    def select_watermark_image(self):
        """选择水印图片"""
        file_types = [
            ("PNG文件", "*.png"),
            ("图片文件", "*.jpg *.jpeg *.png *.bmp"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=file_types
        )
        
        if file_path:
            self.config.image_path = file_path
            self.watermark_image_var.set(file_path)
            self.update_preview()
            
    def select_text_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor(title="选择文字颜色", initialcolor=self.config.color)
        if color[0]:
            self.config.color = tuple(int(c) for c in color[0])
            self.update_preview()
            
    def select_stroke_color(self):
        """选择描边颜色"""
        color = colorchooser.askcolor(title="选择描边颜色", initialcolor=self.config.stroke_color)
        if color[0]:
            self.config.stroke_color = tuple(int(c) for c in color[0])
            self.update_preview()
            
    # 事件处理方法
    def on_text_change(self, event=None):
        """文本变化事件"""
        self.config.text = self.text_var.get()
        self.update_preview()
        
    def on_font_change(self, value=None):
        """字体变化事件"""
        self.config.font_family = self.font_family_var.get()
        self.update_preview()
        
    def on_font_size_change(self, value=None):
        """字体大小变化事件"""
        self.config.font_size = int(self.font_size_var.get())
        self.update_preview()
        
    def on_style_change(self):
        """字体样式变化事件"""
        self.config.font_bold = self.bold_var.get()
        self.config.font_italic = self.italic_var.get()
        self.update_preview()
        
    def on_opacity_change(self, value=None):
        """透明度变化事件"""
        self.config.opacity = int(self.opacity_var.get())
        self.update_preview()
        
    def on_effect_change(self):
        """效果变化事件"""
        self.config.shadow = self.shadow_var.get()
        self.config.stroke = self.stroke_var.get()
        self.update_preview()
        
    def on_stroke_width_change(self, value=None):
        """描边宽度变化事件"""
        self.config.stroke_width = int(self.stroke_width_var.get())
        self.update_preview()
        
    def on_image_scale_change(self, value=None):
        """图片缩放变化事件"""
        self.config.image_scale = self.image_scale_var.get()
        # 更新显示标签
        for widget in self.root.winfo_children():
            if hasattr(widget, 'winfo_children'):
                self._update_scale_label(widget)
        self.update_preview()
        
    def _update_scale_label(self, parent):
        """递归更新缩放标签"""
        for child in parent.winfo_children():
            if isinstance(child, ctk.CTkLabel) and hasattr(child, 'cget'):
                try:
                    if "scale_label" in str(child):
                        child.configure(text=f"{self.config.image_scale:.1f}")
                except:
                    pass
            if hasattr(child, 'winfo_children'):
                self._update_scale_label(child)
                
    def on_image_opacity_change(self, value=None):
        """图片透明度变化事件"""
        self.config.image_opacity = int(self.image_opacity_var.get())
        self.update_preview()
        
    def on_position_change(self):
        """位置变化事件"""
        self.config.position = self.position_var.get()
        self.update_preview()
        
    def on_offset_change(self, value=None):
        """偏移变化事件"""
        self.config.offset_x = int(self.offset_x_var.get())
        self.config.offset_y = int(self.offset_y_var.get())
        self.update_preview()
        
    def on_rotation_change(self, value=None):
        """旋转变化事件"""
        self.config.rotation = int(self.rotation_var.get())
        self.update_preview()
        
    def save_template(self):
        """保存模板"""
        name = simpledialog.askstring("保存模板", "请输入模板名称:")
        if name:
            self.templates[name] = self.config.to_dict()
            self.save_templates()
            self.update_template_list()
            messagebox.showinfo("成功", f"模板 '{name}' 已保存")
            
    def load_template(self):
        """加载模板"""
        selection = self.template_listbox.curselection()
        if selection:
            name = self.template_listbox.get(selection[0])
            if name in self.templates:
                self.config.from_dict(self.templates[name])
                self.update_all_controls()
                self.update_preview()
                messagebox.showinfo("成功", f"模板 '{name}' 已加载")
                
    def delete_template(self):
        """删除模板"""
        selection = self.template_listbox.curselection()
        if selection:
            name = self.template_listbox.get(selection[0])
            if messagebox.askyesno("确认删除", f"确定要删除模板 '{name}' 吗？"):
                del self.templates[name]
                self.save_templates()
                self.update_template_list()
                messagebox.showinfo("成功", f"模板 '{name}' 已删除")
                
    def update_template_list(self):
        """更新模板列表"""
        self.template_listbox.delete(0, tk.END)
        for name in self.templates.keys():
            self.template_listbox.insert(tk.END, name)
            
    def update_all_controls(self):
        """更新所有控件值"""
        self.text_var.set(self.config.text)
        self.font_family_var.set(self.config.font_family)
        self.font_size_var.set(self.config.font_size)
        self.bold_var.set(self.config.font_bold)
        self.italic_var.set(self.config.font_italic)
        self.opacity_var.set(self.config.opacity)
        self.shadow_var.set(self.config.shadow)
        self.stroke_var.set(self.config.stroke)
        self.stroke_width_var.set(self.config.stroke_width)
        self.watermark_image_var.set(self.config.image_path)
        self.image_scale_var.set(self.config.image_scale)
        self.image_opacity_var.set(self.config.image_opacity)
        self.position_var.set(self.config.position)
        self.offset_x_var.set(self.config.offset_x)
        self.offset_y_var.set(self.config.offset_y)
        self.rotation_var.set(self.config.rotation)
        
    def load_templates(self):
        """加载模板文件"""
        template_file = Path("watermark_templates.json")
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load templates: {e}")
                self.templates = {}
        else:
            self.templates = {}
            
    def save_templates(self):
        """保存模板文件"""
        try:
            with open("watermark_templates.json", 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save templates: {e}")
            
    def export_all_images(self):
        """导出所有图片"""
        if not self.image_items:
            messagebox.showwarning("警告", "没有图片需要导出")
            return
            
        if not self.output_directory:
            messagebox.showwarning("警告", "请先选择输出目录")
            return
            
        # 在新线程中执行导出
        threading.Thread(target=self._export_images_thread, daemon=True).start()
        
    def _export_images_thread(self):
        """导出图片线程"""
        try:
            success_count = 0
            total_count = len(self.image_items)
            
            for i, item in enumerate(self.image_items):
                try:
                    # 生成输出文件名
                    output_name = self._generate_output_filename(item.name)
                    output_path = Path(self.output_directory) / output_name
                    
                    # 处理图片
                    with Image.open(item.path) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                            
                        # 添加水印
                        watermarked = self.preview._add_watermark(img, self.config)
                        
                        # 保存图片
                        save_kwargs = {}
                        if self.output_format_var.get() == "JPEG":
                            save_kwargs['quality'] = self.quality_var.get()
                            save_kwargs['optimize'] = True
                            
                        watermarked.save(output_path, format=self.output_format_var.get(), **save_kwargs)
                        
                        item.processed = True
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process {item.path}: {e}")
                    
            # 更新UI
            self.root.after(0, lambda: self._export_complete(success_count, total_count))
            
        except Exception as e:
            logger.error(f"Export thread error: {e}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"导出过程中发生错误: {e}"))
            
    def _export_complete(self, success_count: int, total_count: int):
        """导出完成回调"""
        self.update_image_list()
        messagebox.showinfo("导出完成", f"成功导出 {success_count}/{total_count} 张图片")
        
    def _generate_output_filename(self, original_name: str) -> str:
        """生成输出文件名"""
        name_part = Path(original_name).stem
        ext = f".{self.output_format_var.get().lower()}"
        if ext == ".jpeg":
            ext = ".jpg"
            
        naming_rule = self.naming_var.get()
        naming_text = self.naming_text_var.get()
        
        if naming_rule == "保留原名":
            return f"{name_part}{ext}"
        elif naming_rule == "添加前缀":
            return f"{naming_text}{name_part}{ext}"
        else:  # 添加后缀
            return f"{name_part}{naming_text}{ext}"
            
    def on_closing(self):
        """窗口关闭事件"""
        # 保存当前设置
        self.save_templates()
        self.root.destroy()
        
    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    app = PhotoWatermarkGUI()
    app.run()


if __name__ == '__main__':
    main()