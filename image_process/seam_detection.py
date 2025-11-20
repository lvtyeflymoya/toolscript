import cv2
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

def homomorphic_filter(image, gamma_l=0.5, gamma_h=2.0, cutoff_freq_ratio=0.1):
    """
    同态滤波增强图像对比度
    """
    # 转换为浮点数并取对数
    img_float = np.float32(image)
    img_log = np.log(img_float + 1)
    
    # 傅里叶变换
    img_fft = np.fft.fft2(img_log)
    img_fft_shift = np.fft.fftshift(img_fft)
    
    # 创建同态滤波器
    rows, cols = img_fft_shift.shape
    crow, ccol = rows // 2, cols // 2
    cutoff = cutoff_freq_ratio * min(rows, cols)
    
    # 高斯高通滤波器
    X, Y = np.ogrid[:rows, :cols]
    distance = np.sqrt((X - crow)**2 + (Y - ccol)**2)
    H = (gamma_h - gamma_l) * (1 - np.exp(-(distance**2) / (2 * (cutoff**2)))) + gamma_l
    
    # 应用滤波器
    filtered_fft = img_fft_shift * H
    
    # 逆傅里叶变换
    filtered_fft_ishift = np.fft.ifftshift(filtered_fft)
    img_filtered = np.fft.ifft2(filtered_fft_ishift)
    img_filtered = np.real(img_filtered)
    
    # 指数变换
    result = np.exp(img_filtered) - 1
    result = np.uint8(np.clip(result, 0, 255))
    
    return result

def log_otsu_segmentation(image, sigma=1.0):
    """
    基于LoG算子的Otsu分割方法
    """
    # 步骤1: LoG算子滤波
    # 首先应用高斯模糊
    gaussian = cv2.GaussianBlur(image, (3, 3), sigma)
    
    # 应用拉普拉斯算子
    laplacian = cv2.Laplacian(gaussian, cv2.CV_64F)
    
    # 步骤2: 高阈值边缘增强
    _, high_thresh = cv2.threshold(np.uint8(np.abs(laplacian)), 0, 255, 
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    enhanced_edges = cv2.bitwise_and(np.uint8(np.abs(laplacian)), 
                                    np.uint8(np.abs(laplacian)), 
                                    mask=high_thresh)
    
    # 步骤3: 边缘信息融合
    enhanced_image = cv2.addWeighted(image, 0.7, enhanced_edges, 0.3, 0)
    
    # 步骤4: Otsu分割
    _, otsu_thresh = cv2.threshold(enhanced_image, 0, 255, 
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return otsu_thresh, enhanced_edges

def morphological_processing(binary_image, kernel_size=3):
    """
    形态学后处理：开运算和闭运算
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # 开运算去除噪声和小孔
    opening = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
    
    # 闭运算填充内部空洞
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    
    return closing

def multi_morphology_gradient_edge_detection(image, kernel_size=3):
    """
    多形态学组合梯度边缘检测
    实现公式：Grad[f] = (f ○ b) ⊕ b - (f ● b) ⊖ b
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # 开运算：f ○ b
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    
    # 开运算后膨胀：(f ○ b) ⊕ b
    opening_dilated = cv2.dilate(opening, kernel)
    
    # 闭运算：f ● b
    closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    
    # 闭运算后腐蚀：(f ● b) ⊖ b
    closing_eroded = cv2.erode(closing, kernel)
    
    # 梯度计算：Grad[f] = (f ○ b) ⊕ b - (f ● b) ⊖ b
    gradient_edges = cv2.subtract(opening_dilated, closing_eroded)
    
    return gradient_edges

def clahe_enhancement(image, clip_limit=2.0, grid_size=(8,8)):
    """
    CLAHE对比度受限自适应直方图均衡化
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    enhanced = clahe.apply(image)
    return enhanced

def main_processing_pipeline(image_path):
    """
    主处理流程：实现文档中完整的图像处理流程
    """
    # 1. 读取图像
    original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if original_image is None:
        print("无法读取图像，请检查路径")
        return
    
    # 2. 图像预处理
    # 双边滤波
    bilateral_filtered = cv2.bilateralFilter(original_image, 9, 75, 75)
    
    # 同态滤波增强
    homomorphic_enhanced = homomorphic_filter(bilateral_filtered)
    
    # CLAHE增强
    clahe_enhanced = clahe_enhancement(homomorphic_enhanced)
    
    # 3. LoG-Otsu分割
    segmented_image, enhanced_edges = log_otsu_segmentation(clahe_enhanced, sigma=1.5)
    
    # 4. 形态学处理
    morphological_processed = morphological_processing(segmented_image, kernel_size=5)
    
    # 5. 多形态学梯度边缘检测
    # 对原始增强图像进行边缘检测
    gradient_edges = multi_morphology_gradient_edge_detection(clahe_enhanced, kernel_size=3)
    
    # 对分割后的区域进行边缘检测（限制在目标区域内）
    segmented_edges = cv2.bitwise_and(gradient_edges, gradient_edges, 
                                     mask=morphological_processed)
    
    # 6. 结果显示
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 3, 1)
    plt.imshow(original_image, cmap='gray')
    plt.title('原始图像')
    plt.axis('off')
    
    plt.subplot(2, 3, 2)
    plt.imshow(clahe_enhanced, cmap='gray')
    plt.title('预处理后图像')
    plt.axis('off')
    
    plt.subplot(2, 3, 3)
    plt.imshow(enhanced_edges, cmap='gray')
    plt.title('LoG增强边缘')
    plt.axis('off')
    
    plt.subplot(2, 3, 4)
    plt.imshow(segmented_image, cmap='gray')
    plt.title('Otsu分割结果')
    plt.axis('off')
    
    plt.subplot(2, 3, 5)
    plt.imshow(morphological_processed, cmap='gray')
    plt.title('形态学处理后')
    plt.axis('off')
    
    plt.subplot(2, 3, 6)
    plt.imshow(segmented_edges, cmap='gray')
    plt.title('最终梯度边缘')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'original': original_image,
        'preprocessed': clahe_enhanced,
        'enhanced_edges': enhanced_edges,
        'segmented': segmented_image,
        'morphological': morphological_processed,
        'final_edges': segmented_edges
    }

# 使用示例
if __name__ == "__main__":
    # 替换为您的图像路径
    image_path = "E:/work/车门门环拼接/image/背面打光/4540_3765.bmp"
    results = main_processing_pipeline(image_path)