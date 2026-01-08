import asyncio
import json
import cv2
from pathlib import Path
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from core.init import camera, recognition, visualizer, SIMILARITY_THRESHOLD, FAVICON_PATH
from core.events import shutdown_event, log_queue

router = APIRouter()

# 获取模板目录
BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """提供真实的网站图标"""
    if FAVICON_PATH:
        # 优先从配置的路径寻找
        full_path = Path(__file__).parent.parent.parent / FAVICON_PATH
        if full_path.exists():
            return FileResponse(full_path)
    
    # 兜底从 static 目录寻找
    static_favicon = Path(__file__).parent / "static" / "ico" / "Aiden.png"
    if static_favicon.exists():
        return FileResponse(static_favicon)
        
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
        pass
    except Exception:
        pass
    finally:
        from utils.logger_config import setup_logger
        logger = setup_logger('main', 'system')
        logger.debug("视频流连接已断开")

@router.get("/video_feed")
async def video_feed(request: Request):
    if shutdown_event.is_set():
        return Response(status_code=503)
    return StreamingResponse(
        generate_frames(request), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/logs")
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
                    log_data = await asyncio.wait_for(log_queue.get(), timeout=0.5)
                    yield f"data: {json.dumps(log_data)}\n\n"
                except asyncio.TimeoutError:
                    continue
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
        finally:
            from utils.logger_config import setup_logger
            logger = setup_logger('main', 'system')
            logger.info("日志流连接已断开")
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
