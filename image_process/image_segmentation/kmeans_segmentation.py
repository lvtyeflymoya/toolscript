import cv2
import numpy as np
from sklearn.cluster import KMeans
import argparse
import os

def kmeans_segmentation(image_path, output_path, n_clusters=4, save_colored=True, visualize=False):
    """
    使用K-means均值聚类进行图像分割
    
    参数:
    - image_path: 输入图像路径
    - output_path: 输出图像路径
    - n_clusters: 聚类数量，默认为4
    - save_colored: 是否保存彩色分割结果，默认为True
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
    
    # 将图像转换为RGB格式（OpenCV默认读取为BGR）
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 获取图像尺寸
    height, width, channels = image.shape
    
    # 将图像数据重塑为二维数组（样本数 × 特征数）
    pixels = image_rgb.reshape(-1, 3)
    
    print(f"图像加载完成，尺寸: {width}×{height}")
    print(f"正在执行K-means聚类，聚类数量: {n_clusters}...")
    
    # 执行K-means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(pixels)
    
    # 获取聚类中心
    centers = kmeans.cluster_centers_.astype(int)
    
    # 创建分割后的图像
    segmented_image = centers[labels].reshape(height, width, 3)
    # 确保图像数据类型为uint8，OpenCV处理需要
    segmented_image = segmented_image.astype(np.uint8)
    
    # 保存结果
    if save_colored:
        # 保存彩色分割结果
        segmented_bgr = cv2.cvtColor(segmented_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, segmented_bgr)
        print(f"彩色分割结果已保存到: {output_path}")
    else:
        # 保存灰度分割结果（使用标签）
        label_image = labels.reshape(height, width)
        # 将标签值映射到0-255范围
        label_normalized = cv2.normalize(label_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        cv2.imwrite(output_path, label_normalized)
        print(f"灰度分割结果已保存到: {output_path}")
    
    # 创建并保存掩码图像 - 修改为保存每个聚类的单独掩码
    base_name = os.path.splitext(output_path)[0]
    print(f"正在保存{str(n_clusters)}个聚类的掩码图像...")
    
    # 为每个聚类创建并保存单独的掩码文件
    for i in range(n_clusters):
        # 创建单通道掩码
        mask = 255 * (labels == i).reshape(height, width).astype(np.uint8)
        # 生成掩码文件路径
        mask_file_path = f"{base_name}_mask_cluster_{i}.png"
        # 保存掩码
        cv2.imwrite(mask_file_path, mask)
        print(f"聚类{i}的掩码已保存到: {mask_file_path}")
    
    # 也可以保存一个综合掩码（将标签值映射到不同的灰度级别）
    composite_mask = labels.reshape(height, width)
    composite_mask = cv2.normalize(composite_mask, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    composite_mask_path = f"{base_name}_composite_mask.png"
    cv2.imwrite(composite_mask_path, composite_mask)
    print(f"综合掩码已保存到: {composite_mask_path}")
    
    # 显示结果（如果需要）
    if visualize:
        # 确保可视化时图像也是uint8格式
        if save_colored:
            show_image = cv2.cvtColor(segmented_image, cv2.COLOR_RGB2BGR)
        else:
            show_image = label_normalized
        cv2.imshow("原始图像", image)
        cv2.imshow("分割结果", show_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return True

def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description='使用K-means均值聚类进行图像分割')
    parser.add_argument('-i', '--input', required=True, help='输入图像路径')
    parser.add_argument('-o', '--output', required=True, help='输出图像路径')
    parser.add_argument('-k', '--clusters', type=int, default=4, help='聚类数量，默认为4')
    parser.add_argument('--no-color', action='store_true', help='保存为灰度分割结果，默认为彩色')
    parser.add_argument('--visualize', action='store_true', help='显示分割结果')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # 执行图像分割
    success = kmeans_segmentation(
        image_path=args.input,
        output_path=args.output,
        n_clusters=args.clusters,
        save_colored=not args.no_color,
        visualize=args.visualize
    )
    
    if success:
        print("图像分割完成!")
    else:
        print("图像分割失败!")