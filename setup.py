#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="photo-watermark",
    version="1.2.0",
    author="PhotoWatermark Team",
    author_email="",
    description="一个功能强大的图片水印添加工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/PhotoWatermark",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Multimedia :: Graphics :: Editors",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "photo-watermark=photo_watermark:main",
            "watermark-gui=main:main",
            "template-manager=template_manager:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="watermark, image, photo, batch, processing, gui, cli",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/PhotoWatermark/issues",
        "Source": "https://github.com/yourusername/PhotoWatermark",
        "Documentation": "https://github.com/yourusername/PhotoWatermark/blob/main/README.md",
    },
)