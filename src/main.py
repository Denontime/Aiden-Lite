import os
import asyncio
import json
import logging
import cv2
import signal
from pathlib import Path
from datetime import datetime
from typing import List
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from core.camera import CameraModule
from core.face_recognition import FaceRecognitionModule
from core.visualizer import Visualizer
from utils.logger_config import setup_logger, cleanup_old_logs

# 配置根日志
main_logger = setup_logger('main', 'system')

# 加载环境变量
env_file = Path(__file__).parent.parent / '.env.actual'
if env_file.exists():
    load_dotenv(env_file, override=True)
else:
    main_logger.warning(f".env.actual 文件不存在: {env_file}")

# 配置常量
# [CAMERA]
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', '1280'))
CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', '720'))

# [COMPREFACE]
COMPREFACE_HOST = os.getenv('COMPREFACE_HOST', 'http://localhost')
COMPREFACE_PORT = os.getenv('COMPREFACE_PORT', '8000')
COMPREFACE_RECOGNITION_API_KEY = os.getenv('COMPREFACE_RECOGNITION_API_KEY', '')

# [RECOGNITION]
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.98'))
LOG_COOLDOWN = int(os.getenv('LOG_COOLDOWN', '10'))

# [VISUALIZATION]
FONT_PATH = os.getenv('FONT_PATH', 'C:/Windows/Fonts/msyh.ttc')
FONT_SIZE = int(os.getenv('FONT_SIZE', '15'))
BOX_THICKNESS = int(os.getenv('BOX_THICKNESS', '1'))
TEXT_OFFSET_X = int(os.getenv('TEXT_OFFSET_X', '5'))
TEXT_OFFSET_Y = int(os.getenv('TEXT_OFFSET_Y', '0'))
TEXT_LINE_HEIGHT = int(os.getenv('TEXT_LINE_HEIGHT', '18'))

def parse_tuple(env_val: str, default: tuple) -> tuple:
    if not env_val:
        return default
    try:
        return tuple(map(int, env_val.split(',')))
    except Exception:
        return default

BOX_COLOR = parse_tuple(os.getenv('BOX_COLOR'), (0, 255, 0))
TEXT_COLOR = parse_tuple(os.getenv('TEXT_COLOR'), (0, 255, 0))

# [WEB]
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.getenv('WEB_PORT', '8080'))
FAVICON_PATH = os.getenv('FAVICON_PATH', '')

# 初始化组件
camera = CameraModule(
    camera_index=CAMERA_INDEX,
    width=CAMERA_WIDTH,
    height=CAMERA_HEIGHT
)
recognition = FaceRecognitionModule(
    host=COMPREFACE_HOST,
    port=COMPREFACE_PORT,
    api_key=COMPREFACE_RECOGNITION_API_KEY,
    similarity_threshold=SIMILARITY_THRESHOLD,
    log_cooldown=LOG_COOLDOWN
)
visualizer = Visualizer(
    font_path=FONT_PATH,
    font_size=FONT_SIZE,
    box_color=BOX_COLOR,
    box_thickness=BOX_THICKNESS,
    text_color=TEXT_COLOR,
    text_offset_x=TEXT_OFFSET_X,
    text_offset_y=TEXT_OFFSET_Y,
    text_line_height=TEXT_LINE_HEIGHT
)

# 获取模板目录
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))

# 用于日志流的消息队列
log_queue = asyncio.Queue()
main_loop = None

class LogFilter(logging.Filter):
    """自定义日志过滤器，将识别日志推送到队列"""
    def filter(self, record):
        # 支持多种日志名称格式，只要包含识别关键信息
        if ('识别到人物' in record.getMessage() or '识别到人物' in str(record.msg)):
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_data = {"timestamp": timestamp, "message": record.getMessage()}
            
            if main_loop:
                main_loop.call_soon_threadsafe(log_queue.put_nowait, log_data)
        return True

# 添加过滤器到识别模块的 logger
from core.face_recognition import logger as recognition_logger
recognition_logger.addFilter(LogFilter())

# 用于同步关闭的事件
shutdown_event = asyncio.Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """管理系统生命周期"""
    global main_loop
    main_loop = asyncio.get_running_loop()
    
    # 抢先拦截信号，打破 Uvicorn 的优雅关闭死锁
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    
    def handle_quick_exit(sig, frame):
        # 1. 立即设置事件，让所有 StreamingResponse 退出循环
        if main_loop:
            main_loop.call_soon_threadsafe(shutdown_event.set)
        
        # 2. 调用原生的 Uvicorn 信号处理器，让它按标准流程关闭服务器
        if callable(original_sigint_handler):
            original_sigint_handler(sig, frame)

    signal.signal(signal.SIGINT, handle_quick_exit)
    signal.signal(signal.SIGTERM, handle_quick_exit)

    main_logger.info("正在执行启动序列...")
    try:
        cleanup_old_logs('camera', 'camera_0')
        cleanup_old_logs('face_recognition', 'default')
        cleanup_old_logs('main', 'system')
        camera.start()
        main_logger.info("✓ 系统组件已成功启动")
    except Exception as e:
        main_logger.error(f"✗ 启动过程中出现错误: {e}")
        
    yield
    
    main_logger.info("正在清理硬件资源...")
    camera.stop()
    main_logger.info("✓ 系统组件已安全关闭")
    main_logger.info("="*40)

# 初始化组件
app = FastAPI(title="Aiden-Lite Smart Manager", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """提供真实的网站图标"""
    if FAVICON_PATH:
        full_path = Path(__file__).parent.parent / FAVICON_PATH
        if full_path.exists():
            return FileResponse(full_path)
    return Response(status_code=204)

async def generate_frames(request: Request):
    """视频流生成器，包含实时识别和绘制"""
    try:
        while not shutdown_event.is_set():
            if await request.is_disconnected():
                break
                
            if not camera.is_running:
                break
            
            frame = camera.get_frame()
            if frame is not None:
                img_bytes = camera.frame_to_bytes(frame)
                result = await asyncio.to_thread(recognition.recognize, img_bytes)
                processed_frame = visualizer.draw(frame, result, SIMILARITY_THRESHOLD)
                
                _, buffer = cv2.imencode('.jpg', processed_frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
            await asyncio.sleep(0.04)
    except (asyncio.CancelledError, KeyboardInterrupt):
        # 捕获退出时的正常异常，不打印堆栈
        pass
    except Exception as e:
        main_logger.debug(f"视频流生成器捕获到非预期异常: {e}")
    finally:
        main_logger.debug("视频流连接已断开")

@app.get("/video_feed")
async def video_feed(request: Request):
    if shutdown_event.is_set():
        return Response(status_code=503)
    return StreamingResponse(
        generate_frames(request), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/logs")
async def log_stream(request: Request):
    """SSE 日志流接口"""
    if shutdown_event.is_set():
        return Response(status_code=503)
        
    async def event_generator():
        try:
            while not shutdown_event.is_set():
                if await request.is_disconnected():
                    break
                
                try:
                    # 将超时缩短，提高响应灵敏度
                    log_data = await asyncio.wait_for(log_queue.get(), timeout=0.5)
                    yield f"data: {json.dumps(log_data)}\n\n"
                except asyncio.TimeoutError:
                    continue
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
        finally:
            main_logger.info("日志流连接已断开")
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    # 设置 1 秒强制关闭超时，防止长连接挂死进程
    uvicorn.run(app, host=WEB_HOST, port=WEB_PORT, timeout_graceful_shutdown=1)
