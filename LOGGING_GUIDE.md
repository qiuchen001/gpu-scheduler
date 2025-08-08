# 日志记录说明

## 概述

GPU调度系统提供了完整的日志记录功能，包括系统日志和脚本执行日志，帮助您监控系统运行状态和调试问题。

## 日志文件位置

### 1. 系统日志
- **文件**: `gpu_scheduler.log`
- **位置**: 项目根目录
- **内容**: 系统运行状态、任务管理、GPU监控等

### 2. 脚本执行日志
- **文件**: `logs/scripts_YYYYMMDD.log`
- **位置**: `logs/` 目录
- **内容**: 脚本执行详情、性能信息、错误信息等

## 日志级别

### INFO (信息)
- 任务提交、执行、完成
- GPU状态变化
- 系统启动、停止
- 脚本执行状态

### WARNING (警告)
- GPU资源不足
- 脚本执行超时
- 配置问题

### ERROR (错误)
- 脚本执行失败
- 系统异常
- 文件权限问题

### DEBUG (调试)
- 详细的执行过程
- 内部状态信息

## 系统日志示例

```
2024-01-01 10:00:00 - INFO - 任务调度器初始化完成 - 重试间隔: 5s, 空闲间隔: 1s
2024-01-01 10:00:01 - INFO - 调度器已启动
2024-01-01 10:00:02 - INFO - 任务已提交: task_1, 需要GPU: 2
2024-01-01 10:00:03 - INFO - 开始执行任务: task_1
2024-01-01 10:00:04 - INFO - 检测到脚本类型: python
2024-01-01 10:00:04 - INFO - 设置CUDA_VISIBLE_DEVICES: 0,1
2024-01-01 10:00:04 - INFO - 开始执行python脚本: example_script.py, PID: 12345
2024-01-01 10:00:14 - INFO - python脚本执行成功: example_script.py
2024-01-01 10:00:14 - INFO - 任务执行成功: task_1
```

## 脚本执行日志示例

```
2024-01-01 10:00:02 - INFO - [PYTHON] SCRIPT_TYPE_DETECTED: example_script.py
2024-01-01 10:00:03 - INFO - [PYTHON] GPU_ASSIGNED: example_script.py - GPU: [0, 1]
2024-01-01 10:00:04 - INFO - [PYTHON] EXECUTION_STARTED: example_script.py - CMD: python example_script.py
2024-01-01 10:00:04 - INFO - [PYTHON] PROCESS_STARTED: example_script.py - PID: 12345
2024-01-01 10:00:14 - INFO - [PYTHON] EXECUTION_SUCCESS: example_script.py - Exit: 0, Time: 10.25s
2024-01-01 10:00:14 - INFO - [PYTHON] OUTPUT_SUMMARY: example_script.py - Lines: 15, First: 这是一个Python示例任务
```

## 日志记录的事件类型

### 脚本执行事件

| 事件 | 描述 | 示例 |
|------|------|------|
| `SCRIPT_TYPE_DETECTED` | 脚本类型检测 | `[PYTHON] SCRIPT_TYPE_DETECTED: script.py` |
| `GPU_ASSIGNED` | GPU分配 | `[PYTHON] GPU_ASSIGNED: script.py - GPU: [0, 1]` |
| `EXECUTION_STARTED` | 开始执行 | `[PYTHON] EXECUTION_STARTED: script.py - CMD: python script.py` |
| `PROCESS_STARTED` | 进程启动 | `[PYTHON] PROCESS_STARTED: script.py - PID: 12345` |
| `EXECUTION_SUCCESS` | 执行成功 | `[PYTHON] EXECUTION_SUCCESS: script.py - Exit: 0, Time: 10.25s` |
| `EXECUTION_FAILED` | 执行失败 | `[PYTHON] EXECUTION_FAILED: script.py - Exit: 1, Time: 5.30s` |
| `EXECUTION_TIMEOUT` | 执行超时 | `[PYTHON] EXECUTION_TIMEOUT: script.py - Timeout: 3600s` |
| `OUTPUT_SUMMARY` | 输出摘要 | `[PYTHON] OUTPUT_SUMMARY: script.py - Lines: 15, First: 输出内容...` |
| `FILE_NOT_FOUND` | 文件不存在 | `[UNKNOWN] FILE_NOT_FOUND: script.py` |
| `PERMISSION_DENIED` | 权限不足 | `[UNKNOWN] PERMISSION_DENIED: script.py` |

