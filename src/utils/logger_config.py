import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import os
import threading


def setup_logger(module_name: str, device_name: str = "default") -> logging.Logger:
    """
    设置模块化日志记录器
    
    Args:
        module_name: 模块名称 (如 'camera', 'face_recognition')
        device_name: 设备名称 (如 'camera_0', 'default')
    
    Returns:
        配置好的 Logger 对象
    """
    # 精简模块名映射
    module_short_names = {
        "main": "_main_",
        "face_recognition": "_fr_",
        "camera": "_cam_",
        "web_app": "_web_",
        "log_filter": "_logf_",
        "config": "_cfg_",
        # 可根据需要添加更多映射
    }
    short_module_name = module_short_names.get(module_name, module_name)
    
    logger = logging.getLogger(f"{short_module_name}_{device_name}")
    logger.setLevel(logging.DEBUG)
    
    # 避免重复处理
    if logger.handlers:
        return logger
    
    # 日志目录
    base_log_dir = os.getenv('LOG_DIR', 'logs')
    log_dir = Path(base_log_dir) / module_name / device_name
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{module_name}_{device_name}.log"
    
    # 每小时轮转，保留24小时
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_file),
        when="H",
        interval=1,
        backupCount=24,
        encoding='utf-8'
    )
    
    # 日期格式轮转
    handler.namer = lambda name: name.replace(".log", f"_{datetime.now().strftime('%Y%m%d_%H')}.log")
    
    # 新的日志格式：时间 - [模块] : [线程] - 等级 : 内容
    formatter = logging.Formatter(
        fmt='%(asctime)s - [%(name)s] : [%(threadName)s] - %(levelname)s : %(message)s',
        datefmt='%y%m%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # 同时输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def cleanup_old_logs(module_name: str, device_name: str = "default", days: int = None):
    """
    清理超期日志和压缩历史日志
    
    Args:
        module_name: 模块名称
        device_name: 设备名称
        days: 保留天数 (如果为 None，则从环境变量 LOG_RETENTION_DAYS 读取)
    """
    if days is None:
        days = int(os.getenv('LOG_RETENTION_DAYS', '7'))
        
    base_log_dir = os.getenv('LOG_DIR', 'logs')
    log_dir = Path(base_log_dir) / module_name / device_name
    
    if not log_dir.exists():
        return
    
    cutoff_time = datetime.now().timestamp() - (days * 86400)
    
    for file in log_dir.iterdir():
        if file.stat().st_mtime < cutoff_time:
            try:
                file.unlink()
            except Exception:
                pass
