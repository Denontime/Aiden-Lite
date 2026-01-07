import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import os


def setup_logger(module_name: str, device_name: str = "default") -> logging.Logger:
    """
    设置模块化日志记录器
    
    Args:
        module_name: 模块名称 (如 'camera', 'face_recognition')
        device_name: 设备名称 (如 'camera_0', 'default')
    
    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(f"{module_name}_{device_name}")
    logger.setLevel(logging.DEBUG)
    
    # 避免重复处理
    if logger.handlers:
        return logger
    
    # 日志目录
    log_dir = Path("logs") / module_name / device_name
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
    
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # 同时输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def cleanup_old_logs(module_name: str, device_name: str = "default", days: int = 7):
    """
    清理超期日志和压缩历史日志
    
    Args:
        module_name: 模块名称
        device_name: 设备名称
        days: 保留天数
    """
    log_dir = Path("logs") / module_name / device_name
    
    if not log_dir.exists():
        return
    
    cutoff_time = datetime.now().timestamp() - (days * 86400)
    
    for file in log_dir.iterdir():
        if file.stat().st_mtime < cutoff_time:
            try:
                file.unlink()
            except Exception:
                pass
