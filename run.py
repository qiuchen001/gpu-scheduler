#!/usr/bin/env python3
"""
GPU调度系统启动脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gpu_scheduler.log', encoding='utf-8')
    ]
)

def main():
    """主函数"""
    try:
        from web_app import app, scheduler
        
        # 启动调度器
        scheduler.start()
        logging.info("调度器已启动")
        
        # 启动Web应用
        logging.info("启动Web应用...")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        logging.info("收到中断信号，正在关闭...")
        if 'scheduler' in locals():
            scheduler.stop()
        logging.info("系统已关闭")
    except Exception as e:
        logging.error(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 