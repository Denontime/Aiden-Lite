import logging
from compreface import CompreFace
from typing import Optional, Dict, List
from utils.logger_config import setup_logger

logger = setup_logger('face_recognition', 'default')


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
    
    def recognize(self, image_path: str) -> Optional[Dict]:
        """
        识别人脸
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            识别结果字典或 None
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"发起人脸识别请求")
            logger.info(f"{'='*60}")
            logger.info(f"请求参数 - 图像路径: {image_path}")
            logger.debug(f"API 端点: {self.host}:{self.port}")
            logger.debug(f"使用的 API Key: {self.api_key}")
            
            logger.debug(f"开始识别: {image_path}")
            result = self.recognition.recognize(image_path)
            
            logger.info(f"\n接收服务器响应")
            logger.info(f"{'='*60}")
            
            if result is None:
                logger.error("识别结果为None")
                return None
            
            # 记录完整响应
            logger.debug(f"原始响应类型: {type(result)}")
            logger.debug(f"原始响应内容: {result}")
            logger.info(f"响应状态码: {result.get('code', 'N/A')}")
            logger.info(f"响应消息: {result.get('message', 'N/A')}")
            
            # 检查是否有错误
            if 'code' in result and result['code'] != 0:
                logger.error(f"✗ 服务器返回错误 - Code: {result['code']}, Message: {result.get('message', 'Unknown')}")
                logger.error(f"请检查 API Key 是否为有效的 UUID 格式")
                return result
            
            if 'result' not in result:
                logger.warning("响应中不存在'result'字段")
                logger.debug(f"完整响应内容: {result}")
                return result
            
            faces = result['result']
            face_count = len(faces)
            logger.info(f"✓ 识别完成: 检测到 {face_count} 个人脸")
            
            # 详细记录每个检测到的人脸
            for face_idx, face in enumerate(faces):
                logger.info(f"\n--- 人脸 {face_idx+1} 详情 ---")
                
                # 人脸位置信息
                if 'box' in face:
                    box = face['box']
                    logger.info(f"位置信息 - 概率: {box.get('probability', 'N/A')}, "
                               f"坐标: ({box.get('x_min', 'N/A')}, {box.get('y_min', 'N/A')}) - "
                               f"({box.get('x_max', 'N/A')}, {box.get('y_max', 'N/A')})")
                
                # 人脸特征信息
                if 'age' in face:
                    age = face['age']
                    logger.info(f"年龄估计 - 范围: {age.get('low', 'N/A')}-{age.get('high', 'N/A')}岁, "
                               f"概率: {age.get('probability', 'N/A')}")
                
                if 'gender' in face:
                    gender = face['gender']
                    logger.info(f"性别识别 - 值: {gender.get('value', 'N/A')}, "
                               f"概率: {gender.get('probability', 'N/A')}")
                
                if 'mask' in face:
                    mask = face['mask']
                    logger.info(f"口罩检测 - 值: {mask.get('value', 'N/A')}, "
                               f"概率: {mask.get('probability', 'N/A')}")
                
                # 人脸匹配结果
                subjects = face.get('subjects', [])
                if subjects:
                    logger.info(f"匹配结果数量: {len(subjects)}")
                    for match_idx, subject in enumerate(subjects):
                        name = subject.get('subject', 'N/A')
                        similarity = subject.get('similarity', 'N/A')
                        logger.info(f"  匹配 {match_idx+1}: {name} (相似度: {similarity})")
                else:
                    logger.info("未找到匹配的人脸库中的人物")
                
                # 人脸特征向量
                if 'embedding' in face:
                    embedding = face['embedding']
                    logger.debug(f"特征向量维度: {len(embedding) if isinstance(embedding, list) else 'N/A'}")
                    logger.debug(f"特征向量内容 (前10维): {embedding[:10] if isinstance(embedding, list) else 'N/A'}")
                
                # 执行时间
                if 'execution_time' in face:
                    exec_time = face['execution_time']
                    logger.info(f"各模块执行时间 - "
                               f"detector: {exec_time.get('detector', 'N/A')}ms, "
                               f"age: {exec_time.get('age', 'N/A')}ms, "
                               f"gender: {exec_time.get('gender', 'N/A')}ms, "
                               f"calculator: {exec_time.get('calculator', 'N/A')}ms")
            
            # 插件版本信息
            if 'plugins_versions' in result:
                logger.info(f"使用的插件版本: {result['plugins_versions']}")
            
            logger.info(f"\n识别请求完成\n")
            return result
        except Exception as e:
            logger.error(f"✗ 识别失败: {str(e)}")
            logger.exception("识别异常详情:")
            return None
    
    def extract_names(self, recognition_result: Dict) -> List[str]:
        """
        从识别结果提取人物名称
        
        Args:
            recognition_result: 识别结果
            
        Returns:
            人物名称列表
        """
        names = []
        
        logger.info(f"\n{'='*60}")
        logger.info(f"解析识别结果")
        logger.info(f"{'='*60}")
        
        if not recognition_result:
            logger.error("识别结果为None - 无法解析")
            return names
        
        # 检查错误状态
        if 'code' in recognition_result and recognition_result['code'] != 0:
            logger.error(f"识别结果包含错误 - Code: {recognition_result['code']}, "
                        f"Message: {recognition_result.get('message', 'Unknown')}")
            return names
        
        if 'result' not in recognition_result:
            logger.error("识别结果中不存在'result'字段 - 无法解析")
            logger.debug(f"完整响应内容: {recognition_result}")
            return names
        
        faces = recognition_result['result']
        logger.info(f"总人脸数: {len(faces)}")
        
        if len(faces) == 0:
            logger.info("未检测到任何人脸")
            return names
        
        for idx, face in enumerate(faces):
            logger.info(f"\n处理人脸 {idx+1}/{len(faces)}...")
            subjects = face.get('subjects', [])
            
            if subjects:
                logger.info(f"该人脸有 {len(subjects)} 个匹配候选")
                # 获取相似度最高的人物
                best_match = max(subjects, key=lambda x: x.get('similarity', 0))
                name = best_match.get('subject')
                similarity = best_match.get('similarity', 0)
                
                if name:
                    names.append(name)
                    logger.info(f"✓ 人脸 {idx+1}: {name} (相似度: {similarity:.4f} / {similarity*100:.2f}%)")
                    logger.debug(f"最佳匹配详情 - 姓名: {name}, 相似度: {similarity}")
                    
                    # 记录其他候选
                    if len(subjects) > 1:
                        logger.debug(f"其他候选 (前3个):")
                        for cand_idx, candidate in enumerate(subjects[1:4], 1):
                            cand_name = candidate.get('subject', 'N/A')
                            cand_similarity = candidate.get('similarity', 'N/A')
                            logger.debug(f"  {cand_idx}. {cand_name} (相似度: {cand_similarity})")
                else:
                    logger.warning(f"人脸 {idx+1}: 匹配到的主体名称为空")
            else:
                logger.info(f"✗ 人脸 {idx+1}: 未匹配 (人脸库中无对应人物)")
                logger.debug(f"人脸 {idx+1} 特征 - box: {face.get('box', 'N/A')}, "
                           f"age: {face.get('age', 'N/A')}, "
                           f"gender: {face.get('gender', 'N/A')}")
        
        logger.info(f"\n最终识别结果: 成功识别 {len(names)} 人 -> {names if names else '无匹配'}\n")
        return names
