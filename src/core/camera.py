import cv2
import threading
import time
from pathlib import Path
from typing import Optional, List, Generator
from datetime import datetime
from utils.logger_config import setup_logger

logger = setup_logger('camera', 'cam0')


class CameraModule:
    """摄像头模块 - 支持线程化捕获和视频流"""
    
    def __init__(self, camera_index: int = 0, width: int = 1280, height: int = 720):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.is_running = False
        self.thread = None
        self.lock = threading.Lock()
        
    def connect(self) -> bool:
        """连接摄像头"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # 设置分辨率
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            if not self.cap.isOpened():
                logger.error(f"无法打开摄像头 {self.camera_index}")
                return False
            
            # 获取实际分辨率
            actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.info(f"摄像头 {self.camera_index} 已连接, 分辨率: {actual_w}x{actual_h}")
            return True
        except Exception as e:
            logger.error(f"连接摄像头失败: {e}")
            return False
    
    def start(self):
        """启动后台捕获线程"""
        if self.is_running:
            return
        
        if self.cap is None and not self.connect():
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True, name="CameraCaptureThread")
        self.thread.start()
        logger.info(f"摄像头捕获线程 '{self.thread.name}' (ID: {self.thread.ident}) 已启动")

    def _capture_loop(self):
        """后台捕获循环"""
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
            else:
                logger.warning("捕获帧失败，尝试重新连接...")
                time.sleep(1)
                self.connect()
            time.sleep(0.01)  # 防止占用过多 CPU

    def get_frame(self) -> Optional[object]:
        """获取当前最新帧"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def capture_frame(self) -> Optional[object]:
        """同步捕获一帧（兼容旧代码）"""
        if self.is_running:
            return self.get_frame()
            
        if self.cap is None or not self.cap.isOpened():
            if not self.connect():
                return None
        
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def save_frame(self, frame: object, output_path: str = "photo.jpg") -> bool:
        """保存帧为图像文件"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(output_path, frame)
            if success:
                logger.info(f"图像已保存: {output_path}")
            return success
        except Exception as e:
            logger.error(f"保存图像异常: {e}")
            return False
    
    def take_photo(self, output_dir: str = "output") -> Optional[str]:
        """拍照并保存"""
        frame = self.capture_frame()
        if frame is None:
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        Path(output_dir).mkdir(exist_ok=True)
        photo_path = f"{output_dir}/photo_{timestamp}.jpg"
        
        if self.save_frame(frame, photo_path):
            logger.info(f"✓ 拍照成功: {photo_path}")
            return photo_path
        return None
    
    def get_video_stream(self) -> Generator[bytes, None, None]:
        """生成 MJPEG 视频流字节"""
        while self.is_running:
            frame = self.get_frame()
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.04)  # 约 25 FPS

    def frame_to_bytes(self, frame: object) -> bytes:
        """将帧转换为 JPEG 字节"""
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    
    def stop(self):
        """停止捕获"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.release()

    def release(self):
        """释放摄像头资源"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("摄像头已释放")
