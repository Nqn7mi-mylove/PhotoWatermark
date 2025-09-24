#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建现代化GUI可执行文件脚本
使用PyInstaller将现代化GUI打包为独立可执行文件
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_system_info():
    """获取系统信息"""
    return {
        'system': platform.system(),
        'machine': platform.machine(),
        'python_version': platform.python_version()
    }


def install_dependencies():
    """安装构建依赖"""
    logger.info("安装构建依赖...")
    
    dependencies = [
        'pyinstaller',
        'tkinterdnd2',
        'Pillow'
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True, text=True)
            logger.info(f"✅ {dep} 安装成功")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {dep} 安装失败: {e}")
            return False
    
    return True


def build_executable():
    """构建可执行文件"""
    logger.info("开始构建现代化GUI可执行文件...")
    
    # 获取系统信息
    system_info = get_system_info()
    logger.info(f"系统信息: {system_info}")
    
    # 构建参数
    build_args = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',  # 单文件模式
        '--windowed',  # 无控制台窗口
        '--name', 'watermark-gui-modern',
        '--add-data', 'templates.json:.',
        '--hidden-import', 'tkinterdnd2',
        '--hidden-import', 'PIL._tkinter_finder',
        'watermark_gui_modern.py'
    ]
    
    # 添加图标（如果存在）
    if os.path.exists('icon.ico'):
        build_args.extend(['--icon', 'icon.ico'])
    
    try:
        # 清理之前的构建
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        if os.path.exists('watermark-gui-modern.spec'):
            os.remove('watermark-gui-modern.spec')
            
        # 执行构建
        result = subprocess.run(build_args, check=True, capture_output=True, text=True)
        logger.info("✅ 构建成功")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 构建失败: {e}")
        logger.error(f"错误输出: {e.stderr}")
        return False


def create_release_package():
    """创建发布包"""
    logger.info("创建发布包...")
    
    system_info = get_system_info()
    package_name = f"PhotoWatermark_Modern_GUI_{system_info['machine']}"
    
    # 创建发布目录
    release_dir = Path(package_name)
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    try:
        # 复制可执行文件
        exe_name = 'watermark-gui-modern.exe' if system_info['system'] == 'Windows' else 'watermark-gui-modern'
        exe_path = Path('dist') / exe_name
        
        if exe_path.exists():
            shutil.copy2(exe_path, release_dir / exe_name)
            logger.info(f"✅ 复制可执行文件: {exe_name}")
        else:
            logger.error(f"❌ 可执行文件不存在: {exe_path}")
            return False
        
        # 复制必要文件
        files_to_copy = [
            'templates.json',
            'requirements.txt',
            'README.md'
        ]
        
        for file_name in files_to_copy:
            if os.path.exists(file_name):
                shutil.copy2(file_name, release_dir / file_name)
                logger.info(f"✅ 复制文件: {file_name}")
        
        # 复制测试图片目录
        if os.path.exists('test_images'):
            shutil.copytree('test_images', release_dir / 'test_images')
            logger.info("✅ 复制测试图片目录")
        
        # 创建使用说明
        create_usage_guide(release_dir, system_info)
        
        # 创建启动脚本
        create_launch_script(release_dir, exe_name, system_info)
        
        logger.info(f"✅ 发布包创建完成: {package_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建发布包失败: {e}")
        return False


