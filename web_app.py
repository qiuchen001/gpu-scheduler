from flask import Flask, render_template, request, jsonify, redirect, url_for
import logging
import os
from datetime import datetime
import json

from task_scheduler import TaskScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gpu-scheduler-secret-key'

# 全局调度器实例
scheduler = TaskScheduler()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    try:
        status = scheduler.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks')
def get_tasks():
    """获取所有任务"""
    try:
        tasks = scheduler.get_all_tasks()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit', methods=['POST'])
def submit_task():
    """提交任务"""
    try:
        data = request.get_json()
        script_path = data.get('script_path')
        priority = data.get('priority', 0)
        
        if not script_path:
            return jsonify({'error': '脚本路径不能为空'}), 400
        
        task_id = scheduler.submit_task(script_path, priority)
        return jsonify({'task_id': task_id, 'message': '任务提交成功'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/<task_id>')
def get_task_status(task_id):
    """获取任务状态"""
    try:
        task_status = scheduler.get_task_status(task_id)
        if task_status:
            return jsonify(task_status)
        else:
            return jsonify({'error': '任务不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """取消任务"""
    try:
        success = scheduler.cancel_task(task_id)
        if success:
            return jsonify({'message': '任务已取消'})
        else:
            return jsonify({'error': '任务不存在或无法取消'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def start_scheduler():
    """启动调度器"""
    try:
        scheduler.start()
        return jsonify({'message': '调度器已启动'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_scheduler():
    """停止调度器"""
    try:
        scheduler.stop()
        return jsonify({'message': '调度器已停止'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')

@app.route('/tasks')
def tasks_page():
    """任务管理页面"""
    return render_template('tasks.html')

if __name__ == '__main__':
    # 启动调度器
    scheduler.start()
    
    # 启动Web应用
    app.run(host='0.0.0.0', port=5000, debug=True) 