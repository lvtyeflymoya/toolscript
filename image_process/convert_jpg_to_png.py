# 将一个文件夹中的jpg格式图片转成png
import os
from PIL import Image

def convert_jpg_to_png(source_folder, destination_folder):
    # 确保目标文件夹存在，如果不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        # 检查文件是否为PNG格式（原代码实际是转换 PNG 到 JPG）
        if filename.lower().endswith('.jpeg'):
            # 构建源文件的完整路径
            source_path = os.path.join(source_folder, filename)
            # 提取文件名（不含扩展名）
            base_name = os.path.splitext(filename)[0]
            # 构建目标文件的完整路径，将扩展名改为 .png
            destination_path = os.path.join(destination_folder, f"{base_name}.jpg")

            # 打开PNG图片
            image = Image.open(source_path)
            
            # 新增：将 RGBA/P 模式转换为 RGB 模式以兼容 JPG 格式
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # 保存为JPG图片（修正扩展名）
            image.save(destination_path, quality=95)  # 添加质量参数
            print(f"Converted {filename} to {base_name}.png and saved to {destination_folder}")

if __name__ == "__main__":
    # 请替换为你实际的源文件夹路径
    source_folder = "E:/dataset/ship-平视-0721"
    # 请替换为你实际的目标文件夹路径
    destination_folder = "E:/dataset/ship-平视-0721jpg"
    convert_jpg_to_png(source_folder, destination_folder)