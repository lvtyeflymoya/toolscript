import cv2
import numpy as np
# 在文件开头的导入部分添加以下代码
import matplotlib.pyplot as plt
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
import os
from pathlib import Path

def watershed_segmentation(image_path, output_path, visualize=False):
    """
    使用分水岭算法进行图像分割
    
    参数:
    - image_path: 输入图像路径
    - output_path: 输出图像路径
    - visualize: 是否显示分割过程和结果，默认为False
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
    
    # 1. 图像预处理
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 应用高斯模糊减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 2. 基于Otsu的阈值分割
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # @TODO：可以改善确定前景背景的方法，另外还可以试一下其他基于区域的分割方法，这个方法效果完整一点
    
    # 3. 形态学操作 - 去除噪声和填充小洞
    # 开运算（先腐蚀后膨胀）去除噪声
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # 膨胀操作获取可能的背景区域
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    
    # 4. 计算距离变换
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    
    # 5. 基于距离变换的阈值分割获取前景区域
    _, sure_fg = cv2.threshold(dist_transform, 0.5 * dist_transform.max(), 255, 0)
    
    # 转换为uint8类型
    sure_fg = np.uint8(sure_fg)
    
    # 6. 计算未知区域（背景-前景）
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # 7. 标记连通区域
    _, markers = cv2.connectedComponents(sure_fg)
    
    # 为所有标记加1，使得背景不是0而是1
    markers = markers + 1
    
    # 将未知区域标记为0
    markers[unknown == 255] = 0
    
    # 8. 应用分水岭算法
    markers = cv2.watershed(image, markers)
    
    # 9. 生成分割结果
    # 创建结果图像 - 原始图像上叠加分割边界
    result = image.copy()
    # 在图像上标记分水岭边界（标记为-1的区域）
    result[markers == -1] = [0, 255, 0]  # 边界用绿色标记
    
    # 创建分割掩码图像
    mask = np.zeros_like(gray)
    # 为每个分割区域分配不同的值
    for i in range(2, markers.max() + 1):
        mask[markers == i] = i * (255 // (markers.max() + 1))
    
    # 保存分割结果
    cv2.imwrite(output_path, result)
    print(f"分割结果已保存到: {output_path}")
    
    # 保存分割掩码
    mask_path = os.path.splitext(output_path)[0] + "_mask.png"
    cv2.imwrite(mask_path, mask)
    print(f"分割掩码已保存到: {mask_path}")
    
    # 显示结果（如果需要）
    if visualize:
        plt.figure(figsize=(15, 10))
        
        plt.subplot(231)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title('原始图像')
        plt.axis('off')
        
        plt.subplot(232)
        plt.imshow(thresh, cmap='gray')
        plt.title('Otsu阈值分割')
        plt.axis('off')
        
        plt.subplot(233)
        plt.imshow(sure_bg, cmap='gray')
        plt.title('确定背景')
        plt.axis('off')
        
        plt.subplot(234)
        plt.imshow(sure_fg, cmap='gray')
        plt.title('确定前景')
        plt.axis('off')
        
        plt.subplot(235)
        plt.imshow(dist_transform, cmap='jet')
        plt.title('距离变换')
        plt.axis('off')
        
        plt.subplot(236)
        plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        plt.title('分水岭分割结果')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        # 显示标记图像
        plt.figure(figsize=(10, 5))
        plt.subplot(121)
        plt.imshow(markers, cmap='tab20')
        plt.title('标记图像')
        plt.axis('off')
        
        plt.subplot(122)
        plt.imshow(mask, cmap='gray')
        plt.title('分割掩码')
        plt.axis('off')

        # 显示未知
        plt.figure(figsize=(10, 5))
        plt.subplot(111)
        plt.imshow(unknown, cmap='gray')
        plt.title('未知区域')
        plt.axis('off')
        
        
        plt.tight_layout()
        plt.show()
    
    return True

def batch_process(input_folder, output_folder, visualize=False):
    """
    批量处理文件夹中的所有图像
    
    参数:
    - input_folder: 输入文件夹路径
    - output_folder: 输出文件夹路径
    - visualize: 是否显示分割结果，默认为False
    """
    # 确保输入文件夹存在
    if not os.path.isdir(input_folder):
        print(f"错误: 找不到输入文件夹 {input_folder}")
        return False
    
    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 支持的图像格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    # 获取所有图像文件
    image_files = [f for f in os.listdir(input_folder) 
                  if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    if not image_files:
        print(f"在文件夹 {input_folder} 中未找到支持的图像文件")
        return False
    
    print(f"找到 {len(image_files)} 个图像文件，开始处理...")
    
    # 逐个处理图像
    for i, image_file in enumerate(image_files, 1):
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, f"watershed_{image_file}")
        
        print(f"\n处理图像 {i}/{len(image_files)}: {image_file}")
        try:
            watershed_segmentation(input_path, output_path, visualize)
        except Exception as e:
            print(f"处理失败: {e}")
    
    print("\n批量处理完成！")
    return True

def parse_arguments():
    """
    解析命令行参数
    """
    import argparse
    parser = argparse.ArgumentParser(description='使用分水岭算法进行图像分割')
    parser.add_argument('-i', '--input', required=True, help='输入图像路径或文件夹路径')
    parser.add_argument('-o', '--output', required=True, help='输出图像路径或文件夹路径')
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
            batch_process(args.input, args.output, args.visualize)
    else:
        # 单文件处理模式
        if not os.path.isfile(args.input):
            print(f"错误：单文件处理模式需要输入文件路径，而不是文件夹路径")
        else:
            success = watershed_segmentation(args.input, args.output, args.visualize)
            
            if success:
                print("图像分割完成!")
            else:
                print("图像分割失败!")