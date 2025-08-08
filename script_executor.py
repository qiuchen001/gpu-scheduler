import subprocess
import os
import signal
import time
import logging
from typing import Dict, List, Optional
import threading


class ScriptExecutor:
    """脚本执行器，安全地执行shell和python脚本"""

    def __init__(self):
        self.running_processes = {}
        self.process_lock = threading.Lock()

    def _get_script_type(self, script_path: str) -> str:
        """判断脚本类型"""
        _, ext = os.path.splitext(script_path)
        if ext.lower() in ['.py', '.python']:
            return 'python'
        elif ext.lower() in ['.sh', '.bash', '.zsh', '']:
            return 'shell'
        else:
            # 检查文件头部来判断类型
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#!'):
                        if 'python' in first_line:
                            return 'python'
                        elif any(shell in first_line for shell in ['bash', 'sh', 'zsh']):
                            return 'shell'
            except:
                pass
            return 'shell'  # 默认为shell

    def _get_execution_command(self, script_path: str, script_type: str) -> List[str]:
        """获取执行命令"""
        if script_type == 'python':
            return ['python', script_path]
        else:
            return ['bash', script_path]

    def execute_script(self, script_path: str, gpu_indices: List[int] = None) -> Dict:
        """执行脚本"""
        try:
            # 验证脚本文件
            if not os.path.exists(script_path):
                return {
                    'success': False,
                    'error': f'脚本文件不存在: {script_path}',
                    'output': ''
                }

            if not os.access(script_path, os.R_OK):
                return {
                    'success': False,
                    'error': f'脚本文件无读取权限: {script_path}',
                    'output': ''
                }

            # 判断脚本类型
            script_type = self._get_script_type(script_path)
            logging.info(f"检测到脚本类型: {script_type}")

            # 设置环境变量
            env = os.environ.copy()
            if gpu_indices:
                env['CUDA_VISIBLE_DEVICES'] = ','.join(map(str, gpu_indices))
                logging.info(f"设置CUDA_VISIBLE_DEVICES: {env['CUDA_VISIBLE_DEVICES']}")

            # 获取执行命令
            cmd = self._get_execution_command(script_path, script_type)

            # 执行脚本
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )

            # 记录进程
            process_id = f"process_{process.pid}"
            with self.process_lock:
                self.running_processes[process_id] = {
                    'process': process,
                    'script_path': script_path,
                    'script_type': script_type,
                    'start_time': time.time()
                }

            logging.info(f"开始执行{script_type}脚本: {script_path}, PID: {process.pid}")

            # 获取输出
            output, _ = process.communicate()
            exit_code = process.returncode

            # 清理进程记录
            with self.process_lock:
                if process_id in self.running_processes:
                    del self.running_processes[process_id]

            # 检查执行结果
            if exit_code == 0:
                logging.info(f"{script_type}脚本执行成功: {script_path}")
                return {
                    'success': True,
                    'output': output,
                    'exit_code': exit_code,
                    'script_type': script_type
                }
            else:
                logging.error(f"{script_type}脚本执行失败: {script_path}, 退出码: {exit_code}")
                return {
                    'success': False,
                    'error': f'{script_type}脚本执行失败，退出码: {exit_code}',
                    'output': output,
                    'exit_code': exit_code,
                    'script_type': script_type
                }

        except Exception as e:
            logging.error(f"执行脚本时发生错误: {script_path}, {e}")
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'script_type': 'unknown'
            }

    def execute_script_with_timeout(self, script_path: str, gpu_indices: List[int] = None,
                                    timeout: int = 3600) -> Dict:
        """带超时的脚本执行"""
        try:
            # 验证脚本文件
            if not os.path.exists(script_path):
                return {
                    'success': False,
                    'error': f'脚本文件不存在: {script_path}',
                    'output': ''
                }

            # 判断脚本类型
            script_type = self._get_script_type(script_path)

            # 设置环境变量
            env = os.environ.copy()
            if gpu_indices:
                env['CUDA_VISIBLE_DEVICES'] = ','.join(map(str, gpu_indices))

            # 获取执行命令
            cmd = self._get_execution_command(script_path, script_type)

            # 执行脚本
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )

            # 记录进程
            process_id = f"process_{process.pid}"
            with self.process_lock:
                self.running_processes[process_id] = {
                    'process': process,
                    'script_path': script_path,
                    'script_type': script_type,
                    'start_time': time.time()
                }

            logging.info(f"开始执行{script_type}脚本: {script_path}, PID: {process.pid}, 超时: {timeout}秒")

            try:
                # 等待进程完成，带超时
                output, _ = process.communicate(timeout=timeout)
                exit_code = process.returncode

                # 清理进程记录
                with self.process_lock:
                    if process_id in self.running_processes:
                        del self.running_processes[process_id]

                if exit_code == 0:
                    logging.info(f"{script_type}脚本执行成功: {script_path}")
                    return {
                        'success': True,
                        'output': output,
                        'exit_code': exit_code,
                        'script_type': script_type
                    }
                else:
                    logging.error(f"{script_type}脚本执行失败: {script_path}, 退出码: {exit_code}")
                    return {
                        'success': False,
                        'error': f'{script_type}脚本执行失败，退出码: {exit_code}',
                        'output': output,
                        'exit_code': exit_code,
                        'script_type': script_type
                    }

            except subprocess.TimeoutExpired:
                # 超时，终止进程
                logging.warning(f"{script_type}脚本执行超时: {script_path}, PID: {process.pid}")
                self._terminate_process(process, process_id)

                return {
                    'success': False,
                    'error': f'{script_type}脚本执行超时 (>{timeout}秒)',
                    'output': '',
                    'timeout': True,
                    'script_type': script_type
                }

        except Exception as e:
            logging.error(f"执行脚本时发生错误: {script_path}, {e}")
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'script_type': 'unknown'
            }

    def _terminate_process(self, process: subprocess.Popen, process_id: str):
        """终止进程"""
        try:
            # 发送SIGTERM信号
            process.terminate()

            # 等待进程结束
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # 强制杀死进程
                logging.warning(f"强制终止进程: {process_id}")
                process.kill()
                process.wait()

            # 清理进程记录
            with self.process_lock:
                if process_id in self.running_processes:
                    del self.running_processes[process_id]

        except Exception as e:
            logging.error(f"终止进程时发生错误: {process_id}, {e}")

    def kill_process(self, process_id: str) -> bool:
        """杀死指定进程"""
        with self.process_lock:
            if process_id not in self.running_processes:
                return False

            process_info = self.running_processes[process_id]
            process = process_info['process']

            try:
                self._terminate_process(process, process_id)
                logging.info(f"进程已终止: {process_id}")
                return True
            except Exception as e:
                logging.error(f"终止进程失败: {process_id}, {e}")
                return False

    def get_running_processes(self) -> Dict:
        """获取正在运行的进程信息"""
        with self.process_lock:
            processes = {}
            for process_id, process_info in self.running_processes.items():
                process = process_info['process']
                processes[process_id] = {
                    'script_path': process_info['script_path'],
                    'script_type': process_info.get('script_type', 'unknown'),
                    'pid': process.pid,
                    'start_time': process_info['start_time'],
                    'running_time': time.time() - process_info['start_time']
                }
            return processes

    def kill_all_processes(self):
        """终止所有正在运行的进程"""
        with self.process_lock:
            process_ids = list(self.running_processes.keys())

        for process_id in process_ids:
            self.kill_process(process_id)

        logging.info("所有进程已终止")
