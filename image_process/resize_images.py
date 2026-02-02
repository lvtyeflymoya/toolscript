import cv2
import os

def resize_images(folder_path, output_folder_path, new_size=(2960,1664)):
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
                # 用OpenCV读取图片
                img = cv2.imread(file_path)
                if img is None:
                    print(f"无法读取图片: {filename}")
                    continue
                # 用INTER_AREA高效缩放
                img_resized = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
                # 构建输出文件的完整路径
                output_file_path = os.path.join(output_folder_path, filename)
                # 保存调整后的图片
                cv2.imwrite(output_file_path, img_resized)
                print(f"已调整大小并保存图片: {filename}")
            except Exception as e:
                print(f"无法处理图片: {filename}, 错误信息: {str(e)}")

# 使用示例
input_folder = 'E:/work/图纸解析/test'
output_folder = 'E:/work/图纸解析/test/resized'
resize_images(input_folder, output_folder)
