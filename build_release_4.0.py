#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhotoWatermark 4.0 Release Builder
专用于构建PhotoWatermark 4.0版本的打包脚本
"""

import os
import sys
import shutil
import subprocess
import platform
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 版本信息
VERSION = "4.0.0"
RELEASE_DATE = "2025-01-25"
APP_NAME = "PhotoWatermark"

def get_system_info():
    """获取系统信息"""
    return {
        'system': platform.system(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'platform': platform.platform()
    }

def check_dependencies():
    """检查并安装构建依赖"""
    logger.info("检查构建依赖...")
    
    dependencies = [
        'pyinstaller>=5.0',
        'tkinterdnd2>=0.3.0',
        'Pillow>=9.0.0'
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True, text=True)
            logger.info(f"✅ {dep} 已安装/更新")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {dep} 安装失败: {e}")
            return False
    
    return True

def clean_build_dirs():
    """清理构建目录"""
    logger.info("清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            logger.info(f"✅ 清理目录: {dir_name}")

def create_spec_file():
    """创建PyInstaller spec文件"""
    logger.info("创建PyInstaller spec文件...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['watermark_gui_modern.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates.json', '.'),
        ('test_images', 'test_images'),
    ],
    hiddenimports=[
        'tkinterdnd2',
        'PIL._tkinter_finder'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PhotoWatermark-v{VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('PhotoWatermark_4.0.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    logger.info("✅ spec文件创建完成")

def build_executable():
    """构建可执行文件"""
    logger.info("开始构建可执行文件...")
    
    try:
        # 使用spec文件构建
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'PhotoWatermark_4.0.spec']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        logger.info("✅ 可执行文件构建成功")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 构建失败: {e}")
        logger.error(f"错误输出: {e.stderr}")
        return False

def create_release_package():
    """创建发布包"""
    logger.info("创建发布包...")
    
    system_info = get_system_info()
    package_name = f"PhotoWatermark_v{VERSION}_{system_info['machine']}"
    
    # 创建发布目录
    release_dir = Path(package_name)
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    try:
        # 复制可执行文件
        exe_name = f'PhotoWatermark-v{VERSION}'
        if system_info['system'] == 'Windows':
            exe_name += '.exe'
        
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
            'README.md',
            'CHANGELOG.md',
            'LICENSE'
        ]
        
        for file_name in files_to_copy:
            if os.path.exists(file_name):
                shutil.copy2(file_name, release_dir / file_name)
                logger.info(f"✅ 复制文件: {file_name}")
        
        # 复制测试图片目录
        if os.path.exists('test_images'):
            shutil.copytree('test_images', release_dir / 'test_images')
            logger.info("✅ 复制测试图片目录")
        
        # 创建发布说明
        create_release_notes(release_dir, system_info)
        
        # 创建启动脚本
        create_launch_script(release_dir, exe_name, system_info)
        
        logger.info(f"✅ 发布包创建完成: {package_name}")
        return package_name
        
    except Exception as e:
        logger.error(f"❌ 创建发布包失败: {e}")
        return None

def create_release_notes(release_dir, system_info):
    """创建发布说明"""
    notes_content = f"""# PhotoWatermark v{VERSION} 发布说明

## 版本信息
- **版本号**: {VERSION}
- **发布日期**: {RELEASE_DATE}
- **构建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **系统架构**: {system_info['machine']}
- **Python版本**: {system_info['python_version']}
- **平台**: {system_info['platform']}

## 🎯 主要特性

### 现代化GUI界面
- ✅ **拖拽支持**: 直接拖拽图片文件和文件夹到应用窗口
- ✅ **实时预览**: 所见即所得的水印预览功能
- ✅ **交互式定位**: 在预览区域直接拖拽调整水印位置
- ✅ **批量处理**: 支持同时处理多张图片

### 水印功能
- ✅ **文本水印**: 自定义文字、字体、大小、颜色、透明度
- ✅ **图片水印**: 支持PNG/JPG水印图片，可调整缩放和透明度
- ✅ **位置控制**: 9个预设位置 + 自定义偏移 + 拖拽定位
- ✅ **模板管理**: 保存和加载水印设置模板

### 输出选项
- ✅ **格式支持**: JPEG、PNG格式输出
- ✅ **质量控制**: 可调节JPEG输出质量
- ✅ **批量输出**: 支持批量处理和自定义输出目录

## 🚀 使用方法

### 快速开始
1. 双击运行 `PhotoWatermark-v{VERSION}` 可执行文件
2. 拖拽图片文件到应用窗口，或使用"选择文件"按钮
3. 在右侧设置面板配置水印参数
4. 在预览区域查看效果，可直接拖拽调整水印位置
5. 点击"开始处理"按钮生成带水印的图片

### 高级功能
- **模板管理**: 保存常用设置为模板，快速应用
- **批量处理**: 一次性处理多张图片
- **精确定位**: 使用拖拽或数值输入精确控制水印位置

## 📋 系统要求
- **操作系统**: macOS 10.13+ / Windows 10+ / Linux
- **内存**: 建议 4GB 以上
- **存储**: 至少 100MB 可用空间

## 🛠️ 故障排除

### macOS 安全提示
首次运行时可能出现安全提示：
1. 右键点击可执行文件
2. 选择"打开"
3. 在弹出对话框中点击"打开"

### 性能优化
- 处理大量图片时建议分批处理
- 大尺寸图片可能需要更长处理时间
- 关闭其他占用内存的应用程序

## 📞 技术支持
如遇问题，请提供以下信息：
- 操作系统版本
- 错误信息截图
- 操作步骤描述

---

**PhotoWatermark v{VERSION}** - 专业的图片水印添加工具
"""
    
    with open(release_dir / 'RELEASE_NOTES.md', 'w', encoding='utf-8') as f:
        f.write(notes_content)
    
    logger.info("✅ 发布说明创建完成")

def create_launch_script(release_dir, exe_name, system_info):
    """创建启动脚本"""
    if system_info['system'] == 'Darwin':  # macOS
        script_content = f"""#!/bin/bash
# PhotoWatermark v{VERSION} 启动脚本

echo "启动 PhotoWatermark v{VERSION}..."
cd "$(dirname "$0")"
./{exe_name}
"""
        script_path = release_dir / 'launch.sh'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        logger.info("✅ macOS启动脚本创建完成")
        
    elif system_info['system'] == 'Windows':  # Windows
        script_content = f"""@echo off
REM PhotoWatermark v{VERSION} 启动脚本

echo 启动 PhotoWatermark v{VERSION}...
cd /d "%~dp0"
{exe_name}
"""
        with open(release_dir / 'launch.bat', 'w', encoding='utf-8') as f:
            f.write(script_content)
        logger.info("✅ Windows启动脚本创建完成")

def main():
    """主函数"""
    logger.info(f"开始构建 PhotoWatermark v{VERSION} 发布版本")
    
    system_info = get_system_info()
    logger.info(f"系统信息: {system_info}")
    
    # 检查依赖
    if not check_dependencies():
        logger.error("❌ 依赖检查失败")
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建spec文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        logger.error("❌ 构建失败")
        return False
    
    # 创建发布包
    package_name = create_release_package()
    if not package_name:
        logger.error("❌ 发布包创建失败")
        return False
    
    logger.info(f"🎉 PhotoWatermark v{VERSION} 构建完成!")
    logger.info(f"📦 发布包: {package_name}")
    logger.info(f"📍 位置: {os.path.abspath(package_name)}")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)