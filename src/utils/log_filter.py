import logging
import json
from datetime import datetime
from core.events import log_queue, main_loop

class LogFilter(logging.Filter):
    """自定义日志过滤器，将识别日志推送到队列"""
    def filter(self, record):
        # 支持多种日志名称格式，只要包含识别关键信息
        if ('识别到人物' in record.getMessage() or '识别到人物' in str(record.msg)):
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_data = {"timestamp": timestamp, "message": record.getMessage()}
            
            from core import events
            if events.main_loop:
                events.main_loop.call_soon_threadsafe(log_queue.put_nowait, log_data)
        return True

def setup_log_filtering():
    """将过滤器添加到识别模块的 logger"""
    from core.face_recognition import logger as recognition_logger
    recognition_logger.addFilter(LogFilter())
