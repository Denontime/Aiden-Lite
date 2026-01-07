from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Face:
    """单个人脸数据"""
    box: Dict
    age: Dict
    gender: Dict
    mask: Dict
    subjects: List[Dict]
    embedding: List[float]
    execution_time: Dict
    
    @property
    def is_matched(self) -> bool:
        """是否匹配到人物"""
        return len(self.subjects) > 0
    
    @property
    def best_match_name(self) -> Optional[str]:
        """最佳匹配人物名称"""
        if not self.subjects:
            return None
        best = max(self.subjects, key=lambda x: x.get('similarity', 0))
        return best.get('subject')
    
    @property
    def best_match_similarity(self) -> float:
        """最佳匹配相似度"""
        if not self.subjects:
            return 0.0
        best = max(self.subjects, key=lambda x: x.get('similarity', 0))
        return best.get('similarity', 0.0)


class RecognitionResult:
    """人脸识别结果对象"""
    
    def __init__(self, raw_response: Optional[Dict]):
        self.raw = raw_response
        self.error_code = None
        self.error_message = None
        self.faces: List[Face] = []
        self._parse()
    
    def _parse(self):
        """解析原始响应"""
        if not self.raw:
            return
        
        # 检查错误
        if 'code' in self.raw and self.raw['code'] != 0:
            self.error_code = self.raw['code']
            self.error_message = self.raw.get('message', 'Unknown error')
            return
        
        # 解析人脸数据
        if 'result' in self.raw:
            for face_data in self.raw['result']:
                face = Face(
                    box=face_data.get('box', {}),
                    age=face_data.get('age', {}),
                    gender=face_data.get('gender', {}),
                    mask=face_data.get('mask', {}),
                    subjects=face_data.get('subjects', []),
                    embedding=face_data.get('embedding', []),
                    execution_time=face_data.get('execution_time', {})
                )
                self.faces.append(face)
    
    @property
    def is_error(self) -> bool:
        """是否出错"""
        return self.error_code is not None
    
    @property
    def is_empty(self) -> bool:
        """是否未检测到人脸"""
        return len(self.faces) == 0
    
    @property
    def matched_faces(self) -> List[Face]:
        """已匹配的人脸列表"""
        return [f for f in self.faces if f.is_matched]
    
    @property
    def unmatched_faces(self) -> List[Face]:
        """未匹配的人脸列表"""
        return [f for f in self.faces if not f.is_matched]
    
    @property
    def names(self) -> List[str]:
        """所有匹配的人物名称"""
        names = []
        for face in self.matched_faces:
            name = face.best_match_name
            if name:
                names.append(name)
        return names
    
    @property
    def plugins_versions(self) -> Optional[Dict]:
        """插件版本信息"""
        if self.raw and 'plugins_versions' in self.raw:
            return self.raw['plugins_versions']
        return None
