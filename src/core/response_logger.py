import logging
from .recognition_result import RecognitionResult, Face


class ResponseLogger:
    """人脸识别响应日志记录器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, image_path: str, host: str, port: str, api_key: str):
        """记录请求信息"""
        self.logger.info(f"\n{'='*10} 发起人脸识别请求 {'='*10}")
        self.logger.info(f"请求参数 - 图像路径: {image_path}")
        self.logger.debug(f"API 端点: {host}:{port}")
        self.logger.debug(f"使用的 API Key: {api_key}")
    
    def log_response(self, result: RecognitionResult):
        """记录响应信息"""
        self.logger.info(f"\n{'='*10} 接收服务器响应 {'='*10}")
        
        # 记录原始响应信息
        self.logger.debug(f"原始响应类型: {type(result.raw)}")
        self.logger.debug(f"原始响应内容: {result.raw}")
        
        # 检查错误
        if result.is_error:
            self.logger.error(f"✗ 服务器返回错误 - Code: {result.error_code}, Message: {result.error_message}")
            self.logger.error(f"请检查 API Key 是否为有效的 UUID 格式")
            return
        
        # 记录响应状态
        if result.plugins_versions:
            self.logger.info(f"响应状态码: 0")
            self.logger.info(f"使用的插件版本: {result.plugins_versions}")
        
        # 检查人脸数量
        if result.is_empty:
            self.logger.info("未检测到任何人脸")
            return
        
        self.logger.info(f"✓ 识别完成: 检测到 {len(result.faces)} 个人脸")
        self._log_faces(result.faces)
    
    def _log_faces(self, faces: list[Face]):
        """详细记录每个人脸信息"""
        for idx, face in enumerate(faces, 1):
            self.logger.info(f"\n--- 人脸 {idx} 详情 ---")
            
            # 位置信息
            if face.box:
                self.logger.info(f"位置信息 - 概率: {face.box.get('probability', 'N/A')}, "
                               f"坐标: ({face.box.get('x_min', 'N/A')}, {face.box.get('y_min', 'N/A')}) - "
                               f"({face.box.get('x_max', 'N/A')}, {face.box.get('y_max', 'N/A')})")
            
            # 年龄信息
            if face.age:
                self.logger.info(f"年龄估计 - 范围: {face.age.get('low', 'N/A')}-{face.age.get('high', 'N/A')}岁, "
                               f"概率: {face.age.get('probability', 'N/A')}")
            
            # 性别信息
            if face.gender:
                self.logger.info(f"性别识别 - 值: {face.gender.get('value', 'N/A')}, "
                               f"概率: {face.gender.get('probability', 'N/A')}")
            
            # 口罩检测
            if face.mask:
                self.logger.info(f"口罩检测 - 值: {face.mask.get('value', 'N/A')}, "
                               f"概率: {face.mask.get('probability', 'N/A')}")
            
            # 匹配结果
            if face.is_matched:
                self.logger.info(f"匹配结果数量: {len(face.subjects)}")
                self.logger.info(f"  最佳匹配: {face.best_match_name} (相似度: {face.best_match_similarity:.4f})")
                if len(face.subjects) > 1:
                    self.logger.debug(f"其他候选 (前3个):")
                    for cand_idx, candidate in enumerate(face.subjects[1:4], 1):
                        cand_name = candidate.get('subject', 'N/A')
                        cand_similarity = candidate.get('similarity', 'N/A')
                        self.logger.debug(f"  {cand_idx}. {cand_name} (相似度: {cand_similarity})")
            else:
                self.logger.info("匹配结果: 未找到匹配的人物")
            
            # 特征向量
            if face.embedding:
                self.logger.debug(f"特征向量维度: {len(face.embedding)}")
                self.logger.debug(f"特征向量内容 (前10维): {face.embedding[:10]}")
            
            # 执行时间
            if face.execution_time:
                self.logger.info(f"各模块执行时间 - "
                               f"detector: {face.execution_time.get('detector', 'N/A')}ms, "
                               f"age: {face.execution_time.get('age', 'N/A')}ms, "
                               f"gender: {face.execution_time.get('gender', 'N/A')}ms, "
                               f"calculator: {face.execution_time.get('calculator', 'N/A')}ms")
        
        self.logger.info(f"\n识别请求完成\n")
    
    def log_extraction_result(self, result: RecognitionResult):
        """记录结果提取信息"""
        self.logger.info(f"\n{'='*10} 解析识别结果 {'='*10}")
        
        if result.is_error:
            self.logger.error(f"识别结果包含错误 - Code: {result.error_code}, Message: {result.error_message}")
            return
        
        if result.is_empty:
            self.logger.info("未检测到任何人脸")
            return
        
        self.logger.info(f"总人脸数: {len(result.faces)}")
        self.logger.info(f"已匹配: {len(result.matched_faces)}, 未匹配: {len(result.unmatched_faces)}")
        
        # 已匹配的人脸
        for idx, face in enumerate(result.matched_faces, 1):
            self.logger.info(f"✓ 人脸 {idx}: {face.best_match_name} (相似度: {face.best_match_similarity:.4f} / {face.best_match_similarity*100:.2f}%)")
        
        # 未匹配的人脸
        for idx, face in enumerate(result.unmatched_faces, 1):
            self.logger.info(f"✗ 人脸 {len(result.matched_faces) + idx}: 未匹配 (人脸库中无对应人物)")
        
        self.logger.info(f"\n最终识别结果: 成功识别 {len(result.names)} 人 -> {result.names if result.names else '无匹配'}\n")
