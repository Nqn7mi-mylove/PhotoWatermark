# GUI兼容性说明

## 问题描述

在某些macOS系统上，CustomTkinter和标准Tkinter GUI可能会出现兼容性问题，显示错误信息：
```
macOS 26 (2600) or later required, have instead 16 (1600) !
```

## 问题分析

经过测试发现，即使系统版本显示为macOS 26.0，GUI库仍然报告版本检测错误。这可能是由于：

1. **CustomTkinter版本兼容性**: 不同版本的CustomTkinter对macOS的支持程度不同
2. **系统版本检测问题**: GUI库的版本检测机制可能存在问题
3. **依赖库冲突**: 底层Tkinter或其他依赖库的兼容性问题
4. **Python环境问题**: Python版本与GUI库的兼容性

## 解决方案

### 🎯 推荐方案：交互式命令行界面

我们提供了一个功能完整的交互式命令行界面作为GUI的替代方案：

```bash
python watermark_gui_no_display.py
```

**特点：**
- ✅ 完全兼容所有系统
- ✅ 功能与GUI版本完全一致
- ✅ 友好的交互式菜单
- ✅ 支持所有水印功能
- ✅ 模板管理功能
- ✅ 批量处理支持

### 其他解决方案

1. **使用命令行版本**
   ```bash
   python photo_watermark.py input.jpg -o output.jpg --text "我的水印"
   ```

2. **使用可执行文件**
   ```bash
   cd PhotoWatermark_Distribution
   ./photo-watermark input.jpg -o output.jpg --text "我的水印"
   ```

3. **尝试不同的CustomTkinter版本**
   ```bash
   pip install customtkinter==4.6.3
   ```

## 功能对比

| 功能 | GUI版本 | 交互式命令行 | 纯命令行 | 可执行文件 |
|------|---------|-------------|----------|------------|
| 文本水印 | ✅ | ✅ | ✅ | ✅ |
| 图片水印 | ✅ | ✅ | ✅ | ✅ |
| 模板管理 | ✅ | ✅ | ✅ | ✅ |
| 批量处理 | ✅ | ✅ | ✅ | ✅ |
| 实时预览 | ✅ | ❌ | ❌ | ❌ |
| 拖拽操作 | ✅ | ❌ | ❌ | ❌ |
| 系统兼容性 | ⚠️ | ✅ | ✅ | ✅ |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

## 推荐使用方式

1. **首选**: 交互式命令行界面 (`watermark_gui_no_display.py`)
2. **备选**: 纯命令行版本 (`photo_watermark.py`)
3. **分发**: 可执行文件版本 (PhotoWatermark_Distribution目录)

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