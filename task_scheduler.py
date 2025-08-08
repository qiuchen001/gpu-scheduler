import time
import threading
import queue
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from gpu_monitor import GPUMonitor
from script_parser import ScriptParser
from script_executor import ScriptExecutor


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务数据类"""
    id: str
    script_path: str
    required_gpus: int
    gpu_indices: List[int]
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    error_message: str = ""
    output: str = ""

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self):
        """转换为字典"""
        result = asdict(self)
        result['status'] = self.status.value
        result['created_at'] = self.created_at.isoformat() if self.created_at else None
        result['started_at'] = self.started_at.isoformat() if self.started_at else None
        result['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return result


class TaskScheduler:
    """任务调度器，管理任务队列和执行"""

    def __init__(self):
        self.gpu_monitor = GPUMonitor()
        self.script_parser = ScriptParser()
        self.script_executor = ScriptExecutor()

        self.task_queue = queue.PriorityQueue()
        self.running_tasks = {}
        self.completed_tasks = {}
        self.task_counter = 0

        self.scheduler_thread = None
        self.is_running = False
        self.lock = threading.Lock()

        logging.info("任务调度器初始化完成")

    def start(self):
        """启动调度器"""
        if self.is_running:
            logging.warning("调度器已在运行")
            return

        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logging.info("调度器已启动")

    def stop(self):
        """停止调度器"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logging.info("调度器已停止")

    def submit_task(self, script_path: str, priority: int = 0) -> str:
        """提交任务到队列"""
        try:
            # 解析脚本
            script_info = self.script_parser.extract_script_info(script_path)

            if not script_info['is_valid']:
                raise ValueError(f"脚本无效: {script_info.get('error', '未知错误')}")

            # 创建任务
            with self.lock:
                self.task_counter += 1
                task_id = f"task_{self.task_counter}"

            task = Task(
                id=task_id,
                script_path=script_path,
                required_gpus=script_info['required_gpus'],
                gpu_indices=script_info['gpu_indices'],
                priority=priority
            )

            # 添加到队列 (优先级越高，数字越小)
            self.task_queue.put((-priority, task))

            logging.info(f"任务已提交: {task_id}, 需要GPU: {script_info['required_gpus']}")
            return task_id

        except Exception as e:
            logging.error(f"提交任务失败: {e}")
            raise

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        # 检查运行中的任务
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            return task.to_dict()

        # 检查已完成的任务
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return task.to_dict()

        # 检查队列中的任务
        with self.lock:
            temp_queue = queue.PriorityQueue()
            found_task = None

            while not self.task_queue.empty():
                priority, task = self.task_queue.get()
                if task.id == task_id:
                    found_task = task
                temp_queue.put((priority, task))

            # 恢复队列
            self.task_queue = temp_queue

            if found_task:
                return found_task.to_dict()

        return None

    def get_all_tasks(self) -> Dict:
        """获取所有任务信息"""
        with self.lock:
            # 获取队列中的任务
            pending_tasks = []
            temp_queue = queue.PriorityQueue()

            while not self.task_queue.empty():
                priority, task = self.task_queue.get()
                pending_tasks.append(task.to_dict())
                temp_queue.put((priority, task))

            # 恢复队列
            self.task_queue = temp_queue

        return {
            'pending': pending_tasks,
            'running': [task.to_dict() for task in self.running_tasks.values()],
            'completed': [task.to_dict() for task in self.completed_tasks.values()]
        }

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 检查运行中的任务
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            self.completed_tasks[task_id] = task
            del self.running_tasks[task_id]
            logging.info(f"任务已取消: {task_id}")
            return True

        # 检查队列中的任务
        with self.lock:
            temp_queue = queue.PriorityQueue()
            cancelled = False

            while not self.task_queue.empty():
                priority, task = self.task_queue.get()
                if task.id == task_id:
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.now()
                    self.completed_tasks[task_id] = task
                    cancelled = True
                else:
                    temp_queue.put((priority, task))

            # 恢复队列
            self.task_queue = temp_queue

            if cancelled:
                logging.info(f"任务已取消: {task_id}")
                return True

        return False

    def _scheduler_loop(self):
        """调度器主循环"""
        while self.is_running:
            try:
                # 检查是否有可执行的任务
                if not self.task_queue.empty():
                    # 获取最高优先级的任务
                    priority, task = self.task_queue.get()

                    # 检查GPU可用性
                    if self.gpu_monitor.check_gpu_availability(task.required_gpus):
                        # 执行任务
                        self._execute_task(task)
                    else:
                        # 放回队列
                        self.task_queue.put((priority, task))
                        time.sleep(5)  # 等待5秒后重试
                else:
                    time.sleep(1)  # 队列为空时等待

            except Exception as e:
                logging.error(f"调度器循环错误: {e}")
                time.sleep(5)

    def _execute_task(self, task: Task):
        """执行任务"""
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self.running_tasks[task.id] = task

            logging.info(f"开始执行任务: {task.id}")

            # 执行脚本
            result = self.script_executor.execute_script(
                task.script_path,
                task.gpu_indices
            )

            # 更新任务状态
            task.completed_at = datetime.now()
            task.output = result.get('output', '')

            if result['success']:
                task.status = TaskStatus.COMPLETED
                logging.info(f"任务执行成功: {task.id}")
            else:
                task.status = TaskStatus.FAILED
                task.error_message = result.get('error', '未知错误')
                logging.error(f"任务执行失败: {task.id}, 错误: {task.error_message}")

            # 移动到已完成任务列表
            self.completed_tasks[task.id] = task
            del self.running_tasks[task.id]

        except Exception as e:
            logging.error(f"执行任务时发生错误: {task.id}, {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self.completed_tasks[task.id] = task
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

    def get_system_status(self) -> Dict:
        """获取系统状态"""
        gpu_status = self.gpu_monitor.get_gpu_status_summary()

        return {
            'gpu_status': gpu_status,
            'queue_size': self.task_queue.qsize(),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(self.completed_tasks),
            'scheduler_running': self.is_running
        }
