import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Optional
from .recognition_result import RecognitionResult, Face

class Visualizer:
    """可视化工具 - 在图像上绘制识别结果（支持中文）"""
    
    def __init__(self, 
                 font_path: str = r"C:/Windows/Fonts/msyh.ttc",
                 font_size: int = 15,
                 box_color: tuple = (0, 255, 0),
                 box_thickness: int = 1,
                 text_color: tuple = (0, 255, 0),
                 text_offset_x: int = 5,
                 text_offset_y: int = 0,
                 text_line_height: int = 18):
        """
        初始化可视化工具
        
        Args:
            font_path: TTF 字体路径
            font_size: 字体大小
            box_color: 框颜色 (B, G, R)
            box_thickness: 框粗细
            text_color: 文本颜色 (R, G, B)
            text_offset_x: 文本水平偏移
            text_offset_y: 文本垂直偏移
            text_line_height: 行高
        """
        self.font_path = font_path
        self.font_size = font_size
        self.box_color = box_color
        self.box_thickness = box_thickness
        self.text_color = text_color
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y
        self.text_line_height = text_line_height
        
        try:
            self.font = ImageFont.truetype(self.font_path, size=self.font_size)
        except Exception:
            self.font = None

    def draw(self, frame: np.ndarray, result: RecognitionResult, similarity_threshold: float = 0.75) -> np.ndarray:
        """
        在帧上绘制所有识别结果
        
        Args:
            frame: 原始 BGR 图像
            result: 识别结果对象
            similarity_threshold: 相似度阈值
            
        Returns:
            处理后的 BGR 图像
        """
        if result is None or not result.faces:
            return frame

        # 1. 先画框 (OpenCV)
        for face in result.faces:
            box = face.box
            if box:
                cv2.rectangle(
                    frame,
                    (box['x_min'], box['y_min']),
                    (box['x_max'], box['y_max']),
                    self.box_color,
                    self.box_thickness
                )

        # 2. 转为 PIL 绘文字
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        for face in result.faces:
            box = face.box
            if not box:
                continue

            x_max, y_min = box['x_max'], box['y_min']
            line_y = y_min + self.text_offset_y
            
            # 基础信息
            info_lines = []
            if face.age:
                info_lines.append(f"年龄: {face.age['low']} - {face.age['high']}")
            if face.gender:
                info_lines.append(f"性别: {face.gender['value']}")
            if face.mask:
                info_lines.append(f"口罩: {face.mask['value']}")

            # 匹配结果
            if face.is_matched:
                similarity = face.best_match_similarity
                if similarity >= similarity_threshold:
                    info_lines.append(f"姓名: {face.best_match_name}")
                    info_lines.append(f"相似度: {similarity:.4f}")
                else:
                    info_lines.append(f"未知 (相似度: {similarity:.4f} < {similarity_threshold})")
            else:
                info_lines.append("未匹配到已知人物")

            # 绘制所有行
            for line in info_lines:
                draw.text(
                    (x_max + self.text_offset_x, line_y),
                    line,
                    font=self.font,
                    fill=self.text_color
                )
                line_y += self.text_line_height

        # 3. 转回 BGR
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
