import os
from PIL import Image

def convert_jpg_to_single_channel_png(folder_path):
    # 获取文件夹中所有的JPG图片文件
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
    for image_file in image_files:
        # 构建图片的完整路径
        file_path = os.path.join(folder_path, image_file)
        # 打开图片
        with Image.open(file_path) as img:
            # 将图片转换为单通道（灰度图）
            single_channel_img = img.convert('L')
            # 生成新的文件名，将扩展名改为 .png
            new_file_name = os.path.splitext(image_file)[0] + '.png'
            new_file_path = os.path.join(folder_path, new_file_name)
            # 保存转换后的图片
            single_channel_img.save(new_file_path)
            print(f"Converted {image_file} to {new_file_name}")

# 使用示例
# 替换为你的图片文件夹路径
folder_path = 'E:/zhanglelelelelelele/ImageDataSet/Diffusion_Dataset_test/carpet/ground_truth/wood_waterweed'
convert_jpg_to_single_channel_png(folder_path)