import os
import shutil
from collections import defaultdict
import glob

def classify_yolo_images(label_dir, image_dir, output_root):
    """
    分类YOLO数据集图片到对应类别目录
    :param label_dir: YOLO标签目录路径
    :param image_dir: 原始图片目录路径
    :param output_root: 分类结果根目录
    """
    # 创建分类根目录
    os.makedirs(output_root, exist_ok=True)
    
    # 获取所有标签文件路径
    label_files = glob.glob(os.path.join(label_dir, "*.txt"))
    
    # 存储类别到图片的映射
    class_image_map = defaultdict(set)
    
    # 第一次遍历：收集所有存在的类别
    for label_file in label_files:
        base_name = os.path.splitext(os.path.basename(label_file))[0]
        with open(label_file, 'r') as f:
            for line in f:
                class_id = line.strip().split()[0]
                class_image_map[class_id].add(base_name)
    
    # 第二次遍历：复制图片到所有相关类别目录
    for class_id, basenames in class_image_map.items():
        class_dir = os.path.join(output_root, f"class_{class_id}")
        os.makedirs(class_dir, exist_ok=True)
        
        for base in basenames:
            # 查找源图片文件
            img_path = None
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                temp_path = os.path.join(image_dir, base + ext)
                if os.path.exists(temp_path):
                    img_path = temp_path
                    break
            
            if img_path:
                # 复制到所有相关类别目录
                dest_path = os.path.join(class_dir, os.path.basename(img_path))
                if not os.path.exists(dest_path):
                    shutil.copy(img_path, dest_path)
            else:
                print(f"警告：未找到图片 {base} 的源文件")

if __name__ == "__main__":
    label_directory = "E:/dataset/WSODD USV_dataset/yolo_labels"  # 修改为实际标签目录
    image_directory = "E:/dataset/WSODD USV_dataset/yolo_visualized"    # 修改为实际图片目录
    output_directory = "E:/dataset/WSODD USV_dataset/yolo_classfied"  # 分类输出目录
    
    classify_yolo_images(label_directory, image_directory, output_directory)
    print("图片分类完成！")
