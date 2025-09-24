# PhotoWatermark - 图片水印工具

一个功能强大的图片水印添加工具，支持基于EXIF拍摄时间的自动水印、自定义文本水印、图片水印以及模板管理功能。

## 功能特性

- ✅ **自动时间水印**: 从图片EXIF信息中提取拍摄时间作为水印
- ✅ **自定义文本水印**: 支持自定义水印文本内容
- ✅ **图片水印**: 支持添加图片作为水印（如Logo）
- ✅ **模板管理**: 保存和管理常用的水印配置
- ✅ **批量处理**: 支持目录批量处理
- ✅ **多种格式**: 支持JPEG、PNG、TIFF、BMP格式
- ✅ **灵活配置**: 字体大小、颜色、位置、透明度等可调
- ✅ **命令行界面**: 完整的命令行操作支持

## 安装要求

- Python 3.7+
- Pillow (PIL)

```bash
pip install Pillow
```

## 使用方法

### 命令行使用

#### 基本用法

```bash
# 处理单个图片（使用EXIF时间）
python photo_watermark.py input.jpg -o output.jpg

# 处理目录（批量处理）
python photo_watermark.py /path/to/photos --output-dir /path/to/output

# 自定义水印文本
python photo_watermark.py input.jpg -o output.jpg --text "我的水印"
```

#### 高级配置

```bash
# 设置字体大小、颜色和位置
python photo_watermark.py input.jpg -o output.jpg \
    --font-size 40 --color red --position top-left

# 使用RGB颜色值
python photo_watermark.py input.jpg -o output.jpg \
    --color "255,128,0" --opacity 70

# 添加图片水印
python photo_watermark.py input.jpg -o output.jpg \
    --image-watermark logo.png --opacity 80

# 组合文本和图片水印
python photo_watermark.py input.jpg -o output.jpg \
    --text "2024-01-15" --image-watermark logo.png

# 指定输出格式
python photo_watermark.py input.jpg -o output.png \
    --format PNG --opacity 90
```

#### 模板使用

```bash
# 使用保存的模板
python photo_watermark.py input.jpg -o output.jpg --template "默认水印"

# 管理模板
python template_manager.py save "我的模板" \
    --font-size 35 --color blue --position center --opacity 85

python template_manager.py list
python template_manager.py delete "我的模板"
```

### 支持的参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `input` | 输入文件或目录 | - | `photo.jpg` |
| `-o, --output` | 输出文件或目录 | 自动生成 | `output.jpg` |
| `--text` | 自定义水印文本 | EXIF时间 | `"我的水印"` |
| `--image-watermark` | 水印图片路径 | - | `logo.png` |
| `--template` | 使用模板 | - | `"默认水印"` |
| `--font-size` | 字体大小 | 30 | `40` |
| `--color` | 字体颜色 | white | `red`, `"255,0,0"` |
| `--position` | 水印位置 | bottom-right | `top-left` |
| `--opacity` | 透明度(0-100) | 80 | `70` |
| `--format` | 输出格式 | JPEG | `PNG` |
| `--quality` | JPEG质量(1-100) | 95 | `85` |

### 支持的位置

```
top-left      top-center      top-right
center-left   center          center-right
bottom-left   bottom-center   bottom-right
```

### 支持的颜色

- **颜色名称**: white, black, red, green, blue, yellow, cyan, magenta, gray
- **RGB格式**: "255,255,255" (用逗号分隔的RGB值)

## 模板管理

### 保存模板

```bash
python template_manager.py save "模板名称" \
    --font-size 30 \
    --color white \
    --position bottom-right \
    --opacity 80 \
    --format JPEG \
    --description "模板描述"
```

### 管理模板

```bash
# 列出所有模板
python template_manager.py list

# 删除模板
python template_manager.py delete "模板名称"

# 导出模板
python template_manager.py export templates_backup.json

# 导入模板
python template_manager.py import templates_backup.json
```

## 文件结构

```
PhotoWatermark/
├── photo_watermark.py      # 主程序
├── template_manager.py     # 模板管理器
├── watermark_gui.py        # GUI界面（需要customtkinter）
├── watermark_gui_simple.py # 简化GUI界面
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
└── README.md              # 说明文档
```

## 示例

### 1. 基本水印添加

```bash
# 为单张图片添加基于EXIF时间的水印
python photo_watermark.py vacation.jpg -o vacation_watermarked.jpg
```

### 2. 批量处理

```bash
# 批量处理整个目录
python photo_watermark.py photos/ --output-dir watermarked_photos/
```

### 3. 自定义样式

```bash
# 红色大字体水印在顶部中央
python photo_watermark.py photo.jpg -o output.jpg \
    --text "版权所有" --font-size 50 --color red --position top-center
```

### 4. 添加Logo水印

```bash
# 在右下角添加半透明Logo
python photo_watermark.py photo.jpg -o output.jpg \
    --image-watermark company_logo.png --opacity 60 --position bottom-right
```

### 5. 使用模板

```bash
# 首先保存一个模板
python template_manager.py save "公司标准" \
    --font-size 25 --color "0,0,0" --position bottom-left --opacity 75

# 使用模板处理图片
python photo_watermark.py photo.jpg -o output.jpg --template "公司标准"
```

## 注意事项

1. **EXIF信息**: 如果图片没有EXIF拍摄时间信息，将使用文件修改时间
2. **字体支持**: 程序会自动寻找系统字体，如果找不到会使用默认字体
3. **透明度**: PNG格式支持完整透明度，JPEG格式会转换为RGB
4. **性能**: 批量处理大量图片时建议使用较低的JPEG质量以提高速度
5. **GUI兼容性**: 
   - CustomTkinter GUI在某些macOS版本上可能存在兼容性问题
   - 如遇到GUI启动问题，请使用命令行版本或标准Tkinter版本
   - 标准Tkinter版本: `python watermark_gui_tkinter.py`

## 故障排除

### 常见问题

1. **字体显示问题**: 确保系统有合适的字体文件
2. **EXIF读取失败**: 某些图片格式可能不包含EXIF信息
3. **内存不足**: 处理大图片时可能需要更多内存

### 错误代码

- 退出码 0: 成功
- 退出码 1: 处理失败或文件不存在
- 退出码 2: 参数错误

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 基本水印功能
- EXIF时间提取
- 命令行界面

### v1.1.0
- 添加图片水印支持
- 透明度控制
- 输出格式选择

### v1.2.0
- 模板管理功能
- 批量处理优化
- GUI界面（实验性）