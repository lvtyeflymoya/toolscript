import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import RANSACRegressor

# 读取图像
image = cv2.imread("E:/work/车门门环拼接/image/正面打光/normal/厚/5/2/6686_20464.bmp", cv2.IMREAD_GRAYSCALE)

# 1. 图像二值化
_, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# 2. 中轴变换（Skeletonization）
size = np.size(binary)
skel = np.zeros(binary.shape, np.uint8)

element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
done = False

while not done:
    eroded = cv2.erode(binary, element)
    temp = cv2.dilate(eroded, element)
    temp = cv2.subtract(binary, temp)
    skel = cv2.bitwise_or(skel, temp)
    binary = eroded.copy()

    zeros = size - cv2.countNonZero(binary)
    if zeros == size:
        done = True

# 3. 提取中心线坐标点
y_coords, x_coords = np.where(skel > 0)

# 4. 使用RANSAC方法拟合直线
if len(x_coords) > 0:
    # 准备数据：将x坐标作为特征，y坐标作为目标
    X = x_coords.reshape(-1, 1)
    y = y_coords
    
    # 使用RANSAC回归器
    ransac = RANSACRegressor(random_state=42)
    ransac.fit(X, y)
    
    # 获取拟合的直线参数
    inlier_mask = ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)
    
    # 获取直线参数：y = kx + b
    k = ransac.estimator_.coef_[0]  # 斜率
    b = ransac.estimator_.intercept_  # 截距
    
    # 生成拟合直线上的点
    x_min, x_max = min(x_coords), max(x_coords)
    x_fit = np.linspace(x_min, x_max, 100)
    y_fit = k * x_fit + b
    
    # 5. 创建彩色图像用于显示
    color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # 在原图上绘制所有中心线点
    # 内点（绿色）
    for x, y in zip(x_coords[inlier_mask], y_coords[inlier_mask]):
        cv2.circle(color_image, (x, y), 1, (0, 255, 0), -1)
    
    # 外点（红色）
    for x, y in zip(x_coords[outlier_mask], y_coords[outlier_mask]):
        cv2.circle(color_image, (x, y), 1, (0, 0, 255), -1)
    
    # 在原图上绘制拟合直线（蓝色）
    for i in range(len(x_fit) - 1):
        x1, y1 = int(x_fit[i]), int(y_fit[i])
        x2, y2 = int(x_fit[i+1]), int(y_fit[i+1])
        cv2.line(color_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    
    # 6. 显示结果
    plt.figure(figsize=(15, 5))
    
    # 原始图像
    plt.subplot(1, 3, 1)
    plt.imshow(image, cmap='gray')
    plt.title('原始图像')
    plt.axis('off')
    
    # 骨架图像
    plt.subplot(1, 3, 2)
    plt.imshow(skel, cmap='gray')
    plt.title('提取的中心线')
    plt.axis('off')
    
    # 拟合结果
    plt.subplot(1, 3, 3)
    plt.imshow(cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB))
    plt.title('RANSAC直线拟合结果')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # 7. 打印拟合方程和统计信息
    print(f"中心线直线方程: y = {k:.6f}x + {b:.6f}")
    print(f"总点数: {len(x_coords)}")
    print(f"内点数: {np.sum(inlier_mask)}")
    print(f"外点数: {np.sum(outlier_mask)}")
    print(f"内点比例: {np.sum(inlier_mask) / len(x_coords):.2%}")
    
    # 8. 使用OpenCV显示结果
    cv2.imshow('Original Image', image)
    cv2.imshow('Skeleton', skel)
    cv2.imshow('RANSAC Fitted Line', color_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
else:
    print("未检测到中心线")