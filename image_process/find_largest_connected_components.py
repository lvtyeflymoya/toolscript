import cv2
import numpy as np
import argparse
import os


def find_largest_two_components(image_path, output_path=None):
    """
    找出图像中最大的两个白色连通域，分别求出它们的最小外接多边形，
    将这两个多边形的内部全部填充白色像素，并保存结果
    
    参数:
        image_path: 输入图像路径
        output_path: 输出图像保存路径，默认为None（在原图像目录下生成）
    """
    # 读取图像
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"无法读取图像: {image_path}")
        return False
    
    # 二值化图像（假设白色区域为目标）
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    # 寻找连通域
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
    
    # 按面积排序连通域（跳过背景区域）
    # stats的格式: [x, y, width, height, area]
    areas = stats[1:, 4]  # 第一个是背景，跳过
    if len(areas) < 2:
        print(f"图像中连通域数量不足2个: {len(areas)}")
        return False
    
    # 找出最大的两个连通域的索引
    sorted_indices = np.argsort(areas)[::-1]  # 降序排列
    largest_indices = sorted_indices[:2] + 1  # +1是因为我们跳过了背景
    
    # 创建一个空白图像用于绘制结果
    result = np.zeros_like(binary)
    
    for idx in largest_indices:
        # 创建该连通域的掩码
        component_mask = (labels == idx).astype(np.uint8) * 255
        
        # 寻找该连通域的轮廓
        contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 获取最大的轮廓（应该只有一个）
            contour = max(contours, key=cv2.contourArea)
            
            # 使用Douglas-Peucker算法近似轮廓为多边形
            # 0.01是近似精度，值越小轮廓越接近原始形状
            epsilon = 0.01 * cv2.arcLength(contour, True)
            approx_polygon = cv2.approxPolyDP(contour, epsilon, True)
            
            # 在结果图像上填充多边形
            cv2.fillPoly(result, [approx_polygon], 255)
    
    # 如果未指定输出路径，在原图像目录下生成
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(os.path.dirname(image_path), f"{base_name}_filled_polygons.png")
    
    # 保存结果
    success = cv2.imwrite(output_path, result)
    if success:
        print(f"处理完成，结果已保存至: {output_path}")
    else:
        print(f"保存图像失败: {output_path}")
    
    return success


def process_folder(input_folder, output_folder=None):
    """
    批量处理文件夹中的所有图像
    
    参数:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径，默认为None（在输入文件夹下创建输出目录）
    """
    # 支持的图像格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # 确保输出文件夹存在
    if output_folder is None:
        output_folder = os.path.join(input_folder, 'filled_polygons_output')
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")
    
    # 遍历文件夹中的所有文件
    processed_count = 0
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        
        # 检查是否为支持的图像文件
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in supported_formats:
            print(f"\n处理图像: {filename}")
            
            # 生成输出路径
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_filled_polygons{os.path.splitext(filename)[1]}")
            
            # 处理图像
            result = find_largest_two_components(file_path, output_path)
            if result:
                processed_count += 1
    
    print(f"\n处理完成！共处理 {processed_count} 张图像")
    return processed_count


if __name__ == "__main__":
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='找出图像中最大的两个白色连通域，计算最小外接多边形并填充')
    parser.add_argument('-i', '--input', required=True, help='输入图像路径或文件夹路径')
    parser.add_argument('-o', '--output', help='输出图像路径或文件夹路径')
    parser.add_argument('-b', '--batch', action='store_true', help='批量处理模式')
    
    args = parser.parse_args()
    
    # 根据是否批量处理模式选择不同的处理函数
    if args.batch:
        if not os.path.isdir(args.input):
            print(f"错误：批量处理模式需要输入文件夹路径，而不是文件路径")
        else:
            process_folder(args.input, args.output)
    else:
        if not os.path.isfile(args.input):
            print(f"错误：单文件处理模式需要输入文件路径，而不是文件夹路径")
        else:
            find_largest_two_components(args.input, args.output)