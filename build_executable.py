#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行文件的脚本
使用PyInstaller将Python程序打包为独立的可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        print("请运行: pip install pyinstaller")
        return False

def build_cli_executable():
    """构建命令行版本的可执行文件"""
    print("\n🔨 构建命令行版本...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "photo-watermark",
        "--console",
        "--add-data", "templates.json:.",
        "photo_watermark.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 命令行版本构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令行版本构建失败: {e}")
        return False

def build_gui_executable():
    """构建GUI版本的可执行文件"""
    print("\n🔨 构建GUI版本...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "watermark-gui",
        "--windowed",
        "--add-data", "templates.json:.",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ GUI版本构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ GUI版本构建失败: {e}")
        return False

def build_template_manager_executable():
    """构建模板管理器的可执行文件"""
    print("\n🔨 构建模板管理器...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "template-manager",
        "--console",
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
    
    # 要删除的目录和文件
    to_remove = [
        "build",
        "__pycache__",
        "*.spec"
    ]
    
    for item in to_remove:
        if item.endswith("*.spec"):
            # 删除所有.spec文件
            for spec_file in Path(".").glob("*.spec"):
                try:
                    spec_file.unlink()
                    print(f"删除: {spec_file}")
                except Exception as e:
                    print(f"无法删除 {spec_file}: {e}")
        else:
            # 删除目录
            if os.path.exists(item):
                try:
                    shutil.rmtree(item)
                    print(f"删除目录: {item}")
                except Exception as e:
                    print(f"无法删除目录 {item}: {e}")

def create_distribution_package():
    """创建分发包"""
    print("\n📦 创建分发包...")
    
    dist_dir = Path("PhotoWatermark_Distribution")
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
    
    # 复制文档和配置文件
    files_to_copy = [
        "README.md",
        "requirements.txt",
        "templates.json"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"复制: {file_name}")
    
    # 创建使用说明
    usage_file = dist_dir / "使用说明.txt"
    with open(usage_file, "w", encoding="utf-8") as f:
        f.write("""PhotoWatermark 使用说明

可执行文件说明:
- photo-watermark: 命令行版本，用于批量处理和脚本自动化
- watermark-gui: 图形界面版本，提供可视化操作界面
- template-manager: 模板管理工具，用于管理水印模板

使用方法:
1. 命令行版本:
   ./photo-watermark input.jpg -o output.jpg --text "我的水印"
   
2. GUI版本:
   双击 watermark-gui 启动图形界面
   
3. 模板管理:
   ./template-manager list
   ./template-manager save "模板名" --font-size 30

更多详细说明请参考 README.md 文件。
""")
    
    print(f"✅ 分发包创建完成: {dist_dir}")

def main():
    """主函数"""
    print("🚀 PhotoWatermark 可执行文件构建工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        sys.exit(1)
    
    # 检查必要文件
    required_files = ["photo_watermark.py", "main.py", "template_manager.py"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        sys.exit(1)
    
    success_count = 0
    total_count = 3
    
    # 构建各个版本
    if build_cli_executable():
        success_count += 1
    
    if build_gui_executable():
        success_count += 1
    
    if build_template_manager_executable():
        success_count += 1
    
    # 创建分发包
    if success_count > 0:
        create_distribution_package()
    
    # 清理临时文件
    clean_build_files()
    
    # 总结
    print("\n" + "=" * 50)
    print(f"📊 构建完成: {success_count}/{total_count} 个可执行文件成功")
    
    if success_count == total_count:
        print("🎉 所有可执行文件构建成功！")
        print("📁 可执行文件位于 PhotoWatermark_Distribution 目录")
    elif success_count > 0:
        print("⚠️  部分可执行文件构建成功")
    else:
        print("❌ 所有构建都失败了")
        sys.exit(1)

if __name__ == "__main__":
    main()