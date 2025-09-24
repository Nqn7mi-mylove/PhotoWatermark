# PhotoWatermark GUI 兼容性说明

## 问题描述

在某些macOS系统版本上，CustomTkinter GUI可能出现兼容性问题，表现为：
- 启动时出现 "macOS 26 (2600) or later required, have instead 16 (1600)" 错误
- GUI程序无法正常启动或崩溃

## 原因分析

这个问题主要由以下原因引起：
1. **CustomTkinter版本兼容性**: 新版本的CustomTkinter对macOS版本有更严格的要求
2. **系统版本检测**: CustomTkinter的版本检测机制可能与实际系统版本不匹配
3. **依赖库冲突**: 某些依赖库的版本可能与当前系统不兼容

## 解决方案

### 方案1: 使用标准Tkinter版本（推荐）

我们提供了基于标准Tkinter的GUI版本，具有更好的兼容性：

```bash
python watermark_gui_tkinter.py
```

**特点:**
- 使用Python内置的Tkinter库，兼容性更好
- 功能完整，包含所有核心功能
- 界面简洁，操作直观
- 支持模板管理和所有水印功能

### 方案2: 使用命令行版本

如果GUI仍有问题，可以使用功能完整的命令行版本：

```bash
# 基本用法
python photo_watermark.py input.jpg -o output.jpg --text "我的水印"

# 使用模板
python photo_watermark.py input.jpg --template "默认水印" -o output.jpg

# 批量处理
python photo_watermark.py input_dir/ --output-dir output_dir/ --text "批量水印"
```

### 方案3: 降级CustomTkinter版本

如果必须使用CustomTkinter GUI，可以尝试降级到兼容版本：

```bash
pip install customtkinter==4.6.3
```

然后运行：
```bash
python watermark_gui.py
```

### 方案4: 使用可执行文件

直接使用预编译的可执行文件（如果可用）：

```bash
# 在PhotoWatermark_Distribution目录中
./photo-watermark input.jpg -o output.jpg --text "我的水印"
```

## 功能对比

| 功能 | CustomTkinter GUI | 标准Tkinter GUI | 命令行版本 |
|------|------------------|-----------------|-----------|
| 基本水印功能 | ✅ | ✅ | ✅ |
| 模板管理 | ✅ | ✅ | ✅ |
| 批量处理 | ✅ | ✅ | ✅ |
| 图片水印 | ✅ | ✅ | ✅ |
| 实时预览 | ✅ | ❌ | ❌ |
| 现代UI | ✅ | ❌ | ❌ |
| 系统兼容性 | ⚠️ | ✅ | ✅ |

## 推荐使用方式

1. **日常使用**: 标准Tkinter GUI版本 (`watermark_gui_tkinter.py`)
2. **批量处理**: 命令行版本 (`photo_watermark.py`)
3. **模板管理**: 模板管理器 (`template_manager.py`)
4. **自动化脚本**: 命令行版本集成到脚本中

## 技术细节

### 系统版本检测问题

CustomTkinter使用以下方式检测macOS版本：
```python
import platform
version = platform.mac_ver()[0]
```

在某些环境中，这个检测可能不准确，导致版本检查失败。

### 依赖关系

- **CustomTkinter GUI**: 依赖 `customtkinter >= 5.0.0`
- **标准Tkinter GUI**: 仅依赖Python内置库
- **命令行版本**: 仅依赖 `Pillow >= 9.0.0`

## 报告问题

如果遇到其他兼容性问题，请提供以下信息：

1. 操作系统版本: `sw_vers` (macOS) 或 `uname -a` (Linux)
2. Python版本: `python --version`
3. 依赖库版本: `pip list | grep -E "(customtkinter|Pillow)"`
4. 错误信息的完整输出

## 更新日志

- **v1.2.0**: 添加标准Tkinter GUI版本，解决macOS兼容性问题
- **v1.1.0**: 识别CustomTkinter兼容性问题
- **v1.0.0**: 初始CustomTkinter GUI版本

---

**注意**: 我们建议优先使用标准Tkinter版本的GUI，它提供了良好的用户体验和最佳的系统兼容性。