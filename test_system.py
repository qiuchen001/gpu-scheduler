#!/usr/bin/env python3
"""
GPU调度系统测试脚本
"""

import os
import sys
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gpu_monitor():
    """测试GPU监控模块"""
    print("测试GPU监控模块...")
    try:
        from gpu_monitor import GPUMonitor
        
        monitor = GPUMonitor()
        gpu_info = monitor.get_gpu_info()
        
        print(f"检测到 {len(gpu_info)} 个GPU")
        for gpu in gpu_info:
            print(f"GPU {gpu['index']}: {gpu['name']}, 可用: {gpu['is_available']}")
        
        available_count = monitor.get_available_gpu_count()
        print(f"可用GPU数量: {available_count}")
        
        return True
    except Exception as e:
        print(f"GPU监控测试失败: {e}")
        return False

def test_script_parser():
    """测试脚本解析模块"""
    print("\n测试脚本解析模块...")
    try:
        from script_parser import ScriptParser
        
        parser = ScriptParser()
        
        # 测试Shell脚本
        shell_script_path = "example_script.sh"
        if os.path.exists(shell_script_path):
            result = parser.extract_script_info(shell_script_path)
            print(f"Shell脚本解析结果: {result}")
            
            if result['is_valid']:
                print(f"Shell脚本类型: {result.get('script_type', 'unknown')}")
                print(f"需要GPU数量: {result['required_gpus']}")
                print(f"GPU索引: {result['gpu_indices']}")
            else:
                print(f"Shell脚本无效: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"Shell示例脚本不存在: {shell_script_path}")
            return False
        
        # 测试Python脚本
        python_script_path = "example_python_script.py"
        if os.path.exists(python_script_path):
            result = parser.extract_script_info(python_script_path)
            print(f"Python脚本解析结果: {result}")
            
            if result['is_valid']:
                print(f"Python脚本类型: {result.get('script_type', 'unknown')}")
                print(f"需要GPU数量: {result['required_gpus']}")
                print(f"GPU索引: {result['gpu_indices']}")
                return True
            else:
                print(f"Python脚本无效: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"Python示例脚本不存在: {python_script_path}")
            return False
            
    except Exception as e:
        print(f"脚本解析测试失败: {e}")
        return False

def test_task_scheduler():
    """测试任务调度模块"""
    print("\n测试任务调度模块...")
    try:
        from task_scheduler import TaskScheduler
        
        scheduler = TaskScheduler()
        
        # 测试提交Shell任务
        shell_script_path = "example_script.sh"
        if os.path.exists(shell_script_path):
            task_id = scheduler.submit_task(shell_script_path, priority=0)
            print(f"Shell任务提交成功，ID: {task_id}")
            
            # 获取任务状态
            status = scheduler.get_task_status(task_id)
            print(f"Shell任务状态: {status}")
        
        # 测试提交Python任务
        python_script_path = "example_python_script.py"
        if os.path.exists(python_script_path):
            task_id = scheduler.submit_task(python_script_path, priority=1)
            print(f"Python任务提交成功，ID: {task_id}")
            
            # 获取任务状态
            status = scheduler.get_task_status(task_id)
            print(f"Python任务状态: {status}")
            
            # 获取系统状态
            system_status = scheduler.get_system_status()
            print(f"系统状态: {system_status}")
            
            return True
        else:
            print(f"Python示例脚本不存在: {python_script_path}")
            return False
    except Exception as e:
        print(f"任务调度测试失败: {e}")
        return False

def test_script_executor():
    """测试脚本执行模块"""
    print("\n测试脚本执行模块...")
    try:
        from script_executor import ScriptExecutor
        
        executor = ScriptExecutor()
        
        # 测试执行Shell脚本
        shell_script_path = "example_script.sh"
        if os.path.exists(shell_script_path):
            result = executor.execute_script(shell_script_path, [0, 1])
            print(f"Shell脚本执行结果: {result}")
            
            if result['success']:
                print("Shell脚本执行成功")
            else:
                print(f"Shell脚本执行失败: {result.get('error', '未知错误')}")
        
        # 测试执行Python脚本
        python_script_path = "example_python_script.py"
        if os.path.exists(python_script_path):
            result = executor.execute_script(python_script_path, [0, 1])
            print(f"Python脚本执行结果: {result}")
            
            if result['success']:
                print("Python脚本执行成功")
                return True
            else:
                print(f"Python脚本执行失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"Python示例脚本不存在: {python_script_path}")
            return False
    except Exception as e:
        print(f"脚本执行测试失败: {e}")
        return False

def test_script_type_detection():
    """测试脚本类型检测"""
    print("\n测试脚本类型检测...")
    try:
        from script_executor import ScriptExecutor
        
        executor = ScriptExecutor()
        
        # 测试不同类型的脚本
        test_cases = [
            ("example_script.sh", "shell"),
            ("example_python_script.py", "python"),
            ("test_system.py", "python"),
        ]
        
        for script_path, expected_type in test_cases:
            if os.path.exists(script_path):
                detected_type = executor._get_script_type(script_path)
                print(f"脚本: {script_path}")
                print(f"  期望类型: {expected_type}")
                print(f"  检测类型: {detected_type}")
                print(f"  检测结果: {'✅' if detected_type == expected_type else '❌'}")
            else:
                print(f"脚本不存在: {script_path}")
        
        return True
    except Exception as e:
        print(f"脚本类型检测测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始GPU调度系统测试...\n")
    
    tests = [
        ("GPU监控", test_gpu_monitor),
        ("脚本解析", test_script_parser),
        ("任务调度", test_task_scheduler),
        ("脚本执行", test_script_executor),
        ("脚本类型检测", test_script_type_detection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        print("✅ 支持Shell和Python脚本执行")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置。")
        return False

if __name__ == '__main__':
    main() 