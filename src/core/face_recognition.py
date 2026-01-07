import logging
from compreface import CompreFace
from typing import Optional
from utils.logger_config import setup_logger
from .recognition_result import RecognitionResult
from .response_logger import ResponseLogger

logger = setup_logger('face_recognition', 'default')
response_logger = ResponseLogger(logger)


class FaceRecognitionModule:
    """人脸识别模块 - 使用 CompreFace"""
    
    def __init__(self, host: str, port: str, api_key: str):
        """
        初始化人脸识别
        
        Args:
            host: CompreFace 主机 (如 http://localhost)
            port: CompreFace 端口 (如 8000)
            api_key: 识别服务 API Key
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        
        logger.info(f"初始化参数 - host: {self.host}, port: {self.port}")
        logger.debug(f"API Key: {self.api_key}")
        
        # 初始化 CompreFace
        compre_face = CompreFace(self.host, self.port)
        # 初始化识别服务
        self.recognition = compre_face.init_face_recognition(self.api_key)
        logger.info(f"✓ 人脸识别服务已初始化 - {self.host}:{self.port}")
    
    def recognize(self, image_path: str) -> Optional[RecognitionResult]:
        """
        识别人脸
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            RecognitionResult 对象或 None
        """
        try:
            response_logger.log_request(image_path, self.host, self.port, self.api_key)
            
            raw_response = self.recognition.recognize(image_path)
            result = RecognitionResult(raw_response)
            
            response_logger.log_response(result)
            return result
        except Exception as e:
            logger.error(f"✗ 识别失败: {str(e)}")
            logger.exception("识别异常详情:")
            return None
    
    def extract_names(self, result: RecognitionResult) -> list[str]:
        """
        从识别结果提取人物名称
        
        Args:
            result: RecognitionResult 对象
            
        Returns:
            人物名称列表
        """
        response_logger.log_extraction_result(result)
        return result.names
