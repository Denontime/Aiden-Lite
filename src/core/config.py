import os
from pathlib import Path
from dotenv import load_dotenv
from utils.logger_config import setup_logger

# 配置根日志
config_logger = setup_logger('config', 'sys')

# 基础路径
BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BASE_DIR / '.env.actual'

# 加载环境变量
if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)
else:
    config_logger.warning(f".env.actual 文件不存在: {ENV_FILE}")

def parse_tuple(env_val: str, default: tuple) -> tuple:
    if not env_val:
        return default
    try:
        return tuple(map(int, env_val.split(',')))
    except Exception:
        return default

# [CAMERA]
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', '1280'))
CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', '720'))

# [COMPREFACE]
COMPREFACE_HOST = os.getenv('COMPREFACE_HOST', 'http://localhost')
COMPREFACE_PORT = os.getenv('COMPREFACE_PORT', '8000')
COMPREFACE_RECOGNITION_API_KEY = os.getenv('COMPREFACE_RECOGNITION_API_KEY', '')

# [RECOGNITION]
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.98'))
LOG_COOLDOWN = int(os.getenv('LOG_COOLDOWN', '10'))

# [VISUALIZATION]
FONT_PATH = os.getenv('FONT_PATH', 'C:/Windows/Fonts/msyh.ttc')
FONT_SIZE = int(os.getenv('FONT_SIZE', '15'))
BOX_THICKNESS = int(os.getenv('BOX_THICKNESS', '1'))
TEXT_OFFSET_X = int(os.getenv('TEXT_OFFSET_X', '5'))
TEXT_OFFSET_Y = int(os.getenv('TEXT_OFFSET_Y', '0'))
TEXT_LINE_HEIGHT = int(os.getenv('TEXT_LINE_HEIGHT', '18'))
BOX_COLOR = parse_tuple(os.getenv('BOX_COLOR'), (0, 255, 0))
TEXT_COLOR = parse_tuple(os.getenv('TEXT_COLOR'), (0, 255, 0))

# [WEB]
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.getenv('WEB_PORT', '8080'))
FAVICON_PATH = os.getenv('FAVICON_PATH', '')
