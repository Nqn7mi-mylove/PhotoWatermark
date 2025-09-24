#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建兼容性更好的macOS可执行文件
针对不同macOS版本和架构进行优化
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

def get_system_info():
    """获取系统信息"""
    system_info = {
        'platform': platform.system(),
        'machine': platform.machine(),
        'version': platform.mac_ver()[0] if platform.system() == 'Darwin' else None,
        'python_version': platform.python_version()
    }
    return system_info

def check_dependencies():
    """检查必要的依赖"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装，版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller未安装")
        print("请运行: pip install pyinstaller")
        return False
    
    # 检查必要文件
    required_files = [
        "photo_watermark.py",
        "watermark_gui_no_display.py",
        "template_manager.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    return True

def build_cli_executable():
    """构建命令行版本的可执行文件（兼容性优化）"""
    print("\n🔨 构建兼容性优化的命令行版本...")
    
    # 基础命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "photo-watermark-compatible",
        "--console",
        "--clean",
        # 兼容性优化选项
        "--osx-bundle-identifier", "com.photowatermark.cli",
        # 数据文件
        "--add-data", "templates.json:.",
        # 隐藏导入（确保所有依赖都被包含）
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "PIL.ImageFont",
        "--hidden-import", "PIL.ImageEnhance",
        "--hidden-import", "customtkinter",
        "--hidden-import", "tkinter",
        # 主文件
        "photo_watermark.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 兼容性优化的命令行版本构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令行版本构建失败: {e}")
        return False

def build_interactive_cli_executable():
    """构建交互式命令行版本的可执行文件"""
    print("\n🔨 构建交互式命令行版本...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "watermark-interactive",
        "--console",
        "--clean",
        # 兼容性优化选项
        "--osx-bundle-identifier", "com.photowatermark.interactive",
        # 数据文件
        "--add-data", "templates.json:.",
        # 隐藏导入
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "PIL.ImageFont",
        "--hidden-import", "PIL.ImageEnhance",
        # 主文件
        "watermark_gui_no_display.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 交互式命令行版本构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 交互式命令行版本构建失败: {e}")
        return False

def build_template_manager_executable():
    """构建模板管理器的可执行文件"""
    print("\n🔨 构建模板管理器...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "template-manager-compatible",
        "--console",
        "--clean",
        # 兼容性优化选项
        "--osx-bundle-identifier", "com.photowatermark.template",
        # 隐藏导入
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "PIL.ImageFont",
        # 主文件
        "template_manager.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 模板管理器构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 模板管理器构建失败: {e}")
        return False

def clean_build_files():
    """清理构建过程中产生的临时文件"""
    print("\n🧹 清理临时文件...")
    
    to_remove = [
        "build",
        "__pycache__",
        "*.spec"
    ]
    
    for item in to_remove:
        if item.endswith("*.spec"):
            for spec_file in Path(".").glob("*.spec"):
                try:
                    spec_file.unlink()
                    print(f"删除: {spec_file}")
                except Exception as e:
                    print(f"无法删除 {spec_file}: {e}")
        else:
            if os.path.exists(item):
                try:
                    shutil.rmtree(item)
                    print(f"删除目录: {item}")
                except Exception as e:
                    print(f"无法删除目录 {item}: {e}")

def create_compatible_distribution():
    """创建兼容性优化的分发包"""
    print("\n📦 创建兼容性优化的分发包...")
    
    dist_dir = Path("PhotoWatermark_Compatible_Release")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # 复制可执行文件
    dist_path = Path("dist")
    if dist_path.exists():
        for exe_file in dist_path.glob("*"):
            if exe_file.is_file():
                shutil.copy2(exe_file, dist_dir)
                print(f"复制: {exe_file.name}")
    
    # 复制必要文件
    files_to_copy = [
        "README.md",
        "requirements.txt",
        "templates.json",
        "GUI_COMPATIBILITY.md"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"复制: {file_name}")
    
    # 复制测试图片
    test_images_dir = Path("test_images")
    if test_images_dir.exists():
        dest_test_dir = dist_dir / "test_images"
        shutil.copytree(test_images_dir, dest_test_dir)
        print("复制: test_images/")
    
    # 创建兼容性说明文件
    compatibility_file = dist_dir / "COMPATIBILITY_INFO.md"
    system_info = get_system_info()
    
    with open(compatibility_file, "w", encoding="utf-8") as f:
        f.write(f"""# PhotoWatermark 兼容性信息

