import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

from regex import T
from sympy import true

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号


# ======================== 算法处理部分 ========================

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return gray, blurred

def threshold_segmentation(blurred):
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def morphological_operations(thresh):
    kernel = np.ones((3, 3), np.uint8)
    # 闭运算（先膨胀后腐蚀）填充前景物体内部孔洞
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    # 膨胀操作获取可能的背景区域
    sure_bg = cv2.dilate(closed, kernel, iterations=3)
    return closed, sure_bg

def fill_by_largest_black_area(closed):
    """
    选取面积最大的黑色连通域作为确定背景，其他区域填充白色

    参数:
    - closed: 闭运算后的二值图像

    返回:
    - filled_image: 填充后的图像
    - largest_black_area: 最大黑色连通域的面积
    """
    # 反转图像，使黑色连通域变成白色连通域
    inverted = cv2.bitwise_not(closed)

    # 查找所有连通域
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(inverted, 8, cv2.CV_32S)

    if num_labels <= 1:  # 没有黑色区域
        return closed.copy(), 0

    # 找到面积最大的连通域（跳过背景标签0）
    max_area = 0
    max_label = 0
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area > max_area:
            max_area = area
            max_label = i

    # 创建结果图像：将所有区域填充为白色，除了最大黑色连通域
    filled_image = np.ones_like(closed) * 255  # 初始化为全白
    filled_image[labels == max_label] = 0  # 最大黑色区域保持为黑色

    return filled_image, max_area

def extract_foreground_simple(closed):
    """
    简单的前景提取：先填充，然后腐蚀获得前景标记

    参数:
    - closed: 闭运算后的二值图像

    返回:
    - sure_fg: 确定的前景区域（腐蚀后的白色区域）
    - filled_image: 填充后的图像
    - largest_black_area: 最大黑色连通域面积
    """
    # 1. 填充非最大黑色区域为白色
    filled_image, largest_black_area = fill_by_largest_black_area(closed)

    # 2. 腐蚀运算获得确定前景
    kernel = np.ones((5, 5), np.uint8)
    sure_fg = cv2.erode(filled_image, kernel, iterations=2)

    return sure_fg, filled_image, largest_black_area

def visualize_simple_process(closed, filled_image, sure_fg, largest_black_area):
    """
    可视化简化的处理过程

    参数:
    - closed: 闭运算后的二值图像
    - filled_image: 填充后的图像
    - sure_fg: 确定的前景区域
    - largest_black_area: 最大黑色连通域面积
    """
    plt.figure(figsize=(15, 5))

    plt.subplot(131)
    plt.imshow(closed, cmap='gray')
    plt.title('闭运算后的图像')
    plt.axis('off')

    plt.subplot(132)
    plt.imshow(filled_image, cmap='gray')
    plt.title(f'填充后（最大黑色区域面积：{largest_black_area}）')
    plt.axis('off')

    plt.subplot(133)
    plt.imshow(sure_fg, cmap='gray')
    plt.title('腐蚀后的前景标记')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

