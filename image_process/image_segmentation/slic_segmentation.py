import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import segmentation, color
from skimage.io import imread, imsave
from skimage.color import rgb2lab, lab2rgb
from sklearn.cluster import KMeans
import argparse
import os


def load_image(image_path):
    """加载图像并处理灰度图情况"""
    image = imread(image_path)
    if image.ndim == 2:  # 若为灰度图，转为RGB以便后续处理
        image = color.gray2rgb(image)
    return image


def preprocess_image(image, blur_kernel=(3, 3), blur_sigma=0):
    """图像预处理（去噪）"""
    # 高斯去噪（减少锈迹等噪声对聚类的干扰）
    denoised_image = cv2.GaussianBlur(image, blur_kernel, blur_sigma)
    return denoised_image


def apply_slic(image, n_segments=100, compactness=10, sigma=1):
    """应用SLIC超像素聚类"""
    segments = segmentation.slic(
        image,
        n_segments=n_segments,
        compactness=compactness,
        sigma=sigma,
        start_label=0
    )
    return segments


def generate_segmented_image(image, segments, show_boundaries=True, boundary_color=[0, 0, 0]):
    """生成带超像素边界的图像"""
    # 用原始图像颜色填充超像素
    segmented_image = color.label2rgb(segments, image, kind='avg', bg_label=-1)
    
    # 叠加超像素边界
    if show_boundaries:
        boundaries = segmentation.find_boundaries(segments, mode='thick')
        segmented_image[boundaries] = boundary_color
    
    return segmented_image


def visualize_results(original_image, segments, segmented_image, postprocessed_segments=None, postprocessed_image=None, save_path=None):
    """可视化结果"""
    # 确定子图数量
    if postprocessed_segments is not None and postprocessed_image is not None:
        fig, axes = plt.subplots(1, 5, figsize=(25, 5))
    else:
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    axes[0].imshow(original_image)
    axes[0].set_title("原始图像")
    axes[0].axis('off')
    
    axes[1].imshow(segments, cmap='tab20')  # 超像素标签图（不同颜色代表不同超像素）
    axes[1].set_title("SLIC超像素标签")
    axes[1].axis('off')
    
    axes[2].imshow(segmented_image)
    axes[2].set_title("带边界的超像素分割结果")
    axes[2].axis('off')
    
    # 如果有后处理结果，显示
    if postprocessed_segments is not None and postprocessed_image is not None:
        axes[3].imshow(postprocessed_segments, cmap='tab20')
        axes[3].set_title("颜色聚类后标签")
        axes[3].axis('off')
        
        axes[4].imshow(postprocessed_image)
        axes[4].set_title("颜色聚类后结果")
        axes[4].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"可视化结果已保存至: {save_path}")
    
    plt.show()


def save_segmented_image(segmented_image, output_path):
    """保存分割结果图像"""
    # 确保图像值在0-255范围内
    if segmented_image.max() <= 1:
        segmented_image = (segmented_image * 255).astype(np.uint8)
    
    # 转换为BGR格式以正确保存
    bgr_image = cv2.cvtColor(segmented_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, bgr_image)
    print(f"分割结果已保存至: {output_path}")


def extract_superpixel_features(image, segments):
    """提取超像素的颜色特征"""
    unique_segments = np.unique(segments)
    features = {}
    
    for segment_id in unique_segments:
        mask = segments == segment_id
        # 计算超像素的平均颜色
        mean_color = np.mean(image[mask], axis=0)
        # 计算超像素的面积
        area = np.sum(mask)
        # 计算超像素的边界框
        coords = np.where(mask)
        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()
        
        features[segment_id] = {
            'mean_color': mean_color,
            'area': area,
            'bbox': (y_min, y_max, x_min, x_max)
        }
    
    return features


def filter_superpixels_by_area(segments, features, min_area_ratio=0.01, max_area_ratio=0.5):
    """根据面积过滤超像素"""
    total_pixels = segments.size
    filtered_segments = np.copy(segments)
    filtered_ids = []
    
    for segment_id, feat in features.items():
        area_ratio = feat['area'] / total_pixels
        if area_ratio < min_area_ratio or area_ratio > max_area_ratio:
            filtered_segments[segments == segment_id] = -1
        else:
            filtered_ids.append(segment_id)
    
    return filtered_segments, filtered_ids


