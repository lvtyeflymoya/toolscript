## 将黑白的边缘图重叠话在原图上
import cv2
import numpy as np

def draw_edges_on_original(original_path, edge_path, output_path):
    """
    在原图上用红色绘制边缘图中的边缘
    
    参数:
        original_path: 原图路径
        edge_path: 黑白边缘图路径
        output_path: 结果图保存路径
    """
    # 读取原图和边缘图
    original = cv2.imread(original_path)
    edge_image = cv2.imread(edge_path, cv2.IMREAD_GRAYSCALE)  # 以灰度模式读取
    
    if original is None:
        raise FileNotFoundError(f"无法读取原图: {original_path}")
    if edge_image is None:
        raise FileNotFoundError(f"无法读取边缘图: {edge_path}")
    
    # 确保两张图尺寸相同
    if original.shape[:2] != edge_image.shape[:2]:
        # 调整边缘图尺寸以匹配原图
        edge_image = cv2.resize(edge_image, (original.shape[1], original.shape[0]))
        print(f"已调整边缘图尺寸以匹配原图: {original.shape[1]}x{original.shape[0]}")
    
    # 找到边缘像素（边缘图中像素值不为0的位置）
    edges = edge_image > 0  # 创建布尔掩码
    
    # 在原图上用红色标记边缘
    # 复制原图以避免修改原图
    result = original.copy()
    # 将边缘位置的像素设置为红色 (BGR格式，红色为(0,0,255))
    result[edges] = [0, 0, 255]
    
    # 保存结果图
    cv2.imwrite(output_path, result)
    print(f"结果已保存至: {output_path}")
    
    # 显示结果（可选）
    cv2.imshow('Original Image', original)
    cv2.imshow('Edge Image', edge_image)
    cv2.imshow('Result with Red Edges', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 示例用法
    original_image_path = "D:/ImageAnnotation/threadMeasurement/远心/中间过程/cropped.bmp"   # 替换为你的原图路径
    edge_image_path = "D:/Python_Project/ED_pidinet/test/eval_results/imgs_epoch_019/cropped.bmp"         # 替换为你的边缘图路径
    output_image_path = "D:/Python_Project/ED_pidinet/test/eval_results/imgs_epoch_019/color_edge.bmp"      # 结果图保存路径
    
    try:
        draw_edges_on_original(original_image_path, edge_image_path, output_image_path)
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
