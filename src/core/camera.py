import cv2
from pathlib import Path
from typing import Optional, List
import logging
from datetime import datetime
from io import BytesIO
from utils.logger_config import setup_logger

logger = setup_logger('camera', 'camera_0')


class CameraModule:
    """摄像头模块 - 获取和处理摄像头图像"""
    
    def __init__(self, camera_index: int = 0):
        """
        初始化摄像头
        
        Args:
            camera_index: 摄像头索引，0 为默认摄像头
        """
        self.camera_index = camera_index
        self.cap = None
        
    def connect(self) -> bool:
        """连接摄像头"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.error(f"无法打开摄像头 {self.camera_index}")
                return False
            logger.info(f"摄像头 {self.camera_index} 已连接")
            return True
        except Exception as e:
            logger.error(f"连接摄像头失败: {e}")
            return False
    
    def capture_frame(self) -> Optional[object]:
        """
        捕获一帧图像
        
        Returns:
            numpy array 或 None
        """
        if self.cap is None or not self.cap.isOpened():
            logger.error("摄像头未连接")
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.error("无法读取摄像头帧")
            return None
        
        return frame
    
    def save_frame(self, frame: object, output_path: str = "photo.jpg") -> bool:
        """
        保存帧为图像文件
        
        Args:
            frame: 图像帧
            output_path: 输出文件路径
            
        Returns:
            是否保存成功
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(output_path, frame)
            if success:
                logger.info(f"图像已保存: {output_path}")
            else:
                logger.error(f"保存图像失败: {output_path}")
            return success
        except Exception as e:
            logger.error(f"保存图像异常: {e}")
            return False
    
    def take_photo(self, output_dir: str = "output") -> Optional[str]:
        """
        拍照 - 捕获并保存一张照片（使用时间戳命名）
        
        Args:
            output_dir: 输出目录
            
        Returns:
            保存的文件路径或 None
        """
        if not self.connect():
            logger.error("摄像头连接失败")
            return None
        
        frame = self.capture_frame()
        if frame is None:
            logger.error("捕获帧失败")
            return None
        
        # 使用时间戳作为id
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        Path(output_dir).mkdir(exist_ok=True)
        photo_path = f"{output_dir}/photo_{timestamp}.jpg"
        
        success = self.save_frame(frame, photo_path)
        self.release()
        
        if success:
            logger.info(f"✓ 拍照成功: {photo_path}")
            return photo_path
        else:
            logger.error(f"✗ 拍照保存失败: {photo_path}")
            return None
    
    def frame_to_bytes(self, frame: object) -> bytes:
        """
        将帧转换为 JPEG 字节
        
        Args:
            frame: 图像帧
            
        Returns:
            JPEG 字节数据
        """
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    
    def release(self):
        """释放摄像头资源"""
        if self.cap is not None:
            self.cap.release()
            logger.info("摄像头已释放")
