import uvicorn
from core.config import WEB_HOST, WEB_PORT
from web.app import create_app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    # 设置 1 秒强制关闭超时，防止长连接挂死进程
    uvicorn.run(
        "main:app", 
        host=WEB_HOST, 
        port=WEB_PORT, 
        timeout_graceful_shutdown=1,
        reload=False
    )
