import pynvml
import time
from typing import List, Dict, Optional
import logging


class GPUMonitor:
    """GPU监控类，用于获取GPU状态信息"""

    def __init__(self):
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()
            logging.info(f"成功初始化GPU监控，检测到 {self.device_count} 个GPU")
        except Exception as e:
            logging.error(f"GPU监控初始化失败: {e}")
            self.device_count = 0

    def get_gpu_info(self) -> List[Dict]:
        """获取所有GPU的详细信息"""
        gpu_info = []

        for i in range(self.device_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

                gpu_info.append({
                    'index': i,
                    'name': name.decode('utf-8'),
                    'total_memory': memory_info.total,
                    'used_memory': memory_info.used,
                    'free_memory': memory_info.free,
                    'gpu_utilization': utilization.gpu,
                    'memory_utilization': utilization.memory,
                    'is_available': self._is_gpu_available(memory_info, utilization)
                })
            except Exception as e:
                logging.error(f"获取GPU {i} 信息失败: {e}")
                gpu_info.append({
                    'index': i,
                    'name': 'Unknown',
                    'total_memory': 0,
                    'used_memory': 0,
                    'free_memory': 0,
                    'gpu_utilization': 0,
                    'memory_utilization': 0,
                    'is_available': False
                })

        return gpu_info

    def get_available_gpus(self) -> List[int]:
        """获取可用的GPU索引列表"""
        gpu_info = self.get_gpu_info()
        available_gpus = []

        for gpu in gpu_info:
            if gpu['is_available']:
                available_gpus.append(gpu['index'])

        return available_gpus

    def get_available_gpu_count(self) -> int:
        """获取可用GPU数量"""
        return len(self.get_available_gpus())

    def _is_gpu_available(self, memory_info, utilization) -> bool:
        """判断GPU是否可用"""
        # GPU利用率低于10%且内存使用率低于20%认为可用
        return (utilization.gpu < 10 and
                (memory_info.used / memory_info.total) < 0.2)

    def check_gpu_availability(self, required_count: int) -> bool:
        """检查是否有足够的可用GPU"""
        available_count = self.get_available_gpu_count()
        return available_count >= required_count

    def get_gpu_status_summary(self) -> Dict:
        """获取GPU状态摘要"""
        gpu_info = self.get_gpu_info()
        total_gpus = len(gpu_info)
        available_gpus = len([g for g in gpu_info if g['is_available']])

        return {
            'total_gpus': total_gpus,
            'available_gpus': available_gpus,
            'gpu_details': gpu_info
        }

    def __del__(self):
        """清理资源"""
        try:
            pynvml.nvmlShutdown()
        except:
            pass
