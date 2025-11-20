import cv2
import numpy as np
import argparse
import os
import sys

def convert_gray_to_color(input_path, output_path=None, method='pseudocolor'):
    """
    将灰度图转换为彩色图
    
    参数:
    input_path: 输入灰度图像路径
    output_path: 输出彩色图像路径（可选，默认为输入路径加_color后缀）
    method: 转换方法，可选 'pseudocolor'（伪彩色）或 'rgb'（三通道复制）
    """
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误：输入文件 '{input_path}' 不存在")
        return False
    
    # 读取图像
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        print(f"错误：无法读取图像文件 '{input_path}'")
        return False
    
    # 检查图像是否为灰度图
    if len(img.shape) != 2:
        print(f"警告：输入图像 '{input_path}' 可能不是灰度图，将尝试转换")
        # 如果是彩色图，先转换为灰度
        img_color = cv2.imread(input_path)
        if img_color is not None:
            img = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        else:
            print(f"错误：无法处理图像文件 '{input_path}'")
            return False
    
    # 生成输出路径
    if output_path is None:
        name, ext = os.path.splitext(input_path)
        output_path = f"{name}_color{ext}"
    
    # 根据选择的方法进行转换
    if method == 'pseudocolor':
        # 伪彩色转换：使用颜色映射
        color_img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
    elif method == 'rgb':
        # 三通道复制：将灰度值复制到RGB三个通道
        color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif method == 'hsv':
        # HSV颜色空间转换
        # 将灰度值映射到Hue通道，饱和度和亮度设为固定值
        hsv_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        hsv_img[:, :, 0] = (img / 255.0 * 180).astype(np.uint8)  # Hue: 0-180
        hsv_img[:, :, 1] = 255  # 饱和度设为最大
        hsv_img[:, :, 2] = 255  # 亮度设为最大
        color_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
    else:
        print(f"错误：不支持的转换方法 '{method}'")
        return False
    
    # 保存图像
    success = cv2.imwrite(output_path, color_img)
    
    if success:
        print(f"成功：灰度图已转换为彩色图并保存为 '{output_path}'")
        print(f"输入图像尺寸: {img.shape}")
        print(f"输出图像尺寸: {color_img.shape}")
        print(f"转换方法: {method}")
        return True
    else:
        print(f"错误：无法保存图像到 '{output_path}'")
        return False

def main():
    """主函数：处理命令行参数"""
    parser = argparse.ArgumentParser(description='将灰度图转换为彩色图')
    parser.add_argument('input', help='输入灰度图像路径')
    parser.add_argument('-o', '--output', help='输出彩色图像路径（可选）')
    parser.add_argument('-m', '--method', choices=['pseudocolor', 'rgb', 'hsv'], 
                       default='pseudocolor', help='转换方法：pseudocolor（伪彩色，默认）, rgb（三通道复制）, hsv（HSV颜色空间）')
    
    args = parser.parse_args()
    
    # 执行转换
    convert_gray_to_color(args.input, args.output, args.method)

if __name__ == "__main__":
    main()