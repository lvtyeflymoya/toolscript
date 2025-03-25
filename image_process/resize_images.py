from PIL import Image
import os

def resize_images(folder_path, output_folder_path, new_size=(513, 513)):
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 构建文件的完整路径
        file_path = os.path.join(folder_path, filename)
        
        # 检查文件是否为图片
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            try:
                # 打开图片
                with Image.open(file_path) as img:
                    # 调整图片大小
                    img_resized = img.resize(new_size, Image.LANCZOS)
                    # 构建输出文件的完整路径
                    output_file_path = os.path.join(output_folder_path, filename)
                    # 保存调整后的图片
                    img_resized.save(output_file_path)
                    print(f"已调整大小并保存图片: {filename}")
            except Exception as e:
                print(f"无法处理图片: {filename}, 错误信息: {str(e)}")

# 使用示例
input_folder = 'F:\dataset\\003-waterline\\002-fine\SegmentationClass'
output_folder = 'F:\dataset\\003-waterline\\002-coarse\SegmentationClass'
resize_images(input_folder, output_folder)