def merge_superpixels_by_color(image, segments, n_clusters=2, color_space='rgb'):
    """
    根据颜色特征合并相似的超像素
    
    参数:
    image: 原始图像
    segments: SLIC超像素分割结果
    n_clusters: 目标聚类数量，通常为2（背景和前景）
    color_space: 使用的颜色空间 ('rgb', 'lab')
    
    返回:
    merged_segments: 合并后的超像素标签
    """
    # 获取唯一的超像素ID
    unique_segments = np.unique(segments)
    
    # 跳过背景（-1）
    valid_segments = [seg_id for seg_id in unique_segments if seg_id != -1]
    
    if len(valid_segments) == 0:
        return segments
    
    # 提取每个超像素的颜色特征
    superpixel_colors = []
    for seg_id in valid_segments:
        mask = segments == seg_id
        mean_color = np.mean(image[mask], axis=0)
        superpixel_colors.append(mean_color)
    
    # 转换颜色空间（如果需要）
    superpixel_colors = np.array(superpixel_colors)
    if color_space == 'lab':
        # 将RGB转换为LAB颜色空间（更好地反映人眼视觉感知）
        # 需要先将0-1范围转换为0-255
        rgb_colors = (superpixel_colors * 255).astype(np.uint8)
        lab_colors = []
        for rgb in rgb_colors:
            lab = cv2.cvtColor(np.array([[rgb]]), cv2.COLOR_RGB2LAB)[0][0]
            lab_colors.append(lab)
        superpixel_colors = np.array(lab_colors)
        # 归一化LAB值
        superpixel_colors = superpixel_colors / np.array([100, 127, 127])
    
    # 应用K-means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(superpixel_colors)
    
    # 创建合并后的标签图
    merged_segments = np.copy(segments)
    
    # 为每个原始超像素分配新的聚类标签
    for i, seg_id in enumerate(valid_segments):
        merged_segments[segments == seg_id] = cluster_labels[i]
    
    return merged_segments


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='SLIC超像素聚类分割工具')
    parser.add_argument('--image', '-i', required=True, help='输入图像路径')
    parser.add_argument('--output', '-o', default='slic_segmented_result.png', help='输出图像路径')
    parser.add_argument('--n_segments', '-n', type=int, default=100, help='超像素数量（默认：100）')
    parser.add_argument('--compactness', '-c', type=int, default=10, help='紧凑度（默认：10）')
    parser.add_argument('--sigma', type=float, default=1.0, help='预平滑标准差（默认：1.0）')
    parser.add_argument('--blur_kernel', type=int, default=3, help='高斯模糊核大小（默认：3）')
    parser.add_argument('--show_visualization', action='store_true', help='显示可视化结果')
    parser.add_argument('--save_visualization', type=str, default=None, help='保存可视化结果的路径')
    parser.add_argument('--boundary_color', type=str, default='black', help='边界颜色（black/white/red/green/blue）')
    parser.add_argument('--filter_by_area', action='store_true', help='是否根据面积过滤超像素')
    parser.add_argument('--min_area_ratio', type=float, default=0.01, help='最小面积比例（默认：0.01）')
    parser.add_argument('--max_area_ratio', type=float, default=0.5, help='最大面积比例（默认：0.5）')
    
    # 新增参数：颜色聚类后处理
    parser.add_argument('--postprocess', action='store_true', help='是否进行颜色聚类后处理')
    parser.add_argument('--n_clusters', type=int, default=2, help='颜色聚类数量（默认：2，即背景和前景）')
    parser.add_argument('--color_space', type=str, default='lab', choices=['rgb', 'lab'], 
                        help='颜色空间选择（默认：lab，更好地反映人眼视觉感知）')
    parser.add_argument('--output_mask', type=str, default=None, help='输出二值掩码的路径（仅在postprocess=True时有效）')
    
    args = parser.parse_args()
    
    # 验证输入文件存在
    if not os.path.exists(args.image):
        print(f"错误：找不到输入文件 {args.image}")
        return
    
    # 设置边界颜色
    color_map = {
        'black': [0, 0, 0],
        'white': [1, 1, 1],
        'red': [1, 0, 0],
        'green': [0, 1, 0],
        'blue': [0, 0, 1]
    }
    boundary_color = color_map.get(args.boundary_color.lower(), [0, 0, 0])
    
    print(f"正在处理图像: {args.image}")
    print(f"超像素数量: {args.n_segments}")
    print(f"紧凑度: {args.compactness}")
    print(f"预平滑标准差: {args.sigma}")
    
    # 1. 读取图像
    try:
        image = load_image(args.image)
        print(f"成功加载图像，尺寸: {image.shape}")
    except Exception as e:
        print(f"加载图像失败: {e}")
        return
    
    # 2. 图像预处理
    denoised_image = preprocess_image(image, (args.blur_kernel, args.blur_kernel))
    
    # 3. 应用SLIC超像素聚类
    try:
        segments = apply_slic(denoised_image, args.n_segments, args.compactness, args.sigma)
        num_segments = len(np.unique(segments))
        print(f"SLIC聚类完成，生成了 {num_segments} 个超像素")
    except Exception as e:
        print(f"SLIC聚类失败: {e}")
        return
    
    # 4. 提取超像素特征
    features = extract_superpixel_features(image, segments)
    
    # 5. 根据面积过滤超像素（可选）
    if args.filter_by_area:
        filtered_segments, filtered_ids = filter_superpixels_by_area(
            segments, features, args.min_area_ratio, args.max_area_ratio
        )
        print(f"根据面积过滤后，剩余 {len(filtered_ids)} 个超像素")
        segments = filtered_segments
    
    # 6. 生成分割结果图像
    segmented_image = generate_segmented_image(image, segments, True, boundary_color)
    
    # 7. 颜色聚类后处理（可选）
    postprocessed_segments = None
    postprocessed_image = None
    
    if args.postprocess:
        print(f"进行颜色聚类后处理，目标聚类数量: {args.n_clusters}")
        print(f"使用颜色空间: {args.color_space}")
        
        try:
            # 合并相似颜色的超像素
            postprocessed_segments = merge_superpixels_by_color(
                image, segments, args.n_clusters, args.color_space
            )
            
            # 生成后处理的可视化图像
            postprocessed_image = generate_segmented_image(
                image, postprocessed_segments, True, boundary_color
            )
            
            # 保存后处理结果
            base_output = os.path.splitext(args.output)[0]
            postprocess_output = f"{base_output}_postprocessed.png"
            save_segmented_image(postprocessed_image, postprocess_output)
            
            # 生成并保存二值掩码（如果需要）
            if args.output_mask:
                # 确定哪个聚类是前景（通常是面积较小的那个）
                unique_clusters, counts = np.unique(postprocessed_segments, return_counts=True)
                # 过滤掉背景标签（-1）
                valid_clusters = [(cluster, count) for cluster, count in zip(unique_clusters, counts) if cluster != -1]
                
                if valid_clusters:
                    # 选择面积较小的聚类作为前景
                    foreground_cluster = min(valid_clusters, key=lambda x: x[1])[0]
                    # 创建二值掩码
                    binary_mask = (postprocessed_segments == foreground_cluster).astype(np.uint8) * 255
                    cv2.imwrite(args.output_mask, binary_mask)
                    print(f"二值掩码已保存至: {args.output_mask}")
        except Exception as e:
            print(f"颜色聚类后处理失败: {e}")
    
    # 8. 保存原始分割结果
    save_segmented_image(segmented_image, args.output)
    
    # 9. 可视化结果（可选）
    if args.show_visualization or args.save_visualization:
        visualize_results(
            image, segments, segmented_image, 
            postprocessed_segments, postprocessed_image,
            args.save_visualization
        )
    
    print("SLIC聚类分割完成！")


if __name__ == "__main__":
    main()