### 系统事件

| 事件 | 描述 | 示例 |
|------|------|------|
| 任务提交 | 新任务提交到队列 | `任务已提交: task_1, 需要GPU: 2` |
| 任务执行 | 开始执行任务 | `开始执行任务: task_1` |
| 任务完成 | 任务执行完成 | `任务执行成功: task_1` |
| 任务失败 | 任务执行失败 | `任务执行失败: task_1, 错误: 脚本不存在` |
| GPU监控 | GPU状态检查 | `GPU可用性检查: 需要2个GPU, 可用4个GPU` |
| 调度器状态 | 调度器运行状态 | `调度器已启动` / `调度器已停止` |

## 日志查看方法

### 1. 命令行查看

```bash
# 查看系统日志
tail -f gpu_scheduler.log

# 查看脚本日志
tail -f logs/scripts_20240101.log

# 过滤特定内容
grep "ERROR" gpu_scheduler.log
grep "task_1" logs/scripts_20240101.log

# 查看最近的日志
tail -n 100 gpu_scheduler.log
```

### 2. Web界面查看

访问 `http://localhost:5000/logs` 页面：
- 选择日志类型（系统日志/脚本日志）
- 选择日志级别
- 输入关键词过滤
- 实时刷新日志

### 3. 日志分析

```bash
# 统计错误数量
grep -c "ERROR" gpu_scheduler.log

# 查看特定任务的日志
grep "task_1" gpu_scheduler.log

# 查看脚本执行时间
grep "EXECUTION_SUCCESS" logs/scripts_*.log | grep -o "Time: [0-9.]*s"

# 查看GPU分配情况
grep "GPU_ASSIGNED" logs/scripts_*.log
```

## 日志配置

### 日志级别设置

在 `run.py` 中修改日志级别：

```python
logging.basicConfig(
    level=logging.INFO,  # 可以改为 DEBUG, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gpu_scheduler.log', encoding='utf-8')
    ]
)
```

### 日志轮转

系统会自动创建按日期命名的脚本日志文件：
- `logs/scripts_20240101.log`
- `logs/scripts_20240102.log`
- ...

### 日志清理

```bash
# 清理旧日志文件
find logs/ -name "scripts_*.log" -mtime +30 -delete

# 清理系统日志
> gpu_scheduler.log
```

## 故障排除

### 常见日志问题

1. **日志文件不存在**
   - 检查 `logs/` 目录是否存在
   - 确认文件权限

2. **日志内容为空**
   - 检查系统是否正常运行
   - 确认日志级别设置

3. **日志文件过大**
   - 定期清理旧日志
   - 调整日志级别

### 调试技巧

1. **启用DEBUG级别**
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **查看特定模块日志**
   ```python
   logging.getLogger('script_executor').setLevel(logging.DEBUG)
   ```

3. **添加自定义日志**
   ```python
   logging.info("自定义日志信息")
   logging.error("错误信息", exc_info=True)
   ```

## 最佳实践

### 1. 日志监控
- 定期检查错误日志
- 监控脚本执行时间
- 关注GPU分配情况

### 2. 日志备份
- 定期备份重要日志
- 保留历史日志用于分析

### 3. 日志分析
- 分析脚本执行模式
- 识别性能瓶颈
- 优化系统配置

### 4. 安全考虑
- 避免记录敏感信息
- 定期清理日志文件
- 限制日志文件大小

## 总结

系统提供了完整的日志记录功能：

- ✅ **系统日志**: 记录系统运行状态
- ✅ **脚本日志**: 记录脚本执行详情
- ✅ **Web界面**: 提供友好的日志查看界面
- ✅ **日志分级**: 支持不同级别的日志记录
- ✅ **日志轮转**: 按日期自动创建日志文件
- ✅ **日志过滤**: 支持关键词和级别过滤

这些日志功能帮助您更好地监控系统运行状态，快速定位和解决问题。 