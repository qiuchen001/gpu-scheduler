# Python脚本支持说明

## 概述

GPU调度系统现在完全支持Python脚本的执行！系统可以自动检测脚本类型，解析Python脚本中的GPU需求，并安全地执行Python代码。

## 支持的Python脚本格式

### 1. GPU环境变量设置

```python
import os

# 方式1: 直接设置环境变量
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'

# 方式2: 使用setdefault
os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0,1,2')
```

### 2. PyTorch GPU设置

```python
import torch

# 方式1: 设置设备
torch.cuda.set_device(0)

# 方式2: 创建设备对象
device = torch.device('cuda:0')
```

### 3. 完整的Python脚本示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import torch

def main():
    # 设置GPU环境变量
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    
    print("开始执行Python任务...")
    
    # 检查CUDA可用性
    if torch.cuda.is_available():
        print(f"GPU数量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    
    # 你的GPU计算代码
    print("任务完成")

if __name__ == "__main__":
    main()
```

## 脚本类型检测

系统会自动检测脚本类型：

### 检测规则

1. **文件扩展名检测**:
   - `.py`, `.python` → Python脚本
   - `.sh`, `.bash`, `.zsh`, 无扩展名 → Shell脚本

2. **Shebang检测**:
   - `#!/usr/bin/env python` → Python脚本
   - `#!/bin/bash` → Shell脚本

3. **默认行为**:
   - 无法确定类型时默认为Shell脚本

## GPU需求解析

系统支持解析以下Python代码中的GPU需求：

### 支持的模式

1. **环境变量设置**:
   ```python
   os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'
   ```

2. **setdefault方式**:
   ```python
   os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0,1,2')
   ```

3. **PyTorch设备设置**:
   ```python
   torch.cuda.set_device(0)
   torch.device('cuda:0')
   ```

### GPU索引格式

- **单个GPU**: `0`, `1`, `2`
- **多个GPU**: `0,1,2`
- **GPU范围**: `0-3` (解析为 0,1,2,3)
- **混合格式**: `0,1,3-5` (解析为 0,1,3,4,5)

## 执行环境

### Python环境

- 使用系统默认的Python解释器
- 支持Python 3.x
- 自动设置环境变量

### 安全特性

- 进程隔离执行
- 超时控制
- 错误处理和日志记录
- 进程管理和终止

## Web界面支持

### 任务管理

- 自动显示脚本类型（Python/Shell）
- 脚本类型图标和颜色标识
- 任务详情中显示脚本类型信息

### 提交任务

- 支持Python脚本路径输入
- 自动检测脚本类型
- 实时显示解析结果

## 测试验证

### 运行测试

```bash
python test_system.py
```

### 手动测试

```python
from script_executor import ScriptExecutor

executor = ScriptExecutor()
result = executor.execute_script('your_script.py', [0, 1])
print(result)
```

## 故障排除

### 常见问题

1. **Python脚本执行失败**
   - 检查Python环境是否正确
   - 确认脚本语法无误
   - 查看错误日志

2. **GPU需求解析失败**
   - 确认使用了支持的GPU设置格式
   - 检查脚本编码（推荐UTF-8）

3. **编码问题**
   - 确保Python脚本使用UTF-8编码
   - 添加编码声明：`# -*- coding: utf-8 -*-`

### 调试技巧

1. **查看执行日志**:
   ```bash
   tail -f gpu_scheduler.log
   ```

2. **测试脚本解析**:
   ```python
   from script_parser import ScriptParser
   parser = ScriptParser()
   result = parser.extract_script_info('your_script.py')
   print(result)
   ```

## 最佳实践

### 1. 脚本编写

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)

def main():
    # 设置GPU环境变量
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    
    try:
        # 你的GPU计算代码
        print("任务执行成功")
    except Exception as e:
        print(f"任务执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 2. 错误处理

```python
import os
import sys

def main():
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    
    try:
        # 主要逻辑
        pass
    except ImportError as e:
        print(f"依赖包缺失: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"执行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 3. 资源清理

```python
import os
import atexit

def cleanup():
    # 清理资源
    pass

def main():
    atexit.register(cleanup)
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    # 主要逻辑

if __name__ == "__main__":
    main()
```

## 总结

GPU调度系统现在完全支持Python脚本，提供了：

- ✅ 自动脚本类型检测
- ✅ Python GPU需求解析
- ✅ 安全的脚本执行环境
- ✅ Web界面完整支持
- ✅ 详细的错误处理和日志
- ✅ 进程管理和超时控制

这使得系统更加灵活，可以处理各种类型的GPU计算任务！ 