def create_usage_guide(release_dir, system_info):
    """创建使用说明"""
    guide_content = f"""# PhotoWatermark 现代化GUI版本使用说明

## 版本信息
- 版本: 现代化GUI版本 v1.0
- 构建时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 系统架构: {system_info['machine']}
- Python版本: {system_info['python_version']}

## 功能特性

### 🎯 拖拽导入
- 支持将图片文件直接拖拽到应用窗口
- 支持将整个文件夹拖拽导入所有图片
- 自动识别支持的图片格式 (JPG, PNG, BMP, TIFF)

### 📁 文件选择器
- 点击"选择文件"按钮选择单个或多个图片
- 点击"选择文件夹"按钮导入整个文件夹的图片
- 支持批量选择和处理

### ⚙️ 水印设置
- **文本水印**: 自定义文字、字体、大小、颜色、透明度
- **图片水印**: 支持PNG/JPG水印图片，可调整缩放和透明度
- **位置设置**: 9个预设位置 + 自定义偏移
- **高级选项**: 支持旋转角度设置

### 📋 模板管理
- 保存常用水印设置为模板
- 快速加载和应用已保存的模板
- 支持模板的导入导出

### 🖼️ 实时预览
- 实时预览水印效果
- 支持在图片列表中切换预览
- 所见即所得的编辑体验

## 使用方法

### 1. 导入图片
- **拖拽方式**: 直接将图片文件或文件夹拖拽到"拖拽区域"
- **按钮方式**: 点击"选择文件"或"选择文件夹"按钮

### 2. 设置水印
- 在右侧设置面板中配置水印参数
- 可以同时使用文本水印和图片水印
- 实时预览效果

### 3. 处理图片
- 设置输出目录
- 点击"开始处理"按钮
- 等待处理完成

### 4. 模板管理
- 在"模板管理"选项卡中保存常用设置
- 下次使用时直接加载模板

## 系统要求
- macOS 10.13 或更高版本
- 至少 100MB 可用磁盘空间
- 支持拖拽操作的桌面环境

## 技术特性
- 原生架构优化 ({system_info['machine']})
- 无需安装Python环境
- 独立可执行文件
- 现代化用户界面

## 故障排除

### 应用无法启动
1. 检查系统版本是否满足要求
2. 确保有足够的磁盘空间
3. 尝试以管理员权限运行

### 拖拽功能不工作
1. 确保文件格式受支持
2. 尝试使用文件选择器作为替代方案
3. 检查文件权限

### 处理失败
1. 检查输出目录权限
2. 确保输入图片文件完整
3. 查看错误信息提示

## 支持的文件格式
- **输入**: JPG, JPEG, PNG, BMP, TIFF
- **输出**: JPG (高质量)
- **水印图片**: PNG, JPG, JPEG, BMP, TIFF

## 联系支持
如遇到问题，请检查日志文件或联系技术支持。

---
PhotoWatermark 现代化GUI版本 - 让水印添加更简单！
"""
    
    with open(release_dir / 'USAGE_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)


def create_launch_script(release_dir, exe_name, system_info):
    """创建启动脚本"""
    if system_info['system'] == 'Darwin':  # macOS
        script_content = f"""#!/bin/bash
# PhotoWatermark 现代化GUI启动脚本

# 获取脚本所在目录
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )"

# 切换到应用目录
cd "$DIR"

# 启动应用
echo "启动 PhotoWatermark 现代化GUI..."
./{exe_name}

# 检查退出状态
if [ $? -eq 0 ]; then
    echo "应用正常退出"
else
    echo "应用异常退出，请检查错误信息"
    read -p "按回车键继续..."
fi
"""
        script_path = release_dir / 'launch_modern_gui.sh'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
    elif system_info['system'] == 'Windows':
        script_content = f"""@echo off
REM PhotoWatermark 现代化GUI启动脚本

echo 启动 PhotoWatermark 现代化GUI...
{exe_name}

if %ERRORLEVEL% EQU 0 (
    echo 应用正常退出
) else (
    echo 应用异常退出，请检查错误信息
    pause
)
"""
        with open(release_dir / 'launch_modern_gui.bat', 'w', encoding='utf-8') as f:
            f.write(script_content)


def cleanup():
    """清理构建文件"""
    logger.info("清理构建文件...")
    
    cleanup_dirs = ['build', '__pycache__']
    cleanup_files = ['watermark-gui-modern.spec']
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            logger.info(f"✅ 清理目录: {dir_name}")
    
    for file_name in cleanup_files:
        if os.path.exists(file_name):
            os.remove(file_name)
            logger.info(f"✅ 清理文件: {file_name}")


def main():
    """主函数"""
    logger.info("=== PhotoWatermark 现代化GUI构建脚本 ===")
    
    try:
        # 检查必要文件
        if not os.path.exists('watermark_gui_modern.py'):
            logger.error("❌ 找不到 watermark_gui_modern.py 文件")
            return False
        
        # 安装依赖
        if not install_dependencies():
            logger.error("❌ 依赖安装失败")
            return False
        
        # 构建可执行文件
        if not build_executable():
            logger.error("❌ 构建失败")
            return False
        
        # 创建发布包
        if not create_release_package():
            logger.error("❌ 发布包创建失败")
            return False
        
        # 清理构建文件
        cleanup()
        
        logger.info("🎉 现代化GUI构建完成！")
        logger.info("📦 发布包已准备就绪，可以分发使用")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 构建过程中发生错误: {e}")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)