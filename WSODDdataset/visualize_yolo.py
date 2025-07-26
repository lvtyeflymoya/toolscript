# 根据yolo标注文件可视化

import cv2
import os
import glob

def visualize_yolo_labels(images_dir, labels_dir, output_dir, class_names):
    """
    可视化YOLO格式的标注
    :param images_dir: 图片目录路径
    :param labels_dir: 标签目录路径
    :param output_dir: 输出目录路径
    :param class_names: 类别名称列表
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义颜色方案（BGR格式）
    colors = [(i * 50 % 255, i * 100 % 255, i * 150 % 255) for i in range(len(class_names))]
    
    # 遍历所有标签文件
    for label_path in glob.glob(os.path.join(labels_dir, "*.txt")):
        # 获取对应的图片路径
        base_name = os.path.splitext(os.path.basename(label_path))[0]
        img_path = find_image_file(images_dir, base_name)
        
        if not img_path or not os.path.exists(img_path):
            continue
            
        # 读取图片
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        img_h, img_w = img.shape[:2]
        
        # 读取标签文件
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        # 绘制每个检测框
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
                
            try:
                class_id = int(parts[0])
                x_center = float(parts[1]) * img_w
                y_center = float(parts[2]) * img_h
                width = float(parts[3]) * img_w
                height = float(parts[4]) * img_h
                
                # 计算矩形坐标
                xmin = int(x_center - width/2)
                ymin = int(y_center - height/2)
                xmax = int(x_center + width/2)
                ymax = int(y_center + height/2)
                
                # 绘制矩形和文字
                color = colors[class_id % len(colors)]
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
                cv2.putText(img, f"{class_names[class_id]}", (xmin, ymin-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            except (ValueError, IndexError):
                continue
        
        # 保存结果
        output_path = os.path.join(output_dir, os.path.basename(img_path))
        cv2.imwrite(output_path, img)

def find_image_file(img_dir, base_name):
    """查找匹配的图片文件"""
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        img_path = os.path.join(img_dir, base_name + ext)
        if os.path.exists(img_path):
            return img_path
    return None

if __name__ == "__main__":
    # 配置参数（根据实际情况修改）
    images_dir = "E:/dataset/漂浮物-0722/buoy.v1i.yolov/train/images"
    labels_dir = "E:/dataset/漂浮物-0722/labels/modify/1111"
    output_dir = "E:/dataset/漂浮物-0722/buoy.v1i.yolov/train/visual"
    
    # 类别列表需要与convert_to_yolo中的target_classes保持一致
    # class_names = ['ship', 'rubbish', 'buoy', 'platform', 'wharf', 'pier']
    class_names = ['0', '1', '2', '3', '4-buoyyyyyyyy', '5-buoyyyyyyyyy', '6', '7', '8', '9', '10', '11','12']
    
    visualize_yolo_labels(images_dir, labels_dir, output_dir, class_names)
    print(f"可视化结果已保存到: {output_dir}")
