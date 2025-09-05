# 将coco格式的标注文件转换为yolo格式的标注文件
import json
import os
import shutil

def convert_coco_to_yolo(coco_json_path, target_classes, output_dir):
    """
    将COCO格式标注转换为YOLO格式
    :param coco_json_path: COCO格式的JSON文件路径
    :param target_classes: 需要保留的目标类别列表
    :param output_dir: YOLO标注输出目录
    """
    os.makedirs(output_dir, exist_ok=True)
    
    with open(coco_json_path, 'r') as f:
        coco_data = json.load(f)
    
    # 创建类别映射
    category_map = {cat['id']: idx for idx, cat in enumerate(coco_data['categories']) if cat['name'] in target_classes}
    
    # 创建图片ID到文件名的映射
    image_id_map = {img['id']: img for img in coco_data['images']}
    
    # 遍历所有标注
    for ann in coco_data['annotations']:
        # 跳过不保留的类别
        if ann['category_id'] not in category_map:
            continue
        
        # 获取对应的图片信息
        img_info = image_id_map.get(ann['image_id'])
        if not img_info:
            continue
        
        # 移除图片存在性检查
        img_w, img_h = img_info['width'], img_info['height']
        if img_w == 0 or img_h == 0:
            continue
        
        # 转换坐标到YOLO格式
        x, y, w, h = ann['bbox']
        x_center = (x + w / 2) / img_w
        y_center = (y + h / 2) / img_h
        width = w / img_w
        height = h / img_h
        
        # 验证坐标有效性
        if not (0 <= x_center <= 1 and 0 <= y_center <= 1):
            continue
        
        # 准备输出路径
        base_name = os.path.splitext(img_info['file_name'])[0]
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
        
        with open(txt_path, 'a') as f:
            line = f"{category_map[ann['category_id']]} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
            f.write(line)

if __name__ == "__main__":
    # 修改后的调用示例
    coco_json = "E:/Dataset/标注/zhang/label/COCO/annotations.json"
    target_classes = ['ship','rubbish','buoy', 'platform', 'wharf', 'pier']
    output_dir = "E:/Dataset/标注/zhang/label/YOLO"
    convert_coco_to_yolo(
        coco_json,
        target_classes,
        output_dir
    )