## 构建环境
- 操作系统: {system_info['platform']} {system_info['version']}
- 架构: {system_info['machine']}
- Python版本: {system_info['python_version']}
- 构建时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 可执行文件说明

### photo-watermark-compatible
- **用途**: 命令行版本，适用于批量处理和脚本自动化
- **架构**: 原生架构 (当前系统: {system_info['machine']})
- **兼容性**: macOS 10.13+ (High Sierra及以上版本)
- **使用方法**: 
  ```bash
  ./photo-watermark-compatible input.jpg -o output.jpg --text "我的水印"
  ./photo-watermark-compatible --help  # 查看完整帮助
  ```

### watermark-interactive
- **用途**: 交互式命令行界面，提供菜单式操作
- **架构**: 原生架构 (当前系统: {system_info['machine']})
- **兼容性**: macOS 10.13+ (High Sierra及以上版本)
- **特点**: 无GUI依赖，完全兼容所有macOS版本
- **使用方法**: 
  ```bash
  ./watermark-interactive
  ```

### template-manager-compatible
- **用途**: 模板管理工具
- **架构**: 原生架构 (当前系统: {system_info['machine']})
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

这些可执行文件针对当前系统架构({system_info['machine']})进行了优化，确保在以下环境中正常运行：
- 当前架构的Mac系统
- macOS 10.13 High Sierra 及以上版本
- 无GUI依赖，避免了CustomTkinter和Tkinter的兼容性问题

## 故障排除

如果遇到"无法打开应用程序"的错误：
1. 右键点击可执行文件，选择"打开"
2. 或在终端中运行: `xattr -d com.apple.quarantine ./可执行文件名`

更多详细信息请参考 README.md 和 GUI_COMPATIBILITY.md 文件。
""")
    
    # 创建启动脚本
    launch_script = dist_dir / "launch_interactive.sh"
    with open(launch_script, "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
# PhotoWatermark 交互式启动脚本

echo "🚀 启动 PhotoWatermark 交互式界面..."
echo "如果这是第一次运行，系统可能会要求安全确认。"
echo ""

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 运行交互式程序
"$DIR/watermark-interactive"
""")
    
    # 设置脚本可执行权限
    os.chmod(launch_script, 0o755)
    
    print(f"✅ 兼容性优化的分发包创建完成: {dist_dir}")
    return dist_dir

def main():
    """主函数"""
    print("🚀 PhotoWatermark 兼容性优化构建工具")
    print("=" * 60)
    
    # 显示系统信息
    system_info = get_system_info()
    print(f"📱 系统信息:")
    print(f"   操作系统: {system_info['platform']} {system_info['version']}")
    print(f"   架构: {system_info['machine']}")
    print(f"   Python版本: {system_info['python_version']}")
    print()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    success_count = 0
    total_count = 3
    
    # 构建各个版本
    print("🔧 开始构建兼容性优化的可执行文件...")
    
    if build_cli_executable():
        success_count += 1
    
    if build_interactive_cli_executable():
        success_count += 1
    
    if build_template_manager_executable():
        success_count += 1
    
    # 创建分发包
    if success_count > 0:
        dist_dir = create_compatible_distribution()
    
    # 清理临时文件
    clean_build_files()
    
    # 总结
    print("\n" + "=" * 60)
    print(f"📊 构建完成: {success_count}/{total_count} 个可执行文件成功")
    
    if success_count == total_count:
        print("🎉 所有兼容性优化的可执行文件构建成功！")
        print(f"📁 可执行文件位于 {dist_dir} 目录")
        print("\n💡 使用建议:")
        print("   - 新用户: 运行 ./launch_interactive.sh 或 ./watermark-interactive")
        print("   - 批量处理: 使用 ./photo-watermark-compatible")
        print("   - 模板管理: 使用 ./template-manager-compatible")
        print("\n📖 详细信息请查看 COMPATIBILITY_INFO.md 文件")
    elif success_count > 0:
        print("⚠️  部分可执行文件构建成功")
        print(f"📁 已构建的文件位于 {dist_dir} 目录")
    else:
        print("❌ 所有构建都失败了")
        sys.exit(1)

if __name__ == "__main__":
    main()