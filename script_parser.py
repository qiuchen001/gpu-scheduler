import re
import os
from typing import Dict, List, Optional, Tuple
import logging

class ScriptParser:
    """脚本解析类，用于解析shell和python脚本中的GPU需求"""
    
    def __init__(self):
        # 支持多种GPU设置格式
        self.cuda_patterns = [
            # CUDA_VISIBLE_DEVICES=0,1,2
            re.compile(r'CUDA_VISIBLE_DEVICES\s*=\s*([0-9,\-\s]+)', re.IGNORECASE),
            # os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'
            re.compile(r"os\.environ\[['\"]CUDA_VISIBLE_DEVICES['\"]\]\s*=\s*['\"]([0-9,\-\s]+)['\"]", re.IGNORECASE),
            # os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0,1,2')
            re.compile(r"os\.environ\.setdefault\(['\"]CUDA_VISIBLE_DEVICES['\"],\s*['\"]([0-9,\-\s]+)['\"]\)", re.IGNORECASE),
            # torch.cuda.set_device(0)
            re.compile(r'torch\.cuda\.set_device\((\d+)\)', re.IGNORECASE),
            # device = torch.device('cuda:0')
            re.compile(r"torch\.device\(['\"]cuda:(\d+)['\"]\)", re.IGNORECASE),
        ]
    
    def parse_script(self, script_path: str) -> Dict:
        """解析脚本文件，提取GPU需求信息"""
        try:
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"脚本文件不存在: {script_path}")
            
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            return self.parse_script_content(script_content, script_path)
            
        except Exception as e:
            logging.error(f"解析脚本失败: {e}")
            return {
                'script_path': script_path,
                'required_gpus': 0,
                'gpu_indices': [],
                'is_valid': False,
                'error': str(e)
            }
    
    def parse_script_content(self, script_content: str, script_path: str = "") -> Dict:
        """解析脚本内容，提取GPU需求信息"""
        try:
            # 判断脚本类型
            script_type = self._get_script_type(script_path)
            logging.info(f"解析{script_type}脚本: {script_path}")
            
            # 查找GPU设置
            gpu_indices = []
            cuda_visible_devices = None
            
            for pattern in self.cuda_patterns:
                matches = pattern.findall(script_content)
                for match in matches:
                    if match:
                        indices = self._parse_gpu_indices(match)
                        gpu_indices.extend(indices)
                        if 'CUDA_VISIBLE_DEVICES' in str(pattern):
                            cuda_visible_devices = match.strip()
            
            # 去重并排序
            gpu_indices = sorted(list(set(gpu_indices)))
            
            if not gpu_indices:
                return {
                    'script_path': script_path,
                    'script_type': script_type,
                    'required_gpus': 0,
                    'gpu_indices': [],
                    'is_valid': True,
                    'message': f'{script_type}脚本中未指定GPU需求，将使用所有可用GPU'
                }
            
            return {
                'script_path': script_path,
                'script_type': script_type,
                'required_gpus': len(gpu_indices),
                'gpu_indices': gpu_indices,
                'is_valid': True,
                'cuda_visible_devices': cuda_visible_devices
            }
            
        except Exception as e:
            logging.error(f"解析脚本内容失败: {e}")
            return {
                'script_path': script_path,
                'script_type': 'unknown',
                'required_gpus': 0,
                'gpu_indices': [],
                'is_valid': False,
                'error': str(e)
            }
    
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
    
    def _parse_gpu_indices(self, gpu_indices_str: str) -> List[int]:
        """解析GPU索引字符串"""
        indices = []
        
        # 处理逗号分隔的GPU索引
        for part in gpu_indices_str.split(','):
            part = part.strip()
            if not part:
                continue
            
            # 处理范围表示法 (如 0-3)
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    indices.extend(range(start, end + 1))
                except ValueError:
                    logging.warning(f"无效的GPU范围: {part}")
            else:
                try:
                    indices.append(int(part))
                except ValueError:
                    logging.warning(f"无效的GPU索引: {part}")
        
        # 去重并排序
        return sorted(list(set(indices)))
    
    def validate_script(self, script_path: str) -> Tuple[bool, str]:
        """验证脚本是否有效"""
        try:
            if not os.path.exists(script_path):
                return False, f"脚本文件不存在: {script_path}"
            
            if not os.access(script_path, os.R_OK):
                return False, f"无法读取脚本文件: {script_path}"
            
            # 检查文件扩展名
            script_type = self._get_script_type(script_path)
            _, ext = os.path.splitext(script_path)
            
            if script_type == 'python':
                if ext.lower() not in ['.py', '.python', '']:
                    logging.warning(f"Python脚本文件扩展名可能不正确: {script_path}")
            else:
                if ext.lower() not in ['.sh', '.bash', '.zsh', '']:
                    logging.warning(f"Shell脚本文件扩展名可能不正确: {script_path}")
            
            return True, f"{script_type}脚本验证通过"
            
        except Exception as e:
            return False, f"脚本验证失败: {e}"
    
    def extract_script_info(self, script_path: str) -> Dict:
        """提取脚本的完整信息"""
        # 验证脚本
        is_valid, message = self.validate_script(script_path)
        
        if not is_valid:
            return {
                'script_path': script_path,
                'script_type': 'unknown',
                'is_valid': False,
                'error': message
            }
        
        # 解析脚本
        parse_result = self.parse_script(script_path)
        parse_result['validation_message'] = message
        
        return parse_result 