# PhotoWatermark 兼容性信息

## 构建环境
- 操作系统: Darwin 26.0
- 架构: arm64
- Python版本: 3.11.13
- 构建时间: 2025-09-24 23:20:36

## 可执行文件说明

### photo-watermark-compatible
- **用途**: 命令行版本，适用于批量处理和脚本自动化
- **架构**: 原生架构 (当前系统: arm64)
- **兼容性**: macOS 10.13+ (High Sierra及以上版本)
- **使用方法**: 
  ```bash
  ./photo-watermark-compatible input.jpg -o output.jpg --text "我的水印"
  ./photo-watermark-compatible --help  # 查看完整帮助
  ```

### watermark-interactive
- **用途**: 交互式命令行界面，提供菜单式操作
- **架构**: 原生架构 (当前系统: arm64)
- **兼容性**: macOS 10.13+ (High Sierra及以上版本)
- **特点**: 无GUI依赖，完全兼容所有macOS版本
- **使用方法**: 
  ```bash
  ./watermark-interactive
  ```

### template-manager-compatible
- **用途**: 模板管理工具
- **架构**: 原生架构 (当前系统: arm64)
- **兼容性**: macOS 10.13+ (High Sierra及以上版本)
- **使用方法**: 
  ```bash
  ./template-manager-compatible list
  ./template-manager-compatible save "模板名" --font-size 30
  ```

## 推荐使用方式

1. **新用户推荐**: 使用 `watermark-interactive` - 提供友好的交互式界面
2. **批量处理**: 使用 `photo-watermark-compatible` - 支持命令行参数和脚本自动化
3. **模板管理**: 使用 `template-manager-compatible` - 管理和创建水印模板

## 兼容性保证

这些可执行文件针对当前系统架构(arm64)进行了优化，确保在以下环境中正常运行：
- 当前架构的Mac系统
- macOS 10.13 High Sierra 及以上版本
- 无GUI依赖，避免了CustomTkinter和Tkinter的兼容性问题

## 故障排除

如果遇到"无法打开应用程序"的错误：
1. 右键点击可执行文件，选择"打开"
2. 或在终端中运行: `xattr -d com.apple.quarantine ./可执行文件名`

更多详细信息请参考 README.md 和 GUI_COMPATIBILITY.md 文件。
