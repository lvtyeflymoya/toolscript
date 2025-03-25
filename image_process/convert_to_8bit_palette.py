from PIL import Image
import cv2
import numpy as np

def modify_palette_image(image_path, output_path):
    # 读取图像为8位调色板图像
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    # 检查图像是否成功读取
    if image is None:
        raise ValueError("无法读取图像文件")
    
    # 将OpenCV图像转换为PIL图像
    pil_image = Image.fromarray(image, mode='P')
    
    # 创建调色板
    palette = np.zeros((256, 3), dtype=np.uint8)
    palette[0] = (0, 0, 0)  # 像素值为0的像素改成黑色
    palette[1] = (128, 0, 0)  # 像素值为1的像素改成红色
    palette[2] = (0, 128, 0)  # 像素值为2的像素改成绿色
    
    # 将PIL图像的调色板设置为新的调色板
    pil_image.putpalette(palette.flatten())
    
    # 保存为8位深度的PNG图像
    pil_image.save(output_path, optimize=True, bits=8)

