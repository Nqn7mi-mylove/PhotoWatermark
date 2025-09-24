#!/bin/bash
# PhotoWatermark 交互式启动脚本

echo "🚀 启动 PhotoWatermark 交互式界面..."
echo "如果这是第一次运行，系统可能会要求安全确认。"
echo ""

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 运行交互式程序
"$DIR/watermark-interactive"