def extract_foreground(closed):
    # 使用外接矩形填充方法移除孔洞
    filled, largest_contours = fill_holes_by_bounding_rect(closed)

    # 计算距离变换
    dist_transform = cv2.distanceTransform(filled, cv2.DIST_L2, 5)
    # 基于距离变换的阈值分割获取前景区域
    _, sure_fg = cv2.threshold(dist_transform, 0.2 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    return sure_fg, dist_transform, filled, largest_contours

def compute_markers(sure_bg, sure_fg):
    # 计算未知区域（背景-前景）
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # 标记连通区域
    _, markers = cv2.connectedComponents(sure_fg)
    
    # 为所有标记加1，使得背景不是0而是1
    markers = markers + 1
    
    # 将未知区域标记为0
    markers[unknown == 255] = 0
    
    return markers, unknown

def apply_watershed(image, markers):
    markers = cv2.watershed(image, markers)
    return markers

def generate_segmentation_results(image, gray, markers):
    # 创建结果图像 - 原始图像上叠加分割边界
    result = image.copy()
    # 在图像上标记分水岭边界（标记为-1的区域）
    result[markers == -1] = [0, 255, 0]  # 边界用绿色标记
    
    # 创建分割掩码图像
    mask = np.zeros_like(gray)
    # 为每个分割区域分配不同的值
    for i in range(2, markers.max() + 1):
        mask[markers == i] = i * (255 // (markers.max() + 1))
    
    return result, mask

def watershed_algorithm(image):
    # 1. 图像预处理
    gray, blurred = preprocess_image(image)

    # 2. 阈值分割
    thresh = threshold_segmentation(blurred)

    # 3. 形态学操作
    closed, sure_bg = morphological_operations(thresh)

    # 4. 简化的前景提取
    sure_fg, filled_image, largest_black_area = extract_foreground_simple(closed)

    # 5. 计算标记
    markers, unknown = compute_markers(sure_bg, sure_fg)

    # 6. 应用分水岭算法
    markers = apply_watershed(image, markers)

    # 7. 生成分割结果
    result, mask = generate_segmentation_results(image, gray, markers)

    # 保存中间结果用于可视化
    intermediate_results = {
        'gray': gray,
        'thresh': thresh,
        'sure_bg': sure_bg,
        'sure_fg': sure_fg,
        'unknown': unknown,
        'markers': markers,
        'filled_image': filled_image,
        'largest_black_area': largest_black_area,
        'closed': closed
    }

    return result, mask, intermediate_results


# ======================== 结果显示部分 ========================

def save_results(result, mask, output_path):
    """
    保存分割结果和掩码
    
    参数:
    - result: 带边界标记的结果图像
    - mask: 分割掩码
    - output_path: 输出路径
    
    返回:
    - success: 是否保存成功
    """
    try:
        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存分割结果
        cv2.imwrite(output_path, result)
        print(f"分割结果已保存到: {output_path}")
        
        # 保存分割掩码
        mask_path = os.path.splitext(output_path)[0] + "_mask.png"
        cv2.imwrite(mask_path, mask)
        print(f"分割掩码已保存到: {mask_path}")
        
        return True
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return False


def visualize_process(image, mask, intermediate_results):
    """
    可视化简化的分割过程和结果

    参数:
    - image: 原始BGR图像
    - mask: 分割掩码
    - intermediate_results: 中间处理结果字典
    """
    # 可视化主要处理步骤
    plt.figure(figsize=(20, 12))

    plt.subplot(241)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title('原始图像')
    plt.axis('off')

    plt.subplot(242)
    plt.imshow(intermediate_results['thresh'], cmap='gray')
    plt.title('二值化后的图像')
    plt.axis('off')

    plt.subplot(243)
    plt.imshow(intermediate_results['closed'], cmap='gray')
    plt.title('闭运算后的图像')
    plt.axis('off')

    plt.subplot(244)
    plt.imshow(intermediate_results['filled_image'], cmap='gray')
    plt.title(f'填充后（最大黑色区域面积：{intermediate_results["largest_black_area"]}）')
    plt.axis('off')

    plt.subplot(245)
    plt.imshow(intermediate_results['sure_bg'], cmap='gray')
    plt.title('确定的背景图像')
    plt.axis('off')

    plt.subplot(246)
    plt.imshow(intermediate_results['sure_fg'], cmap='gray')
    plt.title('腐蚀后的前景标记')
    plt.axis('off')

    plt.subplot(247)
    plt.imshow(intermediate_results['unknown'], cmap='gray')
    plt.title('未知区域图像')
    plt.axis('off')

    plt.subplot(248)
    plt.imshow(mask, cmap='gray')
    plt.title('分割后的掩码图像')
    plt.axis('off')

    plt.tight_layout()
    plt.show()


def visualize_markers_and_mask(intermediate_results, mask):
    """
    可视化标记图像和分割掩码
    
    参数:
    - intermediate_results: 中间处理结果字典
    - mask: 分割掩码
    """
    plt.figure(figsize=(10, 5))
    
    plt.subplot(121)
    plt.imshow(intermediate_results['markers'], cmap='tab20')
    plt.title('标记图像')
    plt.axis('off')
    
    plt.subplot(122)
    plt.imshow(mask, cmap='gray')
    plt.title('分割掩码')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()


def visualize_unknown_region(intermediate_results):
    """
    可视化未知区域
    
    参数:
    - intermediate_results: 中间处理结果字典
    """
    plt.figure(figsize=(10, 5))
    
    plt.subplot(111)
    plt.imshow(intermediate_results['unknown'], cmap='gray')
    plt.title('未知区域')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()


# ======================== 主函数 ========================

def watershed_segmentation(image_path, output_path, visualize=True):
    """
    使用分水岭算法进行图像分割
    
    参数:
    - image_path: 输入图像路径
    - output_path: 输出图像路径
    - visualize: 是否显示分割过程和结果，默认为True
    
    返回:
    - success: 是否处理成功
    """
    # 检查输入文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 找不到输入文件 {image_path}")
        return False
    
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"错误: 无法读取图像 {image_path}")
        return False
    
    # 获取图像尺寸
    height, width = image.shape[:2]
    print(f"图像加载完成，尺寸: {width}×{height}")
    
    # 执行分水岭算法
    result, mask, intermediate_results = watershed_algorithm(image)
    
    # 保存结果
    save_success = save_results(result, mask, output_path)
    
    # 显示结果（如果需要）
    if visualize:
        # 显示简化的处理过程
        visualize_simple_process(intermediate_results['closed'],
                               intermediate_results['filled_image'],
                               intermediate_results['sure_fg'],
                               intermediate_results['largest_black_area'])
        # 显示完整的处理流程
        visualize_process(image, mask, intermediate_results)
    
    return save_success


def batch_process(input_folder, output_folder, visualize=False):
    """
    批量处理文件夹中的所有图像
    
    参数:
    - input_folder: 输入文件夹路径
    - output_folder: 输出文件夹路径
    - visualize: 是否显示分割结果，默认为False
    
    返回:
    - success: 是否处理成功
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
    success_count = 0
    for i, image_file in enumerate(image_files, 1):
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, f"watershed_{image_file}")
        
        print(f"\n处理图像 {i}/{len(image_files)}: {image_file}")
        try:
            if watershed_segmentation(input_path, output_path, visualize):
                success_count += 1
        except Exception as e:
            print(f"处理失败: {e}")
    
    print(f"\n批量处理完成！成功处理 {success_count}/{len(image_files)} 个图像")
    return True


def parse_arguments():
    """
    解析命令行参数
    
    返回:
    - args: 解析后的参数
    """
    import argparse
    parser = argparse.ArgumentParser(description='使用分水岭算法进行图像分割')
    parser.add_argument('-i', '--input', 
                        default='E:/work/车门门环拼接/image/正面打光/9/1/1958_7061.bmp', 
                        help='输入图像路径或文件夹路径')
    parser.add_argument('-o', '--output', 
                        default='./output/watershed_result.bmp', 
                        help='输出图像路径或文件夹路径')
    parser.add_argument('-v', '--visualize', 
                        default=False,
                        action='store_true', 
                        help='显示分割结果')
    parser.add_argument('-b', '--batch', 
                        action='store_true', 
                        help='批量处理模式')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # 根据是否批量处理模式选择不同的处理函数
    if args.batch:
        # 批量处理模式
        if not os.path.isdir(args.input):
            print(f"错误：批量处理模式需要输入文件夹路径，而不是文件路径")
        else:
            batch_process(args.input, args.output, visualize=args.visualize)
    else:
        # 单文件处理模式
        if not os.path.isfile(args.input):
            print(f"错误：单文件处理模式需要输入文件路径，而不是文件夹路径")
        else:
            success = watershed_segmentation(args.input, args.output, visualize=args.visualize)
            
            if success:
                print("\n图像分割完成!")
            else:
                print("\n图像分割失败!")
