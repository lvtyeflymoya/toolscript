# 将eiseg标注后的mask转换为灰度掩膜图
import os
from PIL import Image

def process_images(source_folder, destination_folder):
    # 确保目标文件夹存在，如果不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        # 检查文件是否为图片文件
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # 构建源文件和目标文件的完整路径
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, filename)

            # 打开图片
            image = Image.open(source_path)

            # 将图片转换为灰度图
            gray_image = image.convert('L')

            # 创建一个新的二值图像
            binary_image = gray_image.point(lambda p: 255 if p > 0 else 0)

            # 保存处理后的图片
            binary_image.save(destination_path)
            print(f"Processed and saved {filename} to {destination_folder}")

if __name__ == "__main__":
    source_folder = "D:/ImageAnnotation/chuanzha/wood/mask"
    destination_folder = "D:/ImageAnnotation/chuanzha/wood/mask_grayscale"
    process_images(source_folder, destination_folder)