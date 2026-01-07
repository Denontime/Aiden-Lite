"""
摄像头测试脚本
"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.camera import CameraModule


def test_camera():
    """测试摄像头功能"""
    print("🎥 开始测试摄像头...")
    
    camera = CameraModule(camera_index=0)
    
    # 尝试拍照
    success = camera.take_photo("output/test_photo.jpg")
    
    if success:
        print("✅ 摄像头测试成功!")
        print("📸 照片已保存到 output/test_photo.jpg")
    else:
        print("❌ 摄像头测试失败!")
        print("请检查:")
        print("  1. 摄像头是否连接")
        print("  2. 摄像头驱动是否正确安装")
        print("  3. 摄像头权限是否开放")


if __name__ == "__main__":
    test_camera()
