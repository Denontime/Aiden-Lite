"""基于官方 webcam 识别 demo，增加 TTF 字体支持以正确显示中文名称。

运行示例（在 sdk/compreface-python-sdk 目录下）：
    python -m tests.webcam_recognition_cn_demo --api-key YOUR_API_KEY --host http://localhost --port 8000
"""

import argparse
import time
from threading import Thread
from collections import defaultdict
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from compreface import CompreFace
from compreface.service import RecognitionService

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-key",
        help="CompreFace recognition service API key",
        type=str,
        default="1d7ff619-9cac-4f10-b08f-fbf3436dfde1",
    )
    parser.add_argument("--host", help="CompreFace host", type=str, default="http://localhost")
    parser.add_argument("--port", help="CompreFace port", type=str, default="8000")
    parser.add_argument(
        "--font-path",
        help="TTF 字体路径，用于绘制中文（默认使用系统微软雅黑）",
        type=str,
        default=r"C:/Windows/Fonts/msyh.ttc",
    )
    parser.add_argument(
        "--font-size",
        help="字体大小（像素）",
        type=int,
        default=15,
    )
    parser.add_argument(
        "--box-color",
        help="人脸框颜色 (B,G,R 格式)",
        type=str,
        default="0,255,0",
    )
    parser.add_argument(
        "--box-thickness",
        help="人脸框线条粗细（像素）",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--text-color",
        help="文本颜色 (R,G,B 格式)",
        type=str,
        default="0,255,0",
    )
    parser.add_argument(
        "--text-offset-x",
        help="文本水平偏移（相对于框右上角）",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--text-offset-y",
        help="文本垂直起始偏移（相对于框上边界）",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--text-line-height",
        help="文本行间距（像素）",
        type=int,
        default=15,
    )
    parser.add_argument(
        "--face-log-cooldown",
        help="人脸识别日志冷却时间（秒），防止重复打印",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--similarity-threshold",
        help="相似度阈值（0.0-1.0），低于此值的识别结果将被忽略",
        type=float,
        default=0.99,
    )
    return parser.parse_args()


