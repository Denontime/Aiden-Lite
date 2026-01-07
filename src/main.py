import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from core.camera import CameraModule
from core.face_recognition import FaceRecognitionModule
from utils.logger_config import setup_logger, cleanup_old_logs

# 加载 .env.actual 文件到环境变量
env_file = Path(__file__).parent.parent / '.env.actual'
if env_file.exists():
    load_dotenv(env_file, override=True)
else:
    raise FileNotFoundError(f".env.actual 文件不存在: {env_file}")

# 初始化主日志
main_logger = setup_logger('main', 'system')

# 从环境变量读取配置
COMPREFACE_HOST = os.getenv('COMPREFACE_HOST', 'http://localhost')
COMPREFACE_PORT = os.getenv('COMPREFACE_PORT', '8000')
COMPREFACE_RECOGNITION_API_KEY = os.getenv('COMPREFACE_RECOGNITION_API_KEY', '')

main_logger.debug(f"从环境变量读取配置 - Host: {COMPREFACE_HOST}, Port: {COMPREFACE_PORT}, API Key: {COMPREFACE_RECOGNITION_API_KEY}")


def main():
    """主程序 - 拍照并识别人脸"""
    main_logger.info("="*50)
    main_logger.info("启动主程序")
    main_logger.info("="*50)
    
    # 检查 API Key
    if not COMPREFACE_RECOGNITION_API_KEY:
        main_logger.error("✗ 错误！不可用的 API Key - COMPREFACE_RECOGNITION_API_KEY 未设置！")
        main_logger.error("请检查 .env.actual 文件是否存在且包含有效的 API Key")
        return
    
    # 清理过旧日志
    cleanup_old_logs('camera', 'camera_0', days=7)
    cleanup_old_logs('face_recognition', 'default', days=7)
    cleanup_old_logs('main', 'system', days=7)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 初始化摄像头
    main_logger.info("初始化摄像头...")
    camera = CameraModule(camera_index=0)
    
    # 拍照
    main_logger.info("开始拍照...")
    photo_path = camera.take_photo(str(output_dir))
    
    if not photo_path:
        main_logger.error("拍照失败！程序退出")
        return
    
    # 初始化人脸识别
    main_logger.info("初始化人脸识别模块...")
    try:
        face_recognition = FaceRecognitionModule(
            host=COMPREFACE_HOST,
            port=COMPREFACE_PORT,
            api_key=COMPREFACE_RECOGNITION_API_KEY
        )
    except Exception as e:
        main_logger.error(f"初始化人脸识别失败: {e}")
        return
    
    # 识别人脸
    main_logger.info("开始识别人脸...")
    result = face_recognition.recognize(photo_path)
    
    if result and not result.is_error:
        names = face_recognition.extract_names(result)
        if names:
            main_logger.info(f"✓ 最终结果: 识别到人物 -> {', '.join(names)}")
        else:
            main_logger.info("未识别到已注册的人物")
    else:
        main_logger.error("识别失败！")
    
    main_logger.info("程序完成")


if __name__ == "__main__":
    main()
