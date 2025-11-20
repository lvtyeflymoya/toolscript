import cv2
import numpy as np
import argparse
import os

def mean_shift_segmentation(image_path, output_path, spatial_radius=10, color_radius=30, max_level=1, visualize=False):
    """
    使用MeanShift算法进行图像分割
    
    参数:
    - image_path: 输入图像路径
    - output_path: 输出图像路径
    - spatial_radius: 空间窗口半径，默认为10
    - color_radius: 颜色窗口半径，默认为30
    - max_level: 金字塔最大层数，用于加速计算，默认为1
    - visualize: 是否显示分割结果，默认为False
    """
    # 检查输入文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 找不到输入文件 {image_path}")
        return False
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"错误: 无法读取图像 {image_path}")
        return False
    
    # 获取图像尺寸
    height, width = image.shape[:2]
    print(f"图像加载完成，尺寸: {width}×{height}")
    
    # 应用MeanShift分割
    print(f"正在应用MeanShift分割... 参数: spatial_radius={spatial_radius}, color_radius={color_radius}, max_level={max_level}")
    # 修复：使用正确的参数名 sp, sr, maxLevel
    segmented_image = cv2.pyrMeanShiftFiltering(
        image, 
        sp=spatial_radius,  # 空间窗口半径
        sr=color_radius,    # 颜色窗口半径
        maxLevel=max_level  # 金字塔最大层数
    )
    
    # 保存分割结果
    cv2.imwrite(output_path, segmented_image)
    print(f"分割结果已保存到: {output_path}")
    
    # 可选：基于分割结果生成掩码
    # 转换为灰度图以便进一步处理
    gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY)
    
    # 应用自适应阈值获取不同区域
    thresh = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11, 2
    )
    
    # 保存阈值结果作为掩码参考
    mask_path = os.path.splitext(output_path)[0] + "_mask.png"
    cv2.imwrite(mask_path, thresh)
    print(f"掩码图像已保存到: {mask_path}")
    
    # 显示结果（如果需要）
    if visualize:
        cv2.namedWindow("原始图像", cv2.WINDOW_NORMAL)
        cv2.namedWindow("分割结果", cv2.WINDOW_NORMAL)
        cv2.namedWindow("分割掩码", cv2.WINDOW_NORMAL)
        
        cv2.imshow("原始图像", image)
        cv2.imshow("分割结果", segmented_image)
        cv2.imshow("分割掩码", thresh)
        
        print("按任意键关闭窗口...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return True


def batch_process(input_folder, output_folder, spatial_radius=10, color_radius=30, max_level=1):
    """
    批量处理文件夹中的所有图像
    
    参数:
    - input_folder: 输入文件夹路径
    - output_folder: 输出文件夹路径
    - spatial_radius: 空间窗口半径
    - color_radius: 颜色窗口半径
    - max_level: 金字塔最大层数
    """
    # 支持的图像格式
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
    
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")
    
    # 获取输入文件夹中的所有图像文件
    image_files = [f for f in os.listdir(input_folder) 
                  if os.path.isfile(os.path.join(input_folder, f)) 
                  and f.lower().endswith(supported_formats)]
    
    if not image_files:
        print(f"警告: 在目录 '{input_folder}' 中未找到支持的图像文件")
        return
    
    print(f"找到 {len(image_files)} 个图像文件，开始批量处理...")
    
    # 批量处理每个图像
    for i, image_file in enumerate(image_files):
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, f"segmented_{image_file}")
        
        print(f"处理图像 {i+1}/{len(image_files)}: '{image_file}'")
        mean_shift_segmentation(
            input_path, 
            output_path, 
            spatial_radius=spatial_radius, 
            color_radius=color_radius, 
            max_level=max_level, 
            visualize=False
        )
    
    print(f"批量处理完成！所有结果已保存至 '{output_folder}'")


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description='使用MeanShift算法进行图像分割')
    parser.add_argument('-i', '--input', required=True, help='输入图像路径或文件夹路径')
    parser.add_argument('-o', '--output', required=True, help='输出图像路径或文件夹路径')
    parser.add_argument('-s', '--spatial-radius', type=int, default=10, help='空间窗口半径，默认为10')
    parser.add_argument('-c', '--color-radius', type=int, default=30, help='颜色窗口半径，默认为30')
    parser.add_argument('-l', '--max-level', type=int, default=1, help='金字塔最大层数，默认为1')
    parser.add_argument('-v', '--visualize', action='store_true', help='显示分割结果')
    parser.add_argument('-b', '--batch', action='store_true', help='批量处理模式')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # 根据是否批量处理模式选择不同的处理函数
    if args.batch:
        # 批量处理模式
        if not os.path.isdir(args.input):
            print(f"错误：批量处理模式需要输入文件夹路径，而不是文件路径")
        else:
            batch_process(
                args.input, 
                args.output,
                spatial_radius=args.spatial_radius,
                color_radius=args.color_radius,
                max_level=args.max_level
            )
    else:
        # 单文件处理模式
        if not os.path.isfile(args.input):
            print(f"错误：单文件处理模式需要输入文件路径，而不是文件夹路径")
        else:
            success = mean_shift_segmentation(
                image_path=args.input,
                output_path=args.output,
                spatial_radius=args.spatial_radius,
                color_radius=args.color_radius,
                max_level=args.max_level,
                visualize=args.visualize
            )
            
            if success:
                print("图像分割完成!")
            else:
                print("图像分割失败!")