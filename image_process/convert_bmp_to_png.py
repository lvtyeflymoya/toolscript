# 将一个文件夹中的BMP格式图片转成PNG
import os
from PIL import Image

def convert_bmp_to_png(source_folder, destination_folder):
    # 确保目标文件夹存在，如果不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        # 检查文件是否为BMP格式
        if filename.lower().endswith('.bmp'):
            # 构建源文件的完整路径
            source_path = os.path.join(source_folder, filename)
            # 提取文件名（不含扩展名）
            base_name = os.path.splitext(filename)[0]
            # 构建目标文件的完整路径，将扩展名改为 .png
            destination_path = os.path.join(destination_folder, f"{base_name}.png")
            
            try:
                # 打开BMP图片
                image = Image.open(source_path)
                
                # 直接保存为PNG图片
                # 注意：PNG支持RGBA模式，无需转换
                image.save(destination_path, 'PNG')
                print(f"已转换 {filename} 为 {base_name}.png 并保存到 {destination_folder}")
                
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")

if __name__ == "__main__":
    # 请替换为你实际的源文件夹路径
    source_folder = "E:/work/车门门环拼接/image/正面打光/9/2碰"
    # 请替换为你实际的目标文件夹路径
    destination_folder = "E:/work/车门门环拼接/image/正面打光/9/2碰/png"
    
    # 执行转换
    convert_bmp_to_png(source_folder, destination_folder)