import numpy as np
import cv2
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt

def normalized_cut_segmentation_optimized(image, num_segments=5, sigma_color=0.1, sigma_coord=0.1, k_neighbors=10):
    """
    使用优化的归一化割算法进行图像分割
    通过构建稀疏邻接图避免全连接图的内存问题
    
    参数:
    - image: 输入图像 (numpy array)
    - num_segments: 分割的区域数量
    - sigma_color: 颜色特征的高斯权重参数
    - sigma_coord: 坐标特征的高斯权重参数
    - k_neighbors: 构建邻接图时考虑的最近邻数量
    """
    # 转换为float类型以进行计算
    img = image.astype(np.float32) / 255.0
    h, w, c = img.shape
    
    # 将图像重塑为像素向量
    pixels = img.reshape(-1, c)
    n_pixels = pixels.shape[0]
    
    # 创建坐标矩阵
    y_coords, x_coords = np.mgrid[0:h, 0:w]
    coords = np.stack([x_coords, y_coords], axis=-1).reshape(-1, 2)
    
    # 归一化坐标到[0,1]范围
    coords = coords / np.array([w-1, h-1]) if w > 1 and h > 1 else coords
    
    # 构建特征向量 (颜色 + 空间坐标)
    features = np.concatenate([pixels / sigma_color, coords / sigma_coord], axis=1)
    
    # 使用K近邻构建稀疏图
    nbrs = NearestNeighbors(n_neighbors=min(k_neighbors+1, n_pixels), metric='euclidean', n_jobs=-1)
    nbrs.fit(features)
    distances, indices = nbrs.kneighbors(features)
    
    # 计算边权重（相似度）
    rows, cols, weights = [], [], []
    
    for i in range(n_pixels):
        for j_idx, j in enumerate(indices[i]):
            if i != j:  # 避免自环
                # 计算高斯相似度
                dist = distances[i, j_idx]
                weight = np.exp(-dist**2 / 2.0)
                if weight > 1e-6:  # 忽略极小的权重
                    rows.append(i)
                    cols.append(j)
                    weights.append(weight)
    
    # 构建稀疏相似度矩阵
    W = csr_matrix((weights, (rows, cols)), shape=(n_pixels, n_pixels))
    
    # 计算度矩阵
    D = np.array(W.sum(axis=1)).flatten()
    D_sqrt_inv = diags(1.0 / np.sqrt(D), format='csr')
    
    # 计算归一化拉普拉斯矩阵 L_sym = I - D^(-1/2) * W * D^(-1/2)
    L_sym = D_sqrt_inv @ W @ D_sqrt_inv
    L_sym = csr_matrix(L_sym)
    
    # 计算特征值和特征向量 (只计算最小的几个)
    # 由于我们计算的是 L_sym = D^(-1/2) * W * D^(-1/2)，我们需要找最大的特征值
    # 但scipy的eigsh默认找最大的，所以我们需要找最大的几个特征值
    k = min(num_segments, n_pixels-1)
    eigenvals, eigenvecs = eigsh(L_sym, k=k, which='LM')  # LM = Largest Magnitude
    
    # 由于我们找的是W相关的特征向量，实际需要找最小的L=D-W特征值
    # 重新计算L_rw = I - D^(-1) * W
    D_inv = diags(1.0 / D, format='csr')
    L_rw = D_inv @ W
    L_rw = csr_matrix(L_rw)
    
    # 计算L_rw的特征向量（对应最小特征值的）
    eigenvals, eigenvecs = eigsh(L_rw, k=k, which='LR', sigma=0)  # LR = Largest Real part
    
    # 使用K-means聚类
    kmeans = KMeans(n_clusters=num_segments, random_state=42, n_init=10)
    labels = kmeans.fit_predict(eigenvecs)
    
    # 重塑标签到原始图像尺寸
    segmented_img = labels.reshape(h, w)
    
    return segmented_img

def visualize_segmentation(original_img, segmented_img):
    """
    可视化原始图像和分割结果
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    ax1.imshow(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB))
    ax1.set_title('原始图像')
    ax1.axis('off')
    
    ax2.imshow(segmented_img, cmap='tab20')
    ax2.set_title('归一化割分割结果')
    ax2.axis('off')
    
    plt.tight_layout()
    plt.show()

def main():
    # 创建一个示例图像
    # example_img = np.zeros((200, 200, 3), dtype=np.uint8)
    # example_img[50:150, 50:150] = [255, 0, 0]  # 红色方块
    # example_img[25:75, 25:75] = [0, 255, 0]   # 绿色方块
    # example_img[125:175, 125:175] = [0, 0, 255] # 蓝色方块
    image = cv2.imread("E:/work/车门门环拼接/image/正面打光/9/2碰/1984_7063.bmp")
    print("开始图像分割...")
    print(f"图像尺寸: {image.shape}")
    
    # 执行归一化割分割
    segmented = normalized_cut_segmentation_optimized(
        image, 
        num_segments=4, 
        sigma_color=0.1, 
        sigma_coord=0.1, 
        k_neighbors=10
    )
    
    # 可视化结果
    visualize_segmentation(image, segmented)
    
    print("图像分割完成！")
    print(f"分割区域数量: {len(np.unique(segmented))}")
    print(f"分割区域标签: {sorted(list(np.unique(segmented)))}")

if __name__ == "__main__":
    main()



