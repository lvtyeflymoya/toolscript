# 选出名称中带有指定字符的图片

import os
import shutil

def copy_spacial_named_images(source_folder, destination_folder, special_names):
    # 确保目标文件夹存在，如果不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        # 检查文件名是否包含 "special_names" 且是图片文件（这里简单假设图片文件为常见的几种格式）
        if special_names in filename.lower() and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, filename)
            try:
                # 尝试复制文件
                shutil.copy2(source_path, destination_path)
                print(f"Copied {filename} to {destination_folder}")
            except PermissionError:
                print(f"Failed to copy {filename} due to permission issues.")

if __name__ == "__main__":
    special_names = "waterline"
    source_folder = "D:/ImageAnnotation/003-waterline/result-002"
    destination_folder = "D:/ImageAnnotation/003-waterline/result-002/waterline"
    copy_spacial_named_images(source_folder, destination_folder, special_names)
    