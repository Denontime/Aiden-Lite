import asyncio
import signal
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core import events
from core.init import camera
from utils.logger_config import setup_logger, cleanup_old_logs
from utils.log_filter import setup_log_filtering
from web.router import router

main_logger = setup_logger('main', 'sys')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """管理系统生命周期"""
    events.main_loop = asyncio.get_running_loop()
    
    # 抢先拦截信号，打破 Uvicorn 的优雅关闭死锁
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    
    def handle_quick_exit(sig, frame):
        if events.main_loop:
            events.main_loop.call_soon_threadsafe(events.shutdown_event.set)
        if callable(original_sigint_handler):
            original_sigint_handler(sig, frame)

    signal.signal(signal.SIGINT, handle_quick_exit)
    signal.signal(signal.SIGTERM, handle_quick_exit)

    main_logger.info("正在执行启动序列...")
    try:
        cleanup_old_logs('camera', 'camera_0')
        cleanup_old_logs('face_recognition', 'default')
        cleanup_old_logs('main', 'sys')
        
        # 设置日志过滤
        setup_log_filtering()
        
        # 启动硬件
        camera.start()
        main_logger.info("✓ 系统组件已成功启动")
    except Exception as e:
        main_logger.error(f"✗ 启动过程中出现错误: {e}")
        
    yield
    
    main_logger.info(f"{'-'*10} 系统关闭序列启动 {'-'*10}")
    main_logger.info("正在清理硬件资源...")
    camera.stop()
    main_logger.info("✓ 系统组件已安全关闭")
    main_logger.info(f"{'-'*10} 系统关闭序列完成 {'-'*10}")

def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""
    app = FastAPI(title="Aiden-Lite Smart Manager", lifespan=lifespan)
    
    # 挂载静态文件
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        
    app.include_router(router)
    return app
