#将一个文件夹中的图片按指定数字开始重命名,或在后面加上某个字符串
import os

def rename_images(folder_path, start_number):
    # 获取文件夹中所有的图片文件
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
    image_files.sort()  # 按文件名排序

    # 按指定数字开始重命名图片
    for i, image_file in enumerate(image_files, start=start_number):
        file_extension = os.path.splitext(image_file)[1]
        new_name = f"{i:03d}{file_extension}"
        old_path = os.path.join(folder_path, image_file)
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed {image_file} to {new_name}")

def add_mask_suffix_to_images(folder_path):
    # 获取文件夹中所有的图片文件
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
    # 遍历图片文件并添加 _mask 后缀
    for image_file in image_files:
        file_name, file_extension = os.path.splitext(image_file)
        # new_name = f"{file_name}_mask{file_extension}"
        new_name = f"{file_name}{file_extension}"
        old_path = os.path.join(folder_path, image_file)
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed {image_file} to {new_name}")

# 使用示例
folder_path = 'D:/ImageAnnotation/Diffusion_Dataset_test/carpet/test/wood_waterweed'  # 替换为你的图片文件夹路径
start_number = 1  # 替换为你想要开始的数字
rename_images(folder_path, start_number)
# folder_path = 'E:/zhanglelelelelelele/ImageDataSet/Diffusion_Dataset_test/carpet/ground_truth/wood_waterweed'  # 替换为你的图片文件夹路径
add_mask_suffix_to_images(folder_path)

