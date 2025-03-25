# 将32位RGBA图片转成24位RGB图片
import os
from PIL import Image

def convert_32bit_to_24bit(folder_path):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否为 JPG 图片
        if filename.lower().endswith('.jpg'):
            file_path = os.path.join(folder_path, filename)
            try:
                # 打开图片
                with Image.open(file_path) as img:
                    # 检查图片是否为 32 位深度（RGBA）
                    if img.mode == 'RGBA':
                        # 将图片从 RGBA 模式转换为 RGB 模式
                        rgb_img = img.convert('RGB')
                        # 保存转换后的图片
                        rgb_img.save(file_path)
                        print(f"Converted {filename} from RGBA to RGB.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    # 请替换为你实际的文件夹路径
    folder_path = "D:/ImageAnnotation/chuanzha/outside_croped_shipmask"
    convert_32bit_to_24bit(folder_path)