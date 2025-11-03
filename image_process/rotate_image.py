from PIL import Image
import cv2
import numpy as np

def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    # 获取旋转矩阵
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 计算新边界
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # 调整旋转矩阵的平移部分，使图像居中
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # 执行旋转
    rotated = cv2.warpAffine(image, M, (new_w, new_h))
    return rotated

def simple_rotate_image():
    """
    简单的图片旋转示例
    """
    # 设置参数
    input_path = "E:/work/车门门环拼接/image/test/cropped_img.bmp"  # 输入图片路径
    output_path = "E:/work/车门门环拼接/image/test/cropped_img_rotate_30.bmp"  # 输出图片路径
    angle = 30  # 旋转角度（顺时针）
    
    try:
        # 打开图片
        img = Image.open(input_path)
        
        # 旋转图片（expand=True 确保旋转后图像完整显示）
        rotated_img = rotate_image(np.array(img), angle)
        
        # 保存图片
        cv2.imwrite(output_path, rotated_img)
        print(f"图片已成功旋转 {angle} 度并保存到: {output_path}")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_path}")
    except Exception as e:
        print(f"处理图片时发生错误: {e}")

if __name__ == "__main__":
    simple_rotate_image()