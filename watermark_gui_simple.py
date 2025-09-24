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


class WatermarkConfig:
    """水印配置类"""
    
    def __init__(self):
        # 文本水印设置
        self.text = "Sample Watermark"
        self.font_family = "Arial"
        self.font_size = 30
        self.bold = False
        self.italic = False
        self.color = (255, 255, 255)  # RGB
        self.opacity = 80  # 0-100
        self.shadow = True
        self.stroke = False
        self.stroke_color = (0, 0, 0)
        self.stroke_width = 2
        
        # 图片水印设置
        self.image_path = ""
        self.image_scale = 0.2  # 0.1-2.0
        self.image_opacity = 80  # 0-100
        
        # 位置设置
        self.position = "bottom-right"
        self.offset_x = 20
        self.offset_y = 20
        self.rotation = 0  # -180 to 180
        
        # 导出设置
        self.output_format = "JPEG"
        self.jpeg_quality = 95


class ImageItem:
    """图片项目类"""
    
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.thumbnail = None
        self.load_thumbnail()
    
    def load_thumbnail(self):
        """加载缩略图"""
        try:
            with Image.open(self.path) as img:
                img.thumbnail((100, 100))
                self.thumbnail = ImageTk.PhotoImage(img)
        except Exception as e:
            logger.error(f"Failed to load thumbnail for {self.path}: {e}")


