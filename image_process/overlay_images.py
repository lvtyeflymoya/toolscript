#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片叠加工具 - 边缘检测版本

功能：对第二张图片进行Canny边缘检测，然后将得到的边缘用指定颜色绘制在第一张图片上

使用说明：
1. 直接运行：提供两个图片路径作为命令行参数，可选边缘颜色、Canny阈值等参数
2. 作为模块导入：调用overlay_images函数

依赖：
- Pillow (PIL)
- OpenCV (cv2)
- argparse
- numpy
"""

import os
import argparse
import cv2
import numpy as np
from PIL import Image

def overlay_images(image_path1, image_path2, output_path=None, edge_color=(0, 0, 255), 
                   canny_threshold1=100, canny_threshold2=200, resize_to_match=True):
    """
    将第二张图片的边缘检测结果绘制在第一张图片上
    
    参数：
        image_path1 (str): 第一张图片的路径（将作为底层图片）
        image_path2 (str): 第二张图片的路径（将进行边缘检测）
        output_path (str, optional): 输出图片的路径，默认为None（不保存，仅显示）
        edge_color (tuple, optional): 边缘线的颜色，格式为BGR，默认为红色(0, 0, 255)
        canny_threshold1 (int, optional): Canny边缘检测的第一个阈值，默认为100
        canny_threshold2 (int, optional): Canny边缘检测的第二个阈值，默认为200
        resize_to_match (bool, optional): 是否将第二张图片调整为与第一张图片相同大小，默认为True
    
    返回：
        PIL.Image: 处理后的图片对象
    """
    # 检查文件是否存在
    if not os.path.exists(image_path1):
        raise FileNotFoundError(f"第一张图片不存在: {image_path1}")
    if not os.path.exists(image_path2):
        raise FileNotFoundError(f"第二张图片不存在: {image_path2}")
    
    # 使用OpenCV读取图片
    base_img_cv = cv2.imread(image_path1)
    overlay_img_cv = cv2.imread(image_path2)
    
    # 确保base_img_cv和overlay_img_cv不为None
    if base_img_cv is None:
        raise ValueError(f"无法读取第一张图片: {image_path1}")
    if overlay_img_cv is None:
        raise ValueError(f"无法读取第二张图片: {image_path2}")
    
    # 初始化处理区域参数
    process_height, process_width = base_img_cv.shape[:2]
    
    # 如果需要调整大小
    if resize_to_match:
        overlay_img_cv = cv2.resize(overlay_img_cv, (base_img_cv.shape[1], base_img_cv.shape[0]))
        result_img_cv = base_img_cv.copy()
    else:
        # 如果不调整大小，确保图片尺寸相同
        if base_img_cv.shape[:2] != overlay_img_cv.shape[:2]:
            print("警告：两张图片尺寸不同，将只在重叠区域进行处理")
            # 计算处理区域（左上角对齐的重叠区域）
            process_height = min(base_img_cv.shape[0], overlay_img_cv.shape[0])
            process_width = min(base_img_cv.shape[1], overlay_img_cv.shape[1])
        result_img_cv = base_img_cv.copy()
    
    # 对第二张图片进行Canny边缘检测
    # 转换为灰度图
    gray = cv2.cvtColor(overlay_img_cv[:process_height, :process_width], cv2.COLOR_BGR2GRAY)
    # 进行高斯模糊，减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Canny边缘检测
    edges = cv2.Canny(blurred, canny_threshold1, canny_threshold2)
    
    # 在基础图片上绘制边缘
    if resize_to_match or base_img_cv.shape[:2] == overlay_img_cv.shape[:2]:
        # 尺寸相同时，直接在原图上绘制
        result_img_cv[edges > 0] = edge_color
    else:
        # 在重叠区域绘制边缘
        result_img_cv[:process_height, :process_width][edges > 0] = edge_color
    
    # 转换OpenCV图像格式为PIL格式
    # OpenCV使用BGR，PIL使用RGB，需要转换
    result_img_rgb = cv2.cvtColor(result_img_cv, cv2.COLOR_BGR2RGB)
    result_image = Image.fromarray(result_img_rgb)
    
    # 如果需要保存图片
    if output_path:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存图片（转换为RGB模式以兼容常见格式）
        if output_path.lower().endswith(('.jpg', '.jpeg')):
            result_image.convert('RGB').save(output_path)
        else:
            result_image.save(output_path)
        print(f"处理后的图片已保存至: {output_path}")
    
    return result_image

def main():
    """
    命令行入口函数
    example:
        python overlay_images.py -image1 image1.png -image2 image2.png -o output.png -ec 255 0 0 -t1 50 -t2 150
    """
    parser = argparse.ArgumentParser(description='将第二张图片的边缘检测结果绘制在第一张图片上')
    parser.add_argument('-image1', default="E:/work/车门门环拼接/image/overlap/7140_5847正.bmp", help='第一张图片路径（底层图片）')
    parser.add_argument('-image2', default="E:/work/车门门环拼接/image/overlap/7140_5847.bmp", help='第二张图片路径（将进行边缘检测）')
    parser.add_argument('-o', '--output', default="E:/work/车门门环拼接/image/overlap/overlay.bmp", help='输出图片路径')
    parser.add_argument('-ec', '--edge-color', type=int, nargs=3, default=[0, 0, 255],
                        help='边缘线的颜色（B G R），默认为红色 (0 0 255)')
    parser.add_argument('-t1', '--threshold1', type=int, default=100,
                        help='Canny边缘检测的第一个阈值，默认为100')
    parser.add_argument('-t2', '--threshold2', type=int, default=200,
                        help='Canny边缘检测的第二个阈值，默认为200')
    parser.add_argument('-n', '--no-resize', action='store_true',
                        help='不调整图片大小以匹配底层图片')
    
    args = parser.parse_args()
    
    try:
        # 调用边缘叠加函数
        result_image = overlay_images(
            args.image1,
            args.image2,
            args.output,
            tuple(args.edge_color),  # 转换为元组
            args.threshold1,
            args.threshold2,
            not args.no_resize
        )
        
        # 显示图片
        result_image.show()
        
    except Exception as e:
        print(f"错误: {e}")
        exit(1)

if __name__ == "__main__":
    main()