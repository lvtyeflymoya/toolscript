#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片叠加工具

功能：将两张图片按照指定的透明度叠加到一起显示

使用说明：
1. 直接运行：提供两个图片路径作为命令行参数，可选透明度参数
2. 作为模块导入：调用overlay_images函数

依赖：
- Pillow (PIL)
- argparse
- numpy
"""

import os
import argparse
from PIL import Image
import numpy as np

def overlay_images(image_path1, image_path2, output_path=None, alpha=0.5, resize_to_match=True):
    """
    将两张图片叠加到一起
    
    参数：
        image_path1 (str): 第一张图片的路径（将作为底层图片）
        image_path2 (str): 第二张图片的路径（将作为叠加图片）
        output_path (str, optional): 输出图片的路径，默认为None（不保存，仅显示）
        alpha (float, optional): 叠加图片的透明度，范围0.0-1.0，默认为0.5
        resize_to_match (bool, optional): 是否将第二张图片调整为与第一张图片相同大小，默认为True
    
    返回：
        PIL.Image: 叠加后的图片对象
    """
    # 检查文件是否存在
    if not os.path.exists(image_path1):
        raise FileNotFoundError(f"第一张图片不存在: {image_path1}")
    if not os.path.exists(image_path2):
        raise FileNotFoundError(f"第二张图片不存在: {image_path2}")
    
    # 检查透明度参数
    if not 0 <= alpha <= 1:
        raise ValueError("透明度参数必须在0.0到1.0之间")
    
    # 打开图片
    base_image = Image.open(image_path1).convert('RGBA')
    overlay_image = Image.open(image_path2).convert('RGBA')
    
    # 如果需要调整大小
    if resize_to_match:
        overlay_image = overlay_image.resize(base_image.size, Image.LANCZOS)
    else:
        # 如果不调整大小，确保图片尺寸相同
        if base_image.size != overlay_image.size:
            print("警告：两张图片尺寸不同，将只在重叠区域叠加")
    
    # 创建一个新的透明图片作为结果
    result_image = Image.new('RGBA', base_image.size)
    
    # 进行叠加
    # 方法1：使用PIL的blend函数（需要尺寸相同）
    if base_image.size == overlay_image.size:
        result_image = Image.blend(base_image, overlay_image, alpha)
    else:
        # 方法2：对于尺寸不同的图片，手动处理
        result_image.paste(base_image, (0, 0))
        # 计算叠加的位置（居中）
        paste_x = (base_image.width - overlay_image.width) // 2
        paste_y = (base_image.height - overlay_image.height) // 2
        # 使用alpha参数调整叠加图片的透明度
        overlay_array = np.array(overlay_image)
        overlay_array[..., 3] = (overlay_array[..., 3] * alpha).astype(np.uint8)
        overlay_image = Image.fromarray(overlay_array)
        # 粘贴叠加图片
        result_image.paste(overlay_image, (paste_x, paste_y), overlay_image)
    
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
        print(f"叠加后的图片已保存至: {output_path}")
    
    return result_image

def main():
    """
    命令行入口函数
    """
    parser = argparse.ArgumentParser(description='将两张图片叠加到一起')
    parser.add_argument('image1', help='第一张图片路径（底层图片）')
    parser.add_argument('image2', help='第二张图片路径（叠加图片）')
    parser.add_argument('-o', '--output', help='输出图片路径')
    parser.add_argument('-a', '--alpha', type=float, default=0.5, 
                        help='叠加图片的透明度（0.0-1.0），默认为0.5')
    parser.add_argument('-n', '--no-resize', action='store_true',
                        help='不调整图片大小以匹配底层图片')
    
    args = parser.parse_args()
    
    try:
        # 调用叠加函数
        result_image = overlay_images(
            args.image1,
            args.image2,
            args.output,
            args.alpha,
            not args.no_resize
        )
        
        # 显示图片
        result_image.show()
        
    except Exception as e:
        print(f"错误: {e}")
        exit(1)

if __name__ == "__main__":
    main()