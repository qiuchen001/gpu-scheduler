#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python示例脚本 - 使用GPU 0,1
"""

import os
import time
import sys

def main():
    """主函数"""
    print("这是一个Python示例任务")
    print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"脚本路径: {__file__}")
    print(f"工作目录: {os.getcwd()}")
    print(f"用户: {os.getenv('USER', 'unknown')}")
    print(f"Python版本: {sys.version}")
    
    # 设置GPU环境变量
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    print(f"设置CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES')}")
    
    # 尝试导入torch检查CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f"CUDA可用，GPU数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("CUDA不可用")
    except ImportError:
        print("PyTorch未安装，跳过CUDA检查")
    
    # 模拟一些计算
    print("开始模拟计算...")
    for i in range(5):
        print(f"计算步骤 {i+1}/5")
        time.sleep(2)
    
    print("任务完成")

if __name__ == "__main__":
    main() 