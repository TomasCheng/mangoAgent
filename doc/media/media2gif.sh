#!/bin/bash

# video2gif.sh - 使用 ffmpeg 调色板方法将视频转换为高质量 GIF
# 用法: ./video2gif.sh <视频文件> [帧率] [缩放宽度]
# 示例: ./video2gif.sh input.mp4 10 800

# 检查 ffmpeg 是否安装
if ! command -v ffmpeg &> /dev/null; then
    echo "错误: 未找到 ffmpeg，请先安装 ffmpeg。"
    exit 1
fi

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <视频文件> [帧率] [缩放宽度]"
    echo "示例: $0 input.mp4 10 800"
    echo "默认帧率 = 10，缩放宽度 = 800"
    exit 1
fi

input="$1"
fps="${2:-10}"      # 默认帧率 10
scale="${3:-800}"   # 默认缩放宽度 800

# 检查输入文件是否存在
if [ ! -f "$input" ]; then
    echo "错误: 文件 '$input' 不存在。"
    exit 1
fi

# 提取文件名（不含扩展名），生成输出文件名
filename=$(basename -- "$input")
output="${filename%.*}.gif"

# 如果输出文件已存在，询问是否覆盖
if [ -f "$output" ]; then
    read -p "输出文件 '$output' 已存在。是否覆盖？(y/n): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "已取消。"
        exit 0
    fi
fi

# 执行转换（使用调色板方法，lanczos 缩放，无限循环）
echo "正在转换 '$input' -> '$output' (帧率=$fps, 宽度=$scale) ..."
ffmpeg -i "$input" -vf "fps=$fps,scale=$scale:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 "$output"

if [ $? -eq 0 ]; then
    echo "转换成功: $output"
else
    echo "转换失败。"
    exit 1
fi