class ThreadedCamera:
    def __init__(self, api_key: str, host: str, port: str, font_path: str, font_size: int,
                 box_color: tuple, box_thickness: int, text_color: tuple,
                 text_offset_x: int, text_offset_y: int, text_line_height: int,
                 face_log_cooldown: int, similarity_threshold: float):
        self.active = True
        self.results = []
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        # 配置参数
        self.box_color = box_color
        self.box_thickness = box_thickness
        self.text_color = text_color
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y
        self.text_line_height = text_line_height
        self.face_log_cooldown = face_log_cooldown
        self.similarity_threshold = similarity_threshold
        
        # 人脸识别日志追踪
        self.face_last_appeared = defaultdict(float)  # {subject_name: last_appeared_timestamp}
        self.face_logged = set()  # 已打印过日志的人脸名称
        self.current_faces = set()  # 当前帧中的人脸名称

        # 初始化 CompreFace，启用 age / gender 插件
        compre_face: CompreFace = CompreFace(
            host,
            port,
            {
                "limit": 0,
                "det_prob_threshold": 0.8,
                "prediction_count": 1,
                "face_plugins": "age,gender,mask",
                "status": False,
            },
        )

        self.recognition: RecognitionService = compre_face.init_face_recognition(api_key)

        # 初始化 TTF 字体
        self.font = self._load_font(font_path, font_size)

        self.FPS = 1 / 30

        # Start frame retrieval thread
        self.thread = Thread(target=self.show_frame, args=())
        self.thread.daemon = True
        self.thread.start()

    @staticmethod
    def _load_font(font_path: str, size: int = 20):
        """加载 TTF 字体，失败则返回 None。"""
        try:
            font = ImageFont.truetype(font_path, size=size)
            print(f"使用 TTF 字体绘制中文: {font_path}")
            return font
        except Exception as e:  # noqa: BLE001
            print(f"加载 TTF 字体失败: {e}")
            return None

    def draw_text(self, draw: ImageDraw.ImageDraw, text: str, org):
        """统一文本绘制接口，使用 PIL+TTF 支持中文。"""
        if self.font is not None:
            draw.text(org, text, font=self.font, fill=self.text_color)
        else:
            # 没有字体时退回 PIL 默认字体（中文可能显示不完整）
            draw.text(org, text, fill=self.text_color)

    def show_frame(self):
        print("Started")
        while self.capture.isOpened():
            status, frame_raw = self.capture.read()
            if not status:
                continue

            self.frame = cv2.flip(frame_raw, 1)
            
            # 重置当前帧的人脸集合
            previous_faces = self.current_faces.copy()
            self.current_faces.clear()

            if self.results:
                results = self.results
                for result in results:
                    box = result.get("box")
                    if box:
                        x_min = box["x_min"]
                        y_min = box["y_min"]
                        x_max = box["x_max"]
                        y_max = box["y_max"]

                        # 先画框（在 OpenCV 图像上）
                        cv2.rectangle(
                            img=self.frame,
                            pt1=(x_min, y_min),
                            pt2=(x_max, y_max),
                            color=self.box_color,
                            thickness=self.box_thickness,
                        )

            # 转为 PIL 图像以绘制中文（此时 frame 已经包含人脸框）
            pil_img = Image.fromarray(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)

            if self.results:
                results = self.results
                for result in results:
                    box = result.get("box")
                    age = result.get("age")
                    gender = result.get("gender")
                    mask = result.get("mask")
                    subjects = result.get("subjects")
                    if box:
                        x_min = box["x_min"]
                        y_min = box["y_min"]
                        x_max = box["x_max"]
                        y_max = box["y_max"]

                        line_y = y_min + self.text_offset_y
                        if age:
                            age_text = f"年龄: {age['low']} - {age['high']}"
                            self.draw_text(draw, age_text, (x_max + self.text_offset_x, line_y))
                            line_y += self.text_line_height
                        if gender:
                            gender_text = f"性别: {gender['value']}"
                            self.draw_text(draw, gender_text, (x_max + self.text_offset_x, line_y))
                            line_y += self.text_line_height
                        if mask:
                            mask_text = f"口罩: {mask['value']}"
                            self.draw_text(draw, mask_text, (x_max + self.text_offset_x, line_y))
                            line_y += self.text_line_height

                        if subjects:
                            subjects = sorted(subjects, key=lambda k: k["similarity"], reverse=True)
                            top = subjects[0]
                            subject_name = top['subject']
                            similarity = top['similarity']
                            
                            # 检查相似度阈值
                            if similarity < self.similarity_threshold:
                                no_match_text = f"未知人物 (相似度: {similarity:.4f} < {self.similarity_threshold})"
                                self.draw_text(draw, no_match_text, (x_max + self.text_offset_x, line_y))
                                continue
                            
                            # 记录当前帧出现的人脸
                            self.current_faces.add(subject_name)
                            current_time = time.time()
                            self.face_last_appeared[subject_name] = current_time
                            
                            # 第一次出现，打印日志
                            if subject_name not in self.face_logged:
                                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                print(f"[{timestamp}] 识别到人物: {subject_name}, 相似度: {similarity:.4f}")
                                self.face_logged.add(subject_name)
                            
                            subject_text = f"姓名: {subject_name}"
                            similarity_text = f"相似度: {similarity:.4f}"
                            self.draw_text(draw, subject_text, (x_max + self.text_offset_x, line_y))
                            line_y += self.text_line_height
                            self.draw_text(draw, similarity_text, (x_max + self.text_offset_x, line_y))
                        else:
                            no_face_text = "未匹配到已知人物"
                            self.draw_text(draw, no_face_text, (x_max + self.text_offset_x, line_y))

            # 将 PIL 图像转回 OpenCV 格式
            self.frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            # 检查消失的人脸，超过冷却时间后重置状态
            current_time = time.time()
            disappeared_faces = previous_faces - self.current_faces
            for face_name in disappeared_faces:
                last_appeared = self.face_last_appeared.get(face_name, 0)
                if current_time - last_appeared > self.face_log_cooldown:
                    # 超过冷却时间，允许下次重新打印
                    self.face_logged.discard(face_name)

            cv2.imshow("CompreFace Demo", self.frame)
            time.sleep(self.FPS)

            if cv2.waitKey(1) & 0xFF == 27:
                self.capture.release()
                cv2.destroyAllWindows()
                self.active = False

    def is_active(self):
        return self.active

    def update(self):
        if not hasattr(self, "frame"):
            return

        _, im_buf_arr = cv2.imencode(".jpg", self.frame)
        byte_im = im_buf_arr.tobytes()
        data = self.recognition.recognize(byte_im)
        self.results = data.get("result")


if __name__ == "__main__":
    args = parse_arguments()
    
    # 解析颜色参数
    box_color = tuple(map(int, args.box_color.split(',')))
    text_color = tuple(map(int, args.text_color.split(',')))
    
    cam = ThreadedCamera(
        args.api_key, 
        args.host, 
        args.port, 
        args.font_path,
        args.font_size,
        box_color,
        args.box_thickness,
        text_color,
        args.text_offset_x,
        args.text_offset_y,
        args.text_line_height,
        args.face_log_cooldown,
        args.similarity_threshold
    )
    while cam.is_active():
        cam.update()
