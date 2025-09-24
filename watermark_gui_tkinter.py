#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhotoWatermark GUI - 标准Tkinter版本
解决macOS兼容性问题的GUI界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os
import sys
from pathlib import Path
from photo_watermark import PhotoWatermark
from template_manager import TemplateManager

class PhotoWatermarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoWatermark - 图片水印工具")
        self.root.geometry("800x600")
        
        # 初始化变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.text_watermark = tk.StringVar(value="2024-01-15")
        self.image_watermark_path = tk.StringVar()
        self.font_size = tk.IntVar(value=30)
        self.opacity = tk.IntVar(value=80)
        self.quality = tk.IntVar(value=95)
        self.position = tk.StringVar(value="bottom-right")
        self.color = tk.StringVar(value="white")
        self.output_format = tk.StringVar(value="JPEG")
        self.selected_template = tk.StringVar()
        
        # 初始化模板管理器
        self.template_manager = TemplateManager()
        
        self.create_widgets()
        self.load_templates()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="5")
        file_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="输入文件/目录:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(file_frame, textvariable=self.input_path).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        ttk.Label(file_frame, text="输出路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_path).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(file_frame, text="浏览", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        row += 1
        
        # 模板选择区域
        template_frame = ttk.LabelFrame(main_frame, text="模板管理", padding="5")
        template_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        template_frame.columnconfigure(1, weight=1)
        
        ttk.Label(template_frame, text="选择模板:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.selected_template, state="readonly")
        self.template_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
        ttk.Button(template_frame, text="刷新模板", command=self.load_templates).grid(row=0, column=2, padx=5)
        
        row += 1
        
        # 水印设置区域
        watermark_frame = ttk.LabelFrame(main_frame, text="水印设置", padding="5")
        watermark_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        watermark_frame.columnconfigure(1, weight=1)
        
        # 文本水印
        ttk.Label(watermark_frame, text="文本水印:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(watermark_frame, textvariable=self.text_watermark).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 图片水印
        ttk.Label(watermark_frame, text="图片水印:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(watermark_frame, textvariable=self.image_watermark_path).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(watermark_frame, text="选择图片", command=self.browse_image_watermark).grid(row=1, column=2, padx=5, pady=5)
        
        row += 1
        
        # 参数设置区域
        params_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="5")
        params_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(3, weight=1)
        
        # 第一行参数
        ttk.Label(params_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Scale(params_frame, from_=10, to=100, variable=self.font_size, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Label(params_frame, textvariable=self.font_size).grid(row=0, column=2, padx=5)
        
        ttk.Label(params_frame, text="透明度:").grid(row=0, column=3, sticky=tk.W, padx=5)
        ttk.Scale(params_frame, from_=0, to=100, variable=self.opacity, orient=tk.HORIZONTAL).grid(row=0, column=4, sticky=(tk.W, tk.E), padx=5)
        ttk.Label(params_frame, textvariable=self.opacity).grid(row=0, column=5, padx=5)
        
        # 第二行参数
        ttk.Label(params_frame, text="位置:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        position_combo = ttk.Combobox(params_frame, textvariable=self.position, state="readonly")
        position_combo['values'] = ('top-left', 'top-center', 'top-right', 
                                   'center-left', 'center', 'center-right',
                                   'bottom-left', 'bottom-center', 'bottom-right')
        position_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(params_frame, text="颜色:").grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        color_frame = ttk.Frame(params_frame)
        color_frame.grid(row=1, column=4, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Entry(color_frame, textvariable=self.color, width=10).pack(side=tk.LEFT)
        ttk.Button(color_frame, text="选择", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        
        # 第三行参数
        ttk.Label(params_frame, text="输出格式:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        format_combo = ttk.Combobox(params_frame, textvariable=self.output_format, state="readonly")
        format_combo['values'] = ('JPEG', 'PNG')
        format_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(params_frame, text="JPEG质量:").grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)
        ttk.Scale(params_frame, from_=1, to=100, variable=self.quality, orient=tk.HORIZONTAL).grid(row=2, column=4, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Label(params_frame, textvariable=self.quality).grid(row=2, column=5, padx=5, pady=5)
        
        row += 1
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="添加水印", command=self.add_watermark, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="保存为模板", command=self.save_template).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="清空设置", command=self.clear_settings).pack(side=tk.LEFT, padx=10)
        
        row += 1
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def browse_input(self):
        """浏览输入文件或目录"""
        path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.tiff *.bmp"), ("所有文件", "*.*")]
        )
        if not path:
            path = filedialog.askdirectory(title="选择图片目录")
        
        if path:
            self.input_path.set(path)
            
    def browse_output(self):
        """浏览输出路径"""
        if os.path.isdir(self.input_path.get()):
            # 输入是目录，输出也选择目录
            path = filedialog.askdirectory(title="选择输出目录")
        else:
            # 输入是文件，输出选择文件
            path = filedialog.asksaveasfilename(
                title="保存水印图片",
                defaultextension=".jpg",
                filetypes=[("JPEG文件", "*.jpg"), ("PNG文件", "*.png"), ("所有文件", "*.*")]
            )
        
        if path:
            self.output_path.set(path)
            
    def browse_image_watermark(self):
        """浏览图片水印文件"""
        path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg"), ("所有文件", "*.*")]
        )
        if path:
            self.image_watermark_path.set(path)
            
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(title="选择水印颜色")
        if color[1]:  # color[1] 是十六进制颜色值
            self.color.set(color[1])
            
    def load_templates(self):
        """加载模板列表"""
        try:
            templates = self.template_manager.list_templates()
            template_names = [""] + list(templates.keys())
            self.template_combo['values'] = template_names
            self.log("已加载 {} 个模板".format(len(templates)))
        except Exception as e:
            self.log(f"加载模板失败: {e}")
            
    def on_template_selected(self, event=None):
        """模板选择事件"""
        template_name = self.selected_template.get()
        if not template_name:
            return
            
        try:
            templates = self.template_manager.list_templates()
            if template_name in templates:
                template = templates[template_name]
                config = template.config
                
                # 应用模板设置
                self.font_size.set(config.get('font_size', 30))
                self.opacity.set(config.get('opacity', 80))
                self.position.set(config.get('position', 'bottom-right'))
                self.output_format.set(config.get('format', 'JPEG'))
                self.quality.set(config.get('quality', 95))
                
                # 处理颜色
                color = config.get('color', 'white')
                if isinstance(color, tuple) and len(color) == 3:
                    # RGB元组转换为十六进制
                    hex_color = "#{:02x}{:02x}{:02x}".format(*color)
                    self.color.set(hex_color)
                else:
                    self.color.set(str(color))
                
                self.log(f"已应用模板: {template_name}")
        except Exception as e:
            self.log(f"应用模板失败: {e}")
            
    def save_template(self):
        """保存当前设置为模板"""
        # 创建简单的输入对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("保存模板")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))
        
        ttk.Label(dialog, text="模板名称:").pack(pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=30).pack(pady=5)
        
        ttk.Label(dialog, text="模板描述:").pack(pady=10)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=30).pack(pady=5)
        
        def save_action():
            name = name_var.get().strip()
            desc = desc_var.get().strip()
            
            if not name:
                messagebox.showerror("错误", "请输入模板名称")
                return
                
            try:
                # 处理颜色
                color_value = self.color.get()
                if color_value.startswith('#'):
                    # 十六进制转RGB
                    hex_color = color_value.lstrip('#')
                    color_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                else:
                    color_rgb = color_value
                
                success = self.template_manager.save_template(
                    name=name,
                    font_size=self.font_size.get(),
                    color=color_rgb,
                    position=self.position.get(),
                    opacity=self.opacity.get(),
                    output_format=self.output_format.get(),
                    quality=self.quality.get(),
                    description=desc or f"用户自定义模板: {name}"
                )
                
                if success:
                    self.log(f"模板 '{name}' 保存成功")
                    self.load_templates()  # 刷新模板列表
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "保存模板失败")
            except Exception as e:
                messagebox.showerror("错误", f"保存模板失败: {e}")
                
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="保存", command=save_action).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
    def clear_settings(self):
        """清空设置"""
        self.input_path.set("")
        self.output_path.set("")
        self.text_watermark.set("2024-01-15")
        self.image_watermark_path.set("")
        self.font_size.set(30)
        self.opacity.set(80)
        self.quality.set(95)
        self.position.set("bottom-right")
        self.color.set("white")
        self.output_format.set("JPEG")
        self.selected_template.set("")
        self.log("设置已清空")
        
    def add_watermark(self):
        """添加水印"""
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入文件或目录")
            return
            
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出路径")
            return
            
        try:
            # 处理颜色
            color_value = self.color.get()
            if color_value.startswith('#'):
                # 十六进制转RGB
                hex_color = color_value.lstrip('#')
                color_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            else:
                color_rgb = color_value
            
            # 创建PhotoWatermark实例
            watermark = PhotoWatermark(
                font_size=self.font_size.get(),
                color=color_rgb,
                position=self.position.get(),
                opacity=self.opacity.get(),
                output_format=self.output_format.get(),
                quality=self.quality.get()
            )
            
            input_path = self.input_path.get()
            output_path = self.output_path.get()
            text = self.text_watermark.get() if self.text_watermark.get() else None
            image_watermark = self.image_watermark_path.get() if self.image_watermark_path.get() else None
            
            self.log(f"开始处理: {input_path}")
            
            if os.path.isdir(input_path):
                # 批量处理
                success_count, total_count = watermark.process_directory(
                    input_path, output_path, text, image_watermark
                )
                self.log(f"批量处理完成: {success_count}/{total_count} 个文件成功")
            else:
                # 单文件处理
                success = watermark.add_watermark(
                    input_path, output_path, text, image_watermark
                )
                if success:
                    self.log(f"水印添加成功: {output_path}")
                else:
                    self.log("水印添加失败")
                    
            messagebox.showinfo("完成", "水印处理完成！")
            
        except Exception as e:
            error_msg = f"处理失败: {e}"
            self.log(error_msg)
            messagebox.showerror("错误", error_msg)
            
    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')  # 使用现代主题
    
    app = PhotoWatermarkGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()