import logging
import time
from datetime import datetime
from collections import defaultdict
from compreface import CompreFace
from typing import Optional, List, Union
from utils.logger_config import setup_logger
from .recognition_result import RecognitionResult
from .response_logger import ResponseLogger

logger = setup_logger('face_recognition', 'default')
response_logger = ResponseLogger(logger)


class FaceRecognitionModule:
    """人脸识别模块 - 使用 CompreFace"""
    
    def __init__(self, host: str, port: str, api_key: str, 
                 similarity_threshold: float = 0.75,
                 log_cooldown: int = 10):
        """
        初始化人脸识别
        
        Args:
            host: CompreFace 主机 (如 http://localhost)
            port: CompreFace 端口 (如 8000)
            api_key: 识别服务 API Key
            similarity_threshold: 相似度阈值
            log_cooldown: 日志打印冷却时间（秒）
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.similarity_threshold = similarity_threshold
        self.log_cooldown = log_cooldown
        
        # 状态追踪
        self.face_last_appeared = defaultdict(float)  # {name: timestamp}
        self.face_logged = set()  # 已记录日志的人脸
        self.current_faces = set()  # 当前帧检测到的人脸
        
        logger.info(f"初始化参数 - host: {self.host}, port: {self.port}, threshold: {self.similarity_threshold}")
        
        # 初始化 CompreFace
        options = {
            "limit": 0,
            "det_prob_threshold": 0.8,
            "prediction_count": 1,
            "face_plugins": "age,gender,mask",
            "status": False,
        }
        compre_face = CompreFace(self.host, self.port, options)
        # 初始化识别服务
        self.recognition = compre_face.init_face_recognition(self.api_key)
        logger.info(f"✓ 人脸识别服务已初始化 - {self.host}:{self.port}")
    
    def recognize(self, image: Union[str, bytes]) -> Optional[RecognitionResult]:
        """
        识别人脸
        
        Args:
            image: 图像文件路径或图像字节数据
            
        Returns:
            RecognitionResult 对象或 None
        """
        try:
            if isinstance(image, str):
                response_logger.log_request(image, self.host, self.port, self.api_key)
            
            raw_response = self.recognition.recognize(image)
            result = RecognitionResult(raw_response)
            
            if isinstance(image, str):
                response_logger.log_response(result)
                
            self._update_tracking(result)
            return result
        except Exception as e:
            logger.error(f"✗ 识别失败: {str(e)}")
            return None

    def _update_tracking(self, result: RecognitionResult):
        """更新人脸追踪和日志逻辑"""
        previous_faces = self.current_faces.copy()
        self.current_faces.clear()
        current_time = time.time()

        for face in result.matched_faces:
            name = face.best_match_name
            similarity = face.best_match_similarity

            if similarity >= self.similarity_threshold:
                self.current_faces.add(name)
                self.face_last_appeared[name] = current_time

                # 日志去重逻辑
                if name not in self.face_logged:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    logger.info(f"识别到人物: {name}, 相似度: {similarity:.4f}")
                    self.face_logged.add(name)

        # 检查消失的人脸
        disappeared = previous_faces - self.current_faces
        for name in disappeared:
            if current_time - self.face_last_appeared.get(name, 0) > self.log_cooldown:
                self.face_logged.discard(name)
    
    def extract_names(self, result: RecognitionResult) -> List[str]:
        """提取高于阈值的匹配名称"""
        names = []
        for face in result.matched_faces:
            if face.best_match_similarity >= self.similarity_threshold:
                names.append(face.best_match_name)
        return names
