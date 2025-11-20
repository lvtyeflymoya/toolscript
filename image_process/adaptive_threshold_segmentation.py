import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def adaptive_threshold_segmentation(image_path, block_size=11, C=2, save_results=False, output_dir=None):
    """
    使用局部自适应阈值进行图像分割
    
    参数:
        image_path: 图像路径
        block_size: 局部块大小（必须为奇数），默认11
        C: 阈值偏移量，默认2
        save_results: 是否保存分割结果，默认False
        output_dir: 保存结果的目录，默认None（与输入图像同目录）
    
    返回:
        分割后的图像（自适应高斯阈值和自适应均值阈值两种结果）
    """
    # 确保block_size为奇数
    if block_size % 2 == 0:
        block_size += 1
        print(f"警告: block_size必须为奇数，已自动调整为{block_size}")
    
    # 读取图像
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法找到或读取图像: {image_path}")
    
    # 转换为灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 局部自适应阈值分割
    # 方法1：自适应高斯阈值
    adaptive_gaussian = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # 高斯加权局部均值
        cv2.THRESH_BINARY_INV,           # 二值化类型（反相，使目标为白色）
        blockSize=block_size,
        C=C
    )
    
    # 方法2：自适应均值阈值
    adaptive_mean = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,     # 简单局部均值
        cv2.THRESH_BINARY_INV,
        blockSize=block_size,
        C=C
    )

    # 方法3：固定阈值
    _, fixed_threshold = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
    
    # 结果展示
    plt.figure(figsize=(15, 5))
    plt.subplot(141)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title("原始图像")
    plt.axis("off")
    
    plt.subplot(142)
    plt.imshow(adaptive_gaussian, cmap="gray")
    plt.title(f"自适应高斯阈值分割\nblock_size={block_size}, C={C}")
    plt.axis("off")
    
    plt.subplot(143)
    plt.imshow(adaptive_mean, cmap="gray")
    plt.title(f"自适应均值阈值分割\nblock_size={block_size}, C={C}")
    plt.axis("off")

    # 固定阈值
    plt.subplot(144)
    plt.imshow(fixed_threshold, cmap="gray")
    plt.title(f"固定阈值分割\nthreshold=10")
    
    plt.tight_layout()
    plt.show()
    
    # 保存结果（如果需要）
    if save_results:
        # 确定输出目录
        if output_dir is None:
            output_dir = Path(image_path).parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取文件名（不含扩展名）
        base_name = Path(image_path).stem
        
        # 保存结果
        gaussian_path = output_dir / f"{base_name}_gaussian_block{block_size}_C{C}.png"
        mean_path = output_dir / f"{base_name}_mean_block{block_size}_C{C}.png"
        
        cv2.imwrite(str(gaussian_path), adaptive_gaussian)
        cv2.imwrite(str(mean_path), adaptive_mean)
        
        print(f"结果已保存到:\n- {gaussian_path}\n- {mean_path}")
    
    print("分割完成！")
    return adaptive_gaussian, adaptive_mean

def batch_process(folder_path, block_size=11, C=2, save_results=True):
    """
    批量处理文件夹中的所有图像
    
    参数:
        folder_path: 包含图像的文件夹路径
        block_size: 局部块大小
        C: 阈值偏移量
        save_results: 是否保存结果
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    # 支持的图像格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    # 创建输出目录
    output_dir = folder / "threshold_results"
    
    # 遍历文件夹中的所有图像
    image_files = [f for f in folder.iterdir() if f.suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"在文件夹 {folder_path} 中未找到支持的图像文件")
        return
    
    print(f"找到 {len(image_files)} 个图像文件，开始处理...")
    
    for i, image_file in enumerate(image_files, 1):
        print(f"\n处理图像 {i}/{len(image_files)}: {image_file.name}")
        try:
            adaptive_threshold_segmentation(
                str(image_file), 
                block_size=block_size, 
                C=C, 
                save_results=save_results, 
                output_dir=str(output_dir)
            )
        except Exception as e:
            print(f"处理失败: {e}")
    
    print("\n批量处理完成！")


if __name__ == "__main__":
    # 示例用法
    # 1. 单个图像处理
    image_path = "E:/work/车门门环拼接/image/正面打光/9/2碰/4470_3827.bmp"
    adaptive_threshold_segmentation(image_path, block_size=2111, C=20, save_results=True)
    
    # 2. 批量处理
    # folder_path = "path/to/your/images/folder"
    # batch_process(folder_path, block_size=11, C=2)
    