class SimpleWatermarkGUI:
    """简化版水印GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Photo Watermark Tool")
        self.root.geometry("1000x700")
        
        # 配置
        self.config = WatermarkConfig()
        self.images: List[ImageItem] = []
        self.current_image_index = 0
        
        # 控制变量
        self.output_dir_var = tk.StringVar()
        self.text_var = tk.StringVar(value=self.config.text)
        self.font_size_var = tk.IntVar(value=self.config.font_size)
        self.opacity_var = tk.IntVar(value=self.config.opacity)
        self.position_var = tk.StringVar(value=self.config.position)
        
        # 创建界面
        self.create_widgets()
        self.bind_events()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 图片列表
        self.create_image_list(left_frame)
        
        # 预览区域
        self.create_preview_area(left_frame)
        
        # 右侧设置面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.create_settings_panel(right_frame)
    
    def create_image_list(self, parent):
        """创建图片列表"""
        # 按钮框架
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="导入图片", command=self.import_images).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="导入文件夹", command=self.import_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="清空列表", command=self.clear_images).pack(side=tk.LEFT)
        
        # 图片列表
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_listbox = tk.Listbox(list_frame, height=8)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=scrollbar.set)
        
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
    
    def create_preview_area(self, parent):
        """创建预览区域"""
        preview_frame = ttk.LabelFrame(parent, text="预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.preview_canvas = tk.Canvas(preview_frame, bg='white', width=400, height=300)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_settings_panel(self, parent):
        """创建设置面板"""
        settings_frame = ttk.LabelFrame(parent, text="水印设置")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文本设置
        text_frame = ttk.LabelFrame(settings_frame, text="文本水印")
        text_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(text_frame, text="文本内容:").pack(anchor=tk.W)
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var)
        text_entry.pack(fill=tk.X, pady=(0, 5))
        text_entry.bind('<KeyRelease>', self.on_text_change)
        
        ttk.Label(text_frame, text="字体大小:").pack(anchor=tk.W)
        font_scale = ttk.Scale(text_frame, from_=10, to=100, variable=self.font_size_var, 
                              orient=tk.HORIZONTAL, command=self.on_font_size_change)
        font_scale.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(text_frame, text="透明度:").pack(anchor=tk.W)
        opacity_scale = ttk.Scale(text_frame, from_=0, to=100, variable=self.opacity_var,
                                 orient=tk.HORIZONTAL, command=self.on_opacity_change)
        opacity_scale.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(text_frame, text="选择颜色", command=self.select_color).pack(pady=5)
        
        # 位置设置
        pos_frame = ttk.LabelFrame(settings_frame, text="位置设置")
        pos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        positions = [
            ("左上", "top-left"), ("上中", "top-center"), ("右上", "top-right"),
            ("左中", "center-left"), ("中心", "center"), ("右中", "center-right"),
            ("左下", "bottom-left"), ("下中", "bottom-center"), ("右下", "bottom-right")
        ]
        
        for i, (text, value) in enumerate(positions):
            row, col = divmod(i, 3)
            ttk.Radiobutton(pos_frame, text=text, variable=self.position_var, 
                           value=value, command=self.on_position_change).grid(row=row, column=col, sticky=tk.W)
        
        # 导出设置
        export_frame = ttk.LabelFrame(settings_frame, text="导出设置")
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(export_frame, text="输出目录:").pack(anchor=tk.W)
        dir_frame = ttk.Frame(export_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="选择", command=self.select_output_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(export_frame, text="导出所有图片", command=self.export_images).pack(pady=10)
    
    def bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def import_images(self):
        """导入图片"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("所有文件", "*.*")
            ]
        )
        
        for file_path in files:
            self.add_image(file_path)
        
        self.update_image_list()
    
    def import_folder(self):
        """导入文件夹"""
        folder = filedialog.askdirectory(title="选择包含图片的文件夹")
        if folder:
            self.add_images_from_directory(folder)
            self.update_image_list()
    
    def add_image(self, file_path: str):
        """添加单个图片"""
        try:
            # 检查是否为支持的图片格式
            with Image.open(file_path) as img:
                pass  # 只是验证能否打开
            
            # 检查是否已存在
            if not any(item.path == file_path for item in self.images):
                image_item = ImageItem(file_path)
                self.images.append(image_item)
                logger.info(f"Added image: {file_path}")
        except Exception as e:
            logger.error(f"Failed to add image {file_path}: {e}")
    
    def add_images_from_directory(self, dir_path: str):
        """从目录添加图片"""
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        for file_path in Path(dir_path).rglob('*'):
            if file_path.suffix.lower() in supported_formats:
                self.add_image(str(file_path))
    
    def clear_images(self):
        """清空图片列表"""
        self.images.clear()
        self.current_image_index = 0
        self.update_image_list()
        self.preview_canvas.delete("all")
    
    def update_image_list(self):
        """更新图片列表显示"""
        self.image_listbox.delete(0, tk.END)
        for item in self.images:
            self.image_listbox.insert(tk.END, item.name)
        
        if self.images and self.current_image_index < len(self.images):
            self.image_listbox.selection_set(self.current_image_index)
            self.update_preview()
    
    def on_image_select(self, event):
        """图片选择事件"""
        selection = self.image_listbox.curselection()
        if selection:
            self.current_image_index = selection[0]
            self.update_preview()
    
    def update_preview(self):
        """更新预览"""
        if not self.images or self.current_image_index >= len(self.images):
            return
        
        try:
            image_item = self.images[self.current_image_index]
            
            # 加载原图
            with Image.open(image_item.path) as img:
                # 添加水印
                watermarked = self.add_watermark(img.copy())
                
                # 调整预览尺寸
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    watermarked.thumbnail((canvas_width - 20, canvas_height - 20))
                    
                    # 显示预览
                    photo = ImageTk.PhotoImage(watermarked)
                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_image(
                        canvas_width // 2, canvas_height // 2,
                        image=photo, anchor=tk.CENTER
                    )
                    self.preview_canvas.image = photo  # 保持引用
        except Exception as e:
            logger.error(f"Failed to update preview: {e}")
    
    def add_watermark(self, img: Image.Image) -> Image.Image:
        """添加水印"""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 创建透明图层
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 加载字体
        try:
            font = ImageFont.truetype("Arial.ttf", self.config.font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), self.config.text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        x, y = self.calculate_position(img.size, (text_width, text_height))
        
        # 设置颜色和透明度
        alpha = int(255 * self.config.opacity / 100)
        color = (*self.config.color, alpha)
        
        # 绘制阴影
        if self.config.shadow:
            shadow_color = (0, 0, 0, alpha // 2)
            draw.text((x + 2, y + 2), self.config.text, font=font, fill=shadow_color)
        
        # 绘制主文本
        draw.text((x, y), self.config.text, font=font, fill=color)
        
        # 合并图层
        result = Image.alpha_composite(img, overlay)
        return result.convert('RGB')
    
    def calculate_position(self, img_size: Tuple[int, int], text_size: Tuple[int, int]) -> Tuple[int, int]:
        """计算水印位置"""
        img_width, img_height = img_size
        text_width, text_height = text_size
        
        position_map = {
            'top-left': (20, 20),
            'top-center': ((img_width - text_width) // 2, 20),
            'top-right': (img_width - text_width - 20, 20),
            'center-left': (20, (img_height - text_height) // 2),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
            'center-right': (img_width - text_width - 20, (img_height - text_height) // 2),
            'bottom-left': (20, img_height - text_height - 20),
            'bottom-center': ((img_width - text_width) // 2, img_height - text_height - 20),
            'bottom-right': (img_width - text_width - 20, img_height - text_height - 20)
        }
        
        return position_map.get(self.config.position, position_map['bottom-right'])
    
    def on_text_change(self, event=None):
        """文本变化事件"""
        self.config.text = self.text_var.get()
        self.update_preview()
    
    def on_font_size_change(self, value=None):
        """字体大小变化事件"""
        self.config.font_size = self.font_size_var.get()
        self.update_preview()
    
    def on_opacity_change(self, value=None):
        """透明度变化事件"""
        self.config.opacity = self.opacity_var.get()
        self.update_preview()
    
    def on_position_change(self):
        """位置变化事件"""
        self.config.position = self.position_var.get()
        self.update_preview()
    
    def select_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(title="选择文字颜色")
        if color[0]:
            self.config.color = tuple(int(c) for c in color[0])
            self.update_preview()
    
    def select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def export_images(self):
        """导出图片"""
        if not self.images:
            messagebox.showwarning("警告", "请先导入图片")
            return
        
        if not self.output_dir_var.get():
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        # 在新线程中执行导出
        threading.Thread(target=self._export_thread, daemon=True).start()
    
    def _export_thread(self):
        """导出线程"""
        output_dir = Path(self.output_dir_var.get())
        success_count = 0
        
        for i, image_item in enumerate(self.images):
            try:
                with Image.open(image_item.path) as img:
                    # 添加水印
                    watermarked = self.add_watermark(img.copy())
                    
                    # 生成输出文件名
                    output_name = f"watermark_{image_item.name}"
                    output_path = output_dir / output_name
                    
                    # 保存图片
                    if self.config.output_format == "JPEG":
                        watermarked.save(output_path, "JPEG", quality=self.config.jpeg_quality)
                    else:
                        watermarked.save(output_path, "PNG")
                    
                    success_count += 1
                    logger.info(f"Exported: {output_path}")
                    
            except Exception as e:
                logger.error(f"Failed to export {image_item.path}: {e}")
        
        # 显示完成消息
        self.root.after(0, lambda: messagebox.showinfo(
            "导出完成", f"成功导出 {success_count}/{len(self.images)} 张图片"
        ))
    
    def on_closing(self):
        """关闭事件"""
        self.root.destroy()
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    app = SimpleWatermarkGUI()
    app.run()


if __name__ == '__main__':
    main()