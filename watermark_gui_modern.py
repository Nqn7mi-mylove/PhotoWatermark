#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhotoWatermark Modern GUI - 现代化拖拽界面版本
支持拖拽、文件选择器和批量导入的现代化GUI界面

Version: 4.0.0
Release Date: 2025-01-25
"""

__version__ = "4.0.0"
__author__ = "PhotoWatermark Team"
__license__ = "MIT"

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import tkinter.simpledialog
from pathlib import Path
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFont
from typing import List, Dict, Optional, Tuple
import logging
from tkinterdnd2 import DND_FILES, TkinterDnD

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入现有模块
try:
    from photo_watermark import PhotoWatermark
    from template_manager import TemplateManager
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


class ModernPhotoWatermarkGUI:
    """现代化的PhotoWatermark GUI应用"""
    
    def __init__(self):
        # 初始化TkinterDnD
        self.root = TkinterDnD.Tk()
        self.root.title(f"PhotoWatermark v{__version__} - 现代化拖拽界面")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置图标和样式
        self.setup_styles()
        
        # 初始化变量
        self.image_items = []
        self.current_image_index = 0
        self.output_directory = tk.StringVar(value=str(Path.home() / "Desktop" / "Watermarked"))
        
        # 水印配置
        self.watermark_config = {
            'text': tk.StringVar(value="Sample Watermark"),
            'font_size': tk.IntVar(value=30),
            'font_family': tk.StringVar(value="Arial"),
            'color': tk.StringVar(value="#FFFFFF"),
            'opacity': tk.IntVar(value=80),
            'position': tk.StringVar(value="bottom-right"),
            'offset_x': tk.IntVar(value=20),
            'offset_y': tk.IntVar(value=20),
            'rotation': tk.IntVar(value=0),
            'image_path': tk.StringVar(value=""),
            'image_scale': tk.DoubleVar(value=1.0),
            'image_opacity': tk.IntVar(value=80),
            'output_format': tk.StringVar(value="JPEG"),
            'jpeg_quality': tk.IntVar(value=95)
        }
        
        # 拖拽相关变量
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.preview_scale = 1.0
        self.preview_offset_x = 0
        self.preview_offset_y = 0
        self.watermark_items = []  # 存储画布上的水印元素
        
        # 初始化组件
        self.photo_watermark = PhotoWatermark()
        self.template_manager = TemplateManager()
        
        # 创建界面
        self.create_widgets()
        self.bind_events()
        
        # 状态变量
        self.processing = False
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义样式
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('DropZone.TFrame', relief='solid', borderwidth=2)
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主容器
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建左右分栏
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # 左侧：图片导入和预览区域
        self.create_image_area(left_frame)
        
        # 右侧：水印设置区域
        self.create_settings_area(right_frame)
        
    def create_image_area(self, parent):
        """创建图片区域"""
        # 标题
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="📸 图片管理", style='Title.TLabel').pack(side=tk.LEFT)
        
        # 操作按钮
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="📁 选择文件", command=self.select_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📂 选择文件夹", command=self.select_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ 清空", command=self.clear_images).pack(side=tk.LEFT, padx=2)
        
        # 拖拽区域
        self.create_drop_zone(parent)
        
        # 图片列表
        self.create_image_list(parent)
        
        # 预览区域
        self.create_preview_area(parent)
        
    def create_drop_zone(self, parent):
        """创建拖拽区域"""
        drop_frame = ttk.LabelFrame(parent, text="拖拽区域", padding="20")
        drop_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 拖拽提示
        self.drop_label = ttk.Label(
            drop_frame, 
            text="🎯 将图片文件或文件夹拖拽到这里\n支持 JPG, PNG, BMP, TIFF 格式\n或点击上方按钮选择文件",
            justify=tk.CENTER,
            font=('Arial', 12)
        )
        self.drop_label.pack(expand=True)
        
        # 绑定拖拽事件
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # 鼠标悬停效果
        drop_frame.bind('<Enter>', lambda e: self.drop_label.configure(foreground='blue'))
        drop_frame.bind('<Leave>', lambda e: self.drop_label.configure(foreground='black'))
        
    def create_image_list(self, parent):
        """创建图片列表"""
        list_frame = ttk.LabelFrame(parent, text="图片列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview
        columns = ('name', 'size', 'status')
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题
        self.image_tree.heading('name', text='文件名')
        self.image_tree.heading('size', text='尺寸')
        self.image_tree.heading('status', text='状态')
        
        # 设置列宽
        self.image_tree.column('name', width=200)
        self.image_tree.column('size', width=100)
        self.image_tree.column('status', width=80)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.image_tree.bind('<<TreeviewSelect>>', self.on_image_select)
        
    def create_preview_area(self, parent):
        """创建预览区域"""
        preview_frame = ttk.LabelFrame(parent, text="预览", padding="5")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 预览画布
        self.preview_canvas = tk.Canvas(preview_frame, height=200, bg='white')
        self.preview_canvas.pack(fill=tk.X, padx=5, pady=5)
        
        # 预览信息
        self.preview_info = ttk.Label(preview_frame, text="请选择图片进行预览")
        self.preview_info.pack()
        
    def create_settings_area(self, parent):
        """创建设置区域"""
        # 设置容器
        settings_container = ttk.Frame(parent)
        settings_container.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(settings_container, text="⚙️ 水印设置", style='Title.TLabel').pack(pady=(0, 10))
        
        # 创建选项卡
        notebook = ttk.Notebook(settings_container)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 文本水印选项卡
        text_frame = ttk.Frame(notebook)
        notebook.add(text_frame, text="文本水印")
        self.create_text_watermark_settings(text_frame)
        
        # 图片水印选项卡
        image_frame = ttk.Frame(notebook)
        notebook.add(image_frame, text="图片水印")
        self.create_image_watermark_settings(image_frame)
        
        # 位置设置选项卡
        position_frame = ttk.Frame(notebook)
        notebook.add(position_frame, text="位置设置")
        self.create_position_settings(position_frame)
        
        # 模板管理选项卡
        template_frame = ttk.Frame(notebook)
        notebook.add(template_frame, text="模板管理")
        self.create_template_settings(template_frame)
        
        # 输出设置
        self.create_output_settings(settings_container)
        
        # 操作按钮
        self.create_action_buttons(settings_container)
        
    def create_text_watermark_settings(self, parent):
        """创建文本水印设置"""
        # 滚动框架
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 文本内容
        ttk.Label(scrollable_frame, text="水印文本:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(5, 2))
        text_entry = ttk.Entry(scrollable_frame, textvariable=self.watermark_config['text'], width=30)
        text_entry.pack(fill=tk.X, pady=(0, 10))
        text_entry.bind('<KeyRelease>', self.on_settings_change)
        
        # 字体设置
        font_frame = ttk.LabelFrame(scrollable_frame, text="字体设置", padding="5")
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_frame, text="字体:").grid(row=0, column=0, sticky=tk.W, pady=2)
        font_combo = ttk.Combobox(font_frame, textvariable=self.watermark_config['font_family'], 
                                 values=['Arial', 'Times New Roman', 'Helvetica', 'Courier', 'Verdana'])
        font_combo.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0), pady=2)
        font_combo.bind('<<ComboboxSelected>>', self.on_settings_change)
        
        ttk.Label(font_frame, text="大小:").grid(row=1, column=0, sticky=tk.W, pady=2)
        size_scale = ttk.Scale(font_frame, from_=10, to=100, variable=self.watermark_config['font_size'],
                              orient=tk.HORIZONTAL, command=self.on_settings_change)
        size_scale.grid(row=1, column=1, sticky=tk.EW, padx=(5, 0), pady=2)
        
        size_label = ttk.Label(font_frame, text="30")
        size_label.grid(row=1, column=2, padx=(5, 0), pady=2)
        
        def update_size_label(*args):
            size_label.config(text=str(int(self.watermark_config['font_size'].get())))
        self.watermark_config['font_size'].trace('w', update_size_label)
        
        font_frame.columnconfigure(1, weight=1)
        
        # 颜色设置
        color_frame = ttk.LabelFrame(scrollable_frame, text="颜色设置", padding="5")
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="文字颜色:").pack(anchor=tk.W)
        color_btn_frame = ttk.Frame(color_frame)
        color_btn_frame.pack(fill=tk.X, pady=2)
        
        self.color_preview = tk.Label(color_btn_frame, text="  ", bg=self.watermark_config['color'].get(),
                                     relief=tk.RAISED, width=3)
        self.color_preview.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(color_btn_frame, text="选择颜色", command=self.select_color).pack(side=tk.LEFT)
        
        # 透明度设置
        ttk.Label(scrollable_frame, text="透明度:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(10, 2))
        opacity_frame = ttk.Frame(scrollable_frame)
        opacity_frame.pack(fill=tk.X, pady=(0, 10))
        
        opacity_scale = ttk.Scale(opacity_frame, from_=0, to=100, variable=self.watermark_config['opacity'],
                                 orient=tk.HORIZONTAL, command=self.on_settings_change)
        opacity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        opacity_label = ttk.Label(opacity_frame, text="80%")
        opacity_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        def update_opacity_label(*args):
            opacity_label.config(text=f"{int(self.watermark_config['opacity'].get())}%")
        self.watermark_config['opacity'].trace('w', update_opacity_label)
        
        # 布局滚动框架
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_image_watermark_settings(self, parent):
        """创建图片水印设置"""
        # 图片选择
        ttk.Label(parent, text="水印图片:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(5, 2))
        
        img_frame = ttk.Frame(parent)
        img_frame.pack(fill=tk.X, pady=(0, 10))
        
        img_entry = ttk.Entry(img_frame, textvariable=self.watermark_config['image_path'])
        img_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(img_frame, text="浏览", command=self.select_watermark_image).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 缩放设置
        ttk.Label(parent, text="缩放比例:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(10, 2))
        scale_frame = ttk.Frame(parent)
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        
        scale_scale = ttk.Scale(scale_frame, from_=0.1, to=3.0, variable=self.watermark_config['image_scale'],
                               orient=tk.HORIZONTAL, command=self.on_settings_change)
        scale_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        scale_label = ttk.Label(scale_frame, text="1.0x")
        scale_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        def update_scale_label(*args):
            scale_label.config(text=f"{self.watermark_config['image_scale'].get():.1f}x")
        self.watermark_config['image_scale'].trace('w', update_scale_label)
        
        # 透明度设置
        ttk.Label(parent, text="透明度:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(10, 2))
        img_opacity_frame = ttk.Frame(parent)
        img_opacity_frame.pack(fill=tk.X, pady=(0, 10))
        
        img_opacity_scale = ttk.Scale(img_opacity_frame, from_=0, to=100, 
                                     variable=self.watermark_config['image_opacity'],
                                     orient=tk.HORIZONTAL, command=self.on_settings_change)
        img_opacity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        img_opacity_label = ttk.Label(img_opacity_frame, text="80%")
        img_opacity_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        def update_img_opacity_label(*args):
            img_opacity_label.config(text=f"{int(self.watermark_config['image_opacity'].get())}%")
        self.watermark_config['image_opacity'].trace('w', update_img_opacity_label)
        
    def create_position_settings(self, parent):
        """创建位置设置"""
        # 位置选择
        ttk.Label(parent, text="水印位置:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(5, 2))
        
        positions = [
            ("左上角", "top-left"),
            ("上方中央", "top-center"),
            ("右上角", "top-right"),
            ("左侧中央", "middle-left"),
            ("中央", "center"),
            ("右侧中央", "middle-right"),
            ("左下角", "bottom-left"),
            ("下方中央", "bottom-center"),
            ("右下角", "bottom-right")
        ]
        
        pos_frame = ttk.Frame(parent)
        pos_frame.pack(fill=tk.X, pady=(0, 10))
        
        for i, (text, value) in enumerate(positions):
            row, col = divmod(i, 3)
            ttk.Radiobutton(pos_frame, text=text, variable=self.watermark_config['position'], 
                           value=value, command=self.on_settings_change).grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
        
        # 偏移设置
        offset_frame = ttk.LabelFrame(parent, text="位置偏移", padding="5")
        offset_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(offset_frame, text="水平偏移:").grid(row=0, column=0, sticky=tk.W, pady=2)
        x_scale = ttk.Scale(offset_frame, from_=0, to=200, variable=self.watermark_config['offset_x'],
                           orient=tk.HORIZONTAL, command=self.on_settings_change)
        x_scale.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0), pady=2)
        
        x_label = ttk.Label(offset_frame, text="20px")
        x_label.grid(row=0, column=2, padx=(5, 0), pady=2)
        
        ttk.Label(offset_frame, text="垂直偏移:").grid(row=1, column=0, sticky=tk.W, pady=2)
        y_scale = ttk.Scale(offset_frame, from_=0, to=200, variable=self.watermark_config['offset_y'],
                           orient=tk.HORIZONTAL, command=self.on_settings_change)
        y_scale.grid(row=1, column=1, sticky=tk.EW, padx=(5, 0), pady=2)
        
        y_label = ttk.Label(offset_frame, text="20px")
        y_label.grid(row=1, column=2, padx=(5, 0), pady=2)
        
        offset_frame.columnconfigure(1, weight=1)
        
        def update_offset_labels(*args):
            x_label.config(text=f"{int(self.watermark_config['offset_x'].get())}px")
            y_label.config(text=f"{int(self.watermark_config['offset_y'].get())}px")
        
        self.watermark_config['offset_x'].trace('w', update_offset_labels)
        self.watermark_config['offset_y'].trace('w', update_offset_labels)
        
        # 旋转设置
        ttk.Label(parent, text="旋转角度:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(10, 2))
        rotation_frame = ttk.Frame(parent)
        rotation_frame.pack(fill=tk.X, pady=(0, 10))
        
        rotation_scale = ttk.Scale(rotation_frame, from_=-180, to=180, variable=self.watermark_config['rotation'],
                                  orient=tk.HORIZONTAL, command=self.on_settings_change)
        rotation_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        rotation_label = ttk.Label(rotation_frame, text="0°")
        rotation_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        def update_rotation_label(*args):
            rotation_label.config(text=f"{int(self.watermark_config['rotation'].get())}°")
        self.watermark_config['rotation'].trace('w', update_rotation_label)
        
    def create_template_settings(self, parent):
        """创建模板设置"""
        # 模板列表
        ttk.Label(parent, text="保存的模板:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(5, 2))
        
        self.template_listbox = tk.Listbox(parent, height=6)
        self.template_listbox.pack(fill=tk.X, pady=(0, 10))
        
        # 模板操作按钮
        template_btn_frame = ttk.Frame(parent)
        template_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(template_btn_frame, text="保存模板", command=self.save_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(template_btn_frame, text="加载模板", command=self.load_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(template_btn_frame, text="删除模板", command=self.delete_template).pack(side=tk.LEFT, padx=5)
        
        # 更新模板列表
        self.update_template_list()
        
    def create_output_settings(self, parent):
        """创建输出设置"""
        output_frame = ttk.LabelFrame(parent, text="输出设置", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="输出目录:").pack(anchor=tk.W)
        
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=2)
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_directory)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(dir_frame, text="浏览", command=self.select_output_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 输出格式选择
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
        format_combo = ttk.Combobox(format_frame, textvariable=self.watermark_config['output_format'], 
                                   values=["JPEG", "PNG"], state="readonly", width=10)
        format_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # JPEG质量设置
        quality_frame = ttk.Frame(format_frame)
        quality_frame.pack(side=tk.TOP, pady=(10, 5))
        
        self.quality_label = ttk.Label(quality_frame, text="JPEG质量:")
        self.quality_label.pack(side=tk.LEFT)
        
        self.quality_scale = ttk.Scale(quality_frame, from_=10, to=100, orient=tk.HORIZONTAL,
                                      variable=self.watermark_config['jpeg_quality'])
        self.quality_scale.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        self.quality_value_label = ttk.Label(quality_frame, text="95")
        self.quality_value_label.pack(side=tk.LEFT)
        
        # 绑定事件
        format_combo.bind('<<ComboboxSelected>>', self._on_format_change)
        self.quality_scale.bind('<Motion>', self._on_quality_change)
        self.quality_scale.bind('<ButtonRelease-1>', self._on_quality_change)
        
        # 初始化质量控件状态
        self._on_format_change()
        
    def create_action_buttons(self, parent):
        """创建操作按钮"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 处理按钮
        self.process_btn = ttk.Button(btn_frame, text="🚀 开始处理", command=self.process_images)
        self.process_btn.pack(fill=tk.X, pady=(0, 5))
        
        # 进度条
        self.progress = ttk.Progressbar(btn_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # 状态标签
        self.status_label = ttk.Label(btn_frame, text="就绪")
        self.status_label.pack()
        
    def bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定鼠标滚轮事件到预览画布
        self.preview_canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # 绑定预览画布的拖拽事件
        self.preview_canvas.bind("<Button-1>", self.on_preview_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_preview_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_preview_release)
        self.preview_canvas.bind("<Motion>", self.on_preview_motion)
        
    def on_drop(self, event):
        """处理拖拽事件"""
        files = self.root.tk.splitlist(event.data)
        self.add_files(files)
        
    def add_files(self, files):
        """添加文件"""
        for file_path in files:
            path = Path(file_path)
            if path.is_file():
                self.add_image_file(str(path))
            elif path.is_dir():
                self.add_images_from_directory(str(path))
        
        self.update_image_list()
        self.update_drop_zone_text()
        
    def add_image_file(self, file_path):
        """添加单个图片文件"""
        try:
            path = Path(file_path)
            if path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                return False
                
            # 检查是否已存在
            for item in self.image_items:
                if item['path'] == str(path):
                    return False
                    
            # 获取图片信息
            with Image.open(file_path) as img:
                size = f"{img.width}x{img.height}"
                
            # 添加到列表
            self.image_items.append({
                'path': str(path),
                'name': path.name,
                'size': size,
                'status': '待处理'
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add image {file_path}: {e}")
            return False
            
    def add_images_from_directory(self, dir_path):
        """从目录添加图片"""
        supported_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        added_count = 0
        
        for file_path in Path(dir_path).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_exts:
                if self.add_image_file(str(file_path)):
                    added_count += 1
                    
        return added_count
        
    def select_files(self):
        """选择文件"""
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
        
        if files:
            self.add_files(files)
            
    def select_folder(self):
        """选择文件夹"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if folder_path:
            added_count = self.add_images_from_directory(folder_path)
            self.update_image_list()
            self.update_drop_zone_text()
            messagebox.showinfo("导入完成", f"成功导入 {added_count} 张图片")
            
    def clear_images(self):
        """清空图片列表"""
        if self.image_items and messagebox.askyesno("确认", "确定要清空所有图片吗？"):
            self.image_items.clear()
            self.update_image_list()
            self.update_drop_zone_text()
            self.preview_canvas.delete("all")
            self.preview_info.config(text="请选择图片进行预览")
            
    def update_image_list(self):
        """更新图片列表显示"""
        # 清空现有项目
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
            
        # 添加新项目
        for i, item in enumerate(self.image_items):
            self.image_tree.insert('', 'end', values=(item['name'], item['size'], item['status']))
            
    def update_drop_zone_text(self):
        """更新拖拽区域文本"""
        count = len(self.image_items)
        if count == 0:
            text = "🎯 将图片文件或文件夹拖拽到这里\n支持 JPG, PNG, BMP, TIFF 格式\n或点击上方按钮选择文件"
        else:
            text = f"✅ 已添加 {count} 张图片\n继续拖拽添加更多图片"
            
        self.drop_label.config(text=text)
        
    def on_image_select(self, event):
        """图片选择事件"""
        selection = self.image_tree.selection()
        if selection:
            item_id = selection[0]
            index = self.image_tree.index(item_id)
            self.current_image_index = index
            self.update_preview()
            
    def update_preview(self):
        """更新预览"""
        if not self.image_items or self.current_image_index >= len(self.image_items):
            return
            
        try:
            item = self.image_items[self.current_image_index]
            image_path = item['path']
            
            # 加载图片
            with Image.open(image_path) as img:
                # 创建预览图片
                preview_img = self.create_watermark_preview(img)
                
                # 调整预览尺寸
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    preview_img.thumbnail((canvas_width - 10, canvas_height - 10), Image.Resampling.LANCZOS)
                    
                    # 转换为PhotoImage
                    self.preview_photo = ImageTk.PhotoImage(preview_img)
                    
                    # 清空画布并显示图片
                    self.preview_canvas.delete("all")
                    self.watermark_items.clear()  # 清空水印元素列表
                    
                    x = (canvas_width - preview_img.width) // 2
                    y = (canvas_height - preview_img.height) // 2
                    
                    # 显示背景图片
                    bg_item = self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_photo)
                    
                    # 添加可拖拽的水印指示器
                    self.add_watermark_indicators(img, preview_img, x, y)
                    
                    # 更新信息
                    self.preview_info.config(text=f"预览: {item['name']} ({item['size']}) - 可拖拽水印位置")
                    
        except Exception as e:
            logger.error(f"Failed to update preview: {e}")
            self.preview_info.config(text="预览失败")
            
    def add_watermark_indicators(self, original_img, preview_img, preview_x, preview_y):
        """在预览中添加可拖拽的水印指示器"""
        try:
            # 计算缩放比例
            scale_x = preview_img.width / original_img.width
            scale_y = preview_img.height / original_img.height
            
            # 添加文本水印指示器
            if self.watermark_config['text'].get().strip():
                text_pos = self.calculate_watermark_preview_position(
                    original_img.size, 
                    self.get_text_watermark_size(original_img),
                    scale_x, scale_y, preview_x, preview_y
                )
                if text_pos:
                    # 创建文本水印指示器（半透明边框，不填充）
                    x1, y1, x2, y2 = text_pos
                    text_indicator = self.preview_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="red", width=2, stipple="gray25",
                        fill="", tags="watermark_text"
                    )
                    self.watermark_items.append(text_indicator)
                    
                    # 添加小标签在边框外
                    label_x = x1
                    label_y = y1 - 12  # 在矩形上方
                    if label_y < 0:  # 如果上方空间不够，放在下方
                        label_y = y2 + 12
                    text_label = self.preview_canvas.create_text(
                        label_x, label_y, 
                        text="文本", fill="red", font=("Arial", 8, "bold"),
                        anchor="w", tags="watermark_text"
                    )
                    self.watermark_items.append(text_label)
            
            # 添加图片水印指示器
            if self.watermark_config['image_path'].get().strip():
                img_pos = self.calculate_watermark_preview_position(
                    original_img.size,
                    self.get_image_watermark_size(original_img),
                    scale_x, scale_y, preview_x, preview_y
                )
                if img_pos:
                    # 创建图片水印指示器（半透明边框，不填充）
                    x1, y1, x2, y2 = img_pos
                    img_indicator = self.preview_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="blue", width=2, stipple="gray25",
                        fill="", tags="watermark_image"
                    )
                    self.watermark_items.append(img_indicator)
                    
                    # 添加小标签在边框外
                    label_x = x1
                    label_y = y1 - 12  # 在矩形上方
                    if label_y < 0:  # 如果上方空间不够，放在下方
                        label_y = y2 + 12
                    img_label = self.preview_canvas.create_text(
                        label_x, label_y,
                        text="图片", fill="blue", font=("Arial", 8, "bold"),
                        anchor="w", tags="watermark_image"
                    )
                    self.watermark_items.append(img_label)
                    
        except Exception as e:
            logger.error(f"Failed to add watermark indicators: {e}")
            
    def get_text_watermark_size(self, img):
        """获取文本水印的尺寸"""
        try:
            text = self.watermark_config['text'].get()
            font_size = self.watermark_config['font_size'].get()
            font_family = self.watermark_config['font_family'].get()
            
            # 创建临时绘图对象来计算文本尺寸
            temp_img = Image.new('RGB', (100, 100))
            draw = ImageDraw.Draw(temp_img)
            
            try:
                font = ImageFont.truetype(font_family, font_size)
            except:
                font = ImageFont.load_default()
                
            bbox = draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            return (width, height)
        except:
            return (100, 30)  # 默认尺寸
            
    def get_image_watermark_size(self, img):
        """获取图片水印的尺寸"""
        try:
            watermark_path = self.watermark_config['image_path'].get()
            scale = self.watermark_config['image_scale'].get()
            
            if watermark_path and os.path.exists(watermark_path):
                with Image.open(watermark_path) as wm_img:
                    width = int(wm_img.width * scale)
                    height = int(wm_img.height * scale)
                    return (width, height)
        except:
            pass
        return (50, 50)  # 默认尺寸
        
    def calculate_watermark_preview_position(self, img_size, watermark_size, scale_x, scale_y, preview_x, preview_y):
        """计算水印在预览中的位置"""
        try:
            position = self.watermark_config['position'].get()
            offset_x = self.watermark_config['offset_x'].get()
            offset_y = self.watermark_config['offset_y'].get()
            
            # 计算原图中的水印位置
            orig_x, orig_y = self.calculate_position(img_size, watermark_size, position, offset_x, offset_y)
            
            # 转换到预览坐标
            preview_wm_x = preview_x + orig_x * scale_x
            preview_wm_y = preview_y + orig_y * scale_y
            preview_wm_width = watermark_size[0] * scale_x
            preview_wm_height = watermark_size[1] * scale_y
            
            return (
                int(preview_wm_x), 
                int(preview_wm_y),
                int(preview_wm_x + preview_wm_width),
                int(preview_wm_y + preview_wm_height)
            )
        except:
            return None
    
    def create_watermark_preview(self, img):
        """创建带水印的预览图片"""
        # 复制图片
        preview_img = img.copy()
        
        # 添加文本水印
        if self.watermark_config['text'].get().strip():
            preview_img = self.add_text_watermark(preview_img)
            
        # 添加图片水印
        if self.watermark_config['image_path'].get().strip():
            preview_img = self.add_image_watermark(preview_img)
            
        return preview_img
        
    def add_text_watermark(self, img):
        """添加文本水印"""
        try:
            # 创建绘图对象
            draw = ImageDraw.Draw(img)
            
            # 获取配置
            text = self.watermark_config['text'].get()
            font_size = self.watermark_config['font_size'].get()
            font_family = self.watermark_config['font_family'].get()
            color_hex = self.watermark_config['color'].get()
            opacity = self.watermark_config['opacity'].get()
            position = self.watermark_config['position'].get()
            offset_x = self.watermark_config['offset_x'].get()
            offset_y = self.watermark_config['offset_y'].get()
            rotation = self.watermark_config['rotation'].get()
            
            # 转换颜色
            color = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
            color_with_alpha = (*color, int(255 * opacity / 100))
            
            # 加载字体
            try:
                font = ImageFont.truetype(font_family, font_size)
            except:
                font = ImageFont.load_default()
                
            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置
            x, y = self.calculate_position(img.size, (text_width, text_height), position, offset_x, offset_y)
            
            # 如果需要旋转，创建透明图层
            if rotation != 0:
                # 创建透明图层
                txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
                txt_draw = ImageDraw.Draw(txt_layer)
                txt_draw.text((x, y), text, font=font, fill=color_with_alpha)
                
                # 旋转图层
                rotated = txt_layer.rotate(rotation, expand=False)
                
                # 合并到原图
                img = Image.alpha_composite(img.convert('RGBA'), rotated).convert('RGB')
            else:
                # 直接绘制文本
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                draw = ImageDraw.Draw(img)
                draw.text((x, y), text, font=font, fill=color_with_alpha)
                img = img.convert('RGB')
                
        except Exception as e:
            logger.error(f"Failed to add text watermark: {e}")
            
        return img
        
    def add_image_watermark(self, img):
        """添加图片水印"""
        try:
            watermark_path = self.watermark_config['image_path'].get()
            if not watermark_path or not os.path.exists(watermark_path):
                return img
                
            # 加载水印图片
            with Image.open(watermark_path) as watermark:
                # 获取配置
                scale = self.watermark_config['image_scale'].get()
                opacity = self.watermark_config['image_opacity'].get()
                position = self.watermark_config['position'].get()
                offset_x = self.watermark_config['offset_x'].get()
                offset_y = self.watermark_config['offset_y'].get()
                
                # 调整水印尺寸
                new_size = (int(watermark.width * scale), int(watermark.height * scale))
                watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)
                
                # 调整透明度
                if watermark.mode != 'RGBA':
                    watermark = watermark.convert('RGBA')
                    
                # 应用透明度
                alpha = watermark.split()[-1]
                alpha = alpha.point(lambda p: int(p * opacity / 100))
                watermark.putalpha(alpha)
                
                # 计算位置
                x, y = self.calculate_position(img.size, watermark.size, position, offset_x, offset_y)
                
                # 合并图片
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                    
                img.paste(watermark, (x, y), watermark)
                img = img.convert('RGB')
                
        except Exception as e:
            logger.error(f"Failed to add image watermark: {e}")
            
        return img
        
    def calculate_position(self, img_size, item_size, position, offset_x, offset_y):
        """计算水印位置"""
        img_width, img_height = img_size
        item_width, item_height = item_size
        
        positions = {
            'top-left': (offset_x, offset_y),
            'top-center': ((img_width - item_width) // 2, offset_y),
            'top-right': (img_width - item_width - offset_x, offset_y),
            'middle-left': (offset_x, (img_height - item_height) // 2),
            'center': ((img_width - item_width) // 2, (img_height - item_height) // 2),
            'middle-right': (img_width - item_width - offset_x, (img_height - item_height) // 2),
            'bottom-left': (offset_x, img_height - item_height - offset_y),
            'bottom-center': ((img_width - item_width) // 2, img_height - item_height - offset_y),
            'bottom-right': (img_width - item_width - offset_x, img_height - item_height - offset_y)
        }
        
        return positions.get(position, positions['bottom-right'])
     
    def select_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(title="选择文字颜色")
        if color[1]:  # color[1] 是十六进制颜色值
            self.watermark_config['color'].set(color[1])
            self.color_preview.config(bg=color[1])
            self.on_settings_change()
            
    def select_watermark_image(self):
        """选择水印图片"""
        file_types = [
            ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("PNG文件", "*.png"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=file_types
        )
        
        if file_path:
            self.watermark_config['image_path'].set(file_path)
            self.on_settings_change()
            
    def select_output_directory(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_directory.set(directory)
            
    def on_settings_change(self, *args):
        """设置改变事件"""
        # 更新预览
        if hasattr(self, 'preview_canvas'):
            self.root.after_idle(self.update_preview)
            
    def on_mousewheel(self, event):
        """鼠标滚轮事件"""
        # 可以用于缩放预览图片
        pass
        
    def on_preview_click(self, event):
        """预览画布鼠标点击事件"""
        if not self.image_items or self.current_image_index >= len(self.image_items):
            return
            
        # 检查是否点击在水印区域
        clicked_item = self.preview_canvas.find_closest(event.x, event.y)[0]
        
        # 检查是否是水印元素
        if clicked_item in self.watermark_items:
            self.dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.preview_canvas.config(cursor="hand2")
            
    def on_preview_drag(self, event):
        """预览画布拖拽事件"""
        if not self.dragging:
            return
            
        # 计算本次拖拽的增量距离
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        # 更新水印位置（使用增量）
        self.update_watermark_position_from_drag(dx, dy)
        
        # 更新起始位置为当前位置，确保下次计算的是增量
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # 实时更新预览
        self.update_preview()
        
    def on_preview_release(self, event):
        """预览画布鼠标释放事件"""
        if self.dragging:
            self.dragging = False
            self.preview_canvas.config(cursor="")
            
    def on_preview_motion(self, event):
        """预览画布鼠标移动事件"""
        if not self.dragging:
            # 检查鼠标是否悬停在水印上
            try:
                closest_items = self.preview_canvas.find_closest(event.x, event.y)
                if closest_items:
                    closest_item = closest_items[0]
                    if closest_item in self.watermark_items:
                        self.preview_canvas.config(cursor="hand2")
                    else:
                        self.preview_canvas.config(cursor="")
                else:
                    self.preview_canvas.config(cursor="")
            except (IndexError, tk.TclError):
                # 如果画布上没有元素或发生其他错误，设置默认光标
                self.preview_canvas.config(cursor="")
                
    def update_watermark_position_from_drag(self, dx, dy):
        """根据拖拽距离更新水印位置"""
        if not self.image_items or self.current_image_index >= len(self.image_items):
            return
            
        # 获取画布和图片尺寸
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
            
        # 计算相对于原图的偏移量
        # 这里需要考虑预览图片的缩放比例
        try:
            item = self.image_items[self.current_image_index]
            with Image.open(item['path']) as img:
                # 计算预览图片的实际尺寸和位置
                preview_img = img.copy()
                preview_img.thumbnail((canvas_width - 10, canvas_height - 10), Image.Resampling.LANCZOS)
                
                # 计算缩放比例
                scale_x = img.width / preview_img.width
                scale_y = img.height / preview_img.height
                
                # 转换拖拽距离到原图坐标（强制取反方向修正）
                real_dx = -dx * scale_x
                real_dy = -dy * scale_y
                
                # 更新偏移量（直接加上增量）
                current_x = self.watermark_config['offset_x'].get()
                current_y = self.watermark_config['offset_y'].get()
                
                new_x = max(0, min(img.width, current_x + real_dx))
                new_y = max(0, min(img.height, current_y + real_dy))
                
                self.watermark_config['offset_x'].set(int(new_x))
                self.watermark_config['offset_y'].set(int(new_y))
                
        except Exception as e:
            logger.error(f"Failed to update watermark position: {e}")
            
    def save_template(self):
        """保存模板"""
        # 简单的输入对话框
        name = tk.simpledialog.askstring("保存模板", "请输入模板名称:")
        if name:
            try:
                # 收集当前设置
                config = {}
                for key, var in self.watermark_config.items():
                    config[key] = var.get()
                
                # 添加输出设置
                config['output_format'] = self.watermark_config['output_format'].get()
                config['jpeg_quality'] = self.watermark_config['jpeg_quality'].get()
                
                # 修复字段名映射问题
                if 'color' in config:
                    # 将颜色从十六进制转换为RGB元组
                    color_hex = config['color']
                    if color_hex.startswith('#'):
                        color_hex = color_hex[1:]
                    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                    config['font_color'] = rgb
                    del config['color']  # 删除原字段
                    
                # 保存模板 - 修正参数顺序
                success = self.template_manager.save_template(name, config, "用户自定义模板", overwrite=True)
                if success:
                    self.update_template_list()
                    messagebox.showinfo("成功", f"模板 '{name}' 保存成功！")
                else:
                    messagebox.showerror("错误", f"保存模板 '{name}' 失败")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存模板失败: {e}")
                logger.error(f"Save template error: {e}")
                
    def load_template(self):
        """加载模板"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
            
        template_name = self.template_listbox.get(selection[0])
        
        try:
            # load_template返回config字典，不是template对象
            config = self.template_manager.load_template(template_name)
            if config:
                # 应用模板设置
                for key, value in config.items():
                    if key in self.watermark_config:
                        if key == 'font_color':
                            # 将RGB元组转换为十六进制颜色
                            if isinstance(value, (list, tuple)) and len(value) >= 3:
                                hex_color = f"#{value[0]:02x}{value[1]:02x}{value[2]:02x}"
                                self.watermark_config['color'].set(hex_color)
                                self.color_preview.config(bg=hex_color)
                        elif key in ['output_format', 'jpeg_quality']:
                            # 处理输出格式设置
                            self.watermark_config[key].set(value)
                            if key == 'output_format':
                                self._on_format_change()
                            elif key == 'jpeg_quality':
                                self._on_quality_change()
                        else:
                            self.watermark_config[key].set(value)
                    elif key == 'font_color':
                        # 将RGB元组转换为十六进制颜色
                        if isinstance(value, (list, tuple)) and len(value) == 3:
                            hex_color = '#%02x%02x%02x' % tuple(value)
                            self.watermark_config['color'].set(hex_color)
                            self.color_preview.config(bg=hex_color)
                
                # 更新颜色预览
                self.update_preview()
                messagebox.showinfo("成功", f"模板 '{template_name}' 加载成功！")
            else:
                messagebox.showerror("错误", f"加载模板 '{template_name}' 失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载模板失败: {e}")
            logger.error(f"Load template error: {e}")
            
    def delete_template(self):
        """删除模板"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
            
        template_name = self.template_listbox.get(selection[0])
        
        if messagebox.askyesno("确认", f"确定要删除模板 '{template_name}' 吗？"):
            try:
                self.template_manager.delete_template(template_name)
                self.update_template_list()
                messagebox.showinfo("成功", f"模板 '{template_name}' 删除成功！")
                
            except Exception as e:
                messagebox.showerror("错误", f"删除模板失败: {e}")
                
    def update_template_list(self):
        """更新模板列表"""
        self.template_listbox.delete(0, tk.END)
        
        try:
            templates = self.template_manager.list_templates()
            for template_info in templates:
                self.template_listbox.insert(tk.END, template_info['name'])
                
        except Exception as e:
            logger.error(f"Failed to update template list: {e}")
            
    def process_images(self):
        """处理图片"""
        if not self.image_items:
            messagebox.showwarning("警告", "请先添加图片")
            return
            
        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请稍候")
            return
            
        # 检查输出目录
        output_dir = Path(self.output_directory.get())
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建输出目录: {e}")
            return
            
        # 开始处理
        self.processing = True
        self.process_btn.config(text="处理中...", state='disabled')
        self.progress.config(maximum=len(self.image_items), value=0)
        
        # 在新线程中处理
        thread = threading.Thread(target=self._process_images_thread)
        thread.daemon = True
        thread.start()
        
    def _process_images_thread(self):
        """处理图片线程"""
        success_count = 0
        total_count = len(self.image_items)
        
        for i, item in enumerate(self.image_items):
            try:
                # 更新状态
                self.root.after(0, lambda idx=i: self._update_item_status(idx, "处理中"))
                self.root.after(0, lambda val=i: self.progress.config(value=val))
                self.root.after(0, lambda: self.status_label.config(text=f"处理中 {i+1}/{total_count}"))
                
                # 处理图片
                input_path = item['path']
                output_format = self.watermark_config['output_format'].get()
                file_extension = '.jpg' if output_format == 'JPEG' else '.png'
                output_path = Path(self.output_directory.get()) / f"watermarked_{Path(item['name']).stem}{file_extension}"
                
                # 加载图片
                with Image.open(input_path) as img:
                    # 添加水印
                    watermarked_img = self.create_watermark_preview(img)
                    
                    # 保存图片
                    if output_format == 'JPEG':
                        # 如果原图有透明通道，转换为RGB
                        if watermarked_img.mode in ('RGBA', 'LA'):
                            background = Image.new('RGB', watermarked_img.size, (255, 255, 255))
                            background.paste(watermarked_img, mask=watermarked_img.split()[-1] if watermarked_img.mode == 'RGBA' else None)
                            watermarked_img = background
                        
                        quality = self.watermark_config['jpeg_quality'].get()
                        watermarked_img.save(str(output_path), format='JPEG', quality=quality, optimize=True)
                    else:  # PNG
                        watermarked_img.save(str(output_path), format='PNG', optimize=True)
                    
                success_count += 1
                self.root.after(0, lambda idx=i: self._update_item_status(idx, "完成"))
                
            except Exception as e:
                logger.error(f"Failed to process {item['path']}: {e}")
                self.root.after(0, lambda idx=i: self._update_item_status(idx, "失败"))
                
        # 处理完成
        self.root.after(0, lambda: self._process_complete(success_count, total_count))
        
    def _update_item_status(self, index, status):
        """更新项目状态"""
        if index < len(self.image_items):
            self.image_items[index]['status'] = status
            
            # 更新树视图
            children = self.image_tree.get_children()
            if index < len(children):
                item_id = children[index]
                values = list(self.image_tree.item(item_id, 'values'))
                values[2] = status  # 状态列
                self.image_tree.item(item_id, values=values)
                
    def _process_complete(self, success_count, total_count):
        """处理完成"""
        self.processing = False
        self.process_btn.config(text="🚀 开始处理", state='normal')
        self.progress.config(value=total_count)
        self.status_label.config(text=f"完成: {success_count}/{total_count}")
        
        if success_count > 0:
            message = f"成功处理 {success_count} 张图片"
            if success_count < total_count:
                message += f"，{total_count - success_count} 张失败"
            messagebox.showinfo("处理完成", message)
        else:
            messagebox.showerror("处理失败", "没有成功处理任何图片")
            
        if success_count > 0:
            message = f"成功处理 {success_count} 张图片"
            if success_count < total_count:
                message += f"，{total_count - success_count} 张失败"
            messagebox.showinfo("处理完成", message)
        else:
            messagebox.showerror("处理失败", "没有成功处理任何图片")
            
    def _on_format_change(self, event=None):
        """输出格式改变事件"""
        format_type = self.watermark_config['output_format'].get()
        if format_type == "JPEG":
            self.quality_label.config(state="normal")
            self.quality_scale.config(state="normal")
            self.quality_value_label.config(state="normal")
        else:
            self.quality_label.config(state="disabled")
            self.quality_scale.config(state="disabled")
            self.quality_value_label.config(state="disabled")
    
    def _on_quality_change(self, event=None):
        """JPEG质量改变事件"""
        quality = int(self.watermark_config['jpeg_quality'].get())
        self.quality_value_label.config(text=str(quality))
    
    def on_closing(self):
        """关闭事件"""
        if self.processing:
            if not messagebox.askyesno("确认", "正在处理图片，确定要退出吗？"):
                return
                
        self.root.destroy()
        
    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = ModernPhotoWatermarkGUI()
        app.run()
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        messagebox.showerror("启动失败", f"应用启动失败: {e}")


if __name__ == '__main__':
    main()