# PhotoWatermark

一个基于EXIF拍摄时间的图片水印工具，可以自动为图片添加日期水印。

## 功能特性

- 🕒 **自动提取EXIF时间信息**：从图片的EXIF数据中读取拍摄时间
- 🎨 **自定义水印样式**：支持设置字体大小、颜色和位置
- 📍 **多种位置选择**：支持9个不同的水印位置
- 🎯 **批量处理**：一次处理整个目录中的所有图片
- 📁 **自动输出管理**：在原目录下创建 `_watermark` 子目录保存结果
- 🔧 **智能降级**：如果没有EXIF信息，自动使用文件修改时间

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python photo_watermark.py /path/to/your/photos
```

### 高级用法

```bash
# 设置字体大小为40，颜色为红色，位置在左上角
python photo_watermark.py /path/to/photos --font-size 40 --color red --position top-left

# 使用RGB颜色值
python photo_watermark.py /path/to/photos --color "255,0,0" --position center

# 显示详细输出
python photo_watermark.py /path/to/photos --verbose
```

## 命令行参数

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `directory` | - | 必需 | 包含图片的目录路径 |
| `--font-size` | `-s` | 30 | 字体大小 |
| `--color` | `-c` | white | 字体颜色 |
| `--position` | `-p` | bottom-right | 水印位置 |
| `--verbose` | `-v` | false | 显示详细输出 |

### 支持的水印位置

```
top-left      top-center      top-right
center-left   center          center-right
bottom-left   bottom-center   bottom-right
```

### 支持的颜色格式

**颜色名称：**
- `white`, `black`, `red`, `green`, `blue`
- `yellow`, `cyan`, `magenta`, `gray`

**RGB格式：**
- `"255,255,255"` (白色)
- `"255,0,0"` (红色)
- `"0,255,0"` (绿色)

## 支持的图片格式

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- TIFF (`.tiff`)
- BMP (`.bmp`)

## 输出说明

程序会在输入目录下创建一个名为 `原目录名_watermark` 的子目录，所有添加水印的图片都会保存在这个目录中，文件名保持不变。

例如：
```
/photos/
├── IMG_001.jpg
├── IMG_002.jpg
└── photos_watermark/
    ├── IMG_001.jpg  (带水印)
    └── IMG_002.jpg  (带水印)
```

## 使用示例

### 示例1：基本使用
```bash
python photo_watermark.py ~/Pictures/vacation
```

### 示例2：自定义样式
```bash
python photo_watermark.py ~/Pictures/vacation \
  --font-size 25 \
  --color "255,255,0" \
  --position top-right
```

### 示例3：查看详细输出
```bash
python photo_watermark.py ~/Pictures/vacation --verbose
```

## 注意事项

1. **EXIF信息**：如果图片没有EXIF拍摄时间信息，程序会使用文件的修改时间作为水印内容
2. **字体支持**：程序会尝试使用系统字体，如果找不到合适的字体会使用默认字体
3. **图片质量**：输出的JPEG图片质量设置为95%，保持高质量
4. **透明背景**：水印文字会添加半透明的黑色背景，提高可读性

## 错误处理

程序包含完善的错误处理机制：
- 自动跳过无法处理的文件
- 详细的错误日志输出
- 处理结果统计报告

## 许可证

请查看 LICENSE 文件了解许可证信息。
