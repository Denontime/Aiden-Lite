from core.config import *
from core.camera import CameraModule
from core.face_recognition import FaceRecognitionModule
from core.visualizer import Visualizer

# 初始化核心组件
camera = CameraModule(
    camera_index=CAMERA_INDEX,
    width=CAMERA_WIDTH,
    height=CAMERA_HEIGHT
)

recognition = FaceRecognitionModule(
    host=COMPREFACE_HOST,
    port=COMPREFACE_PORT,
    api_key=COMPREFACE_RECOGNITION_API_KEY,
    similarity_threshold=SIMILARITY_THRESHOLD,
    log_cooldown=LOG_COOLDOWN
)

visualizer = Visualizer(
    font_path=FONT_PATH,
    font_size=FONT_SIZE,
    box_color=BOX_COLOR,
    box_thickness=BOX_THICKNESS,
    text_color=TEXT_COLOR,
    text_offset_x=TEXT_OFFSET_X,
    text_offset_y=TEXT_OFFSET_Y,
    text_line_height=TEXT_LINE_HEIGHT
)
