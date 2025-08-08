#!/bin/bash

# 示例脚本 - 使用GPU 0,1
CUDA_VISIBLE_DEVICES=0,1 \
echo "这是一个示例任务" \
&& echo "当前时间: $(date)" \
&& echo "使用GPU: $CUDA_VISIBLE_DEVICES" \
&& echo "脚本路径: $0" \
&& echo "工作目录: $(pwd)" \
&& echo "用户: $(whoami)" \
&& echo "主机名: $(hostname)" \
&& sleep 10 \
&& echo "任务完成" 