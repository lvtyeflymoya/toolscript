# 解析voc格式的标注文件，并将其转为yolo格式的标注文件，同时将对应的图片文件复制到指定的文件夹中。

import xml.etree.ElementTree as ET
import os
import glob
import shutil  # 新增导入

def get_all_classes(annotations_dir):
    # 使用集合自动去重
    classes = set()
    
    # 遍历所有XML文件
    for xml_file in glob.glob(os.path.join(annotations_dir, "*.xml")):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # 解析每个object的类别名称
        for obj in root.iter('object'):
            name_elem = obj.find('name')
            if name_elem is not None and name_elem.text:
                cls_name = name_elem.text.strip()
                if cls_name:  # 防止空字符串
                    classes.add(cls_name)
    
    return sorted(list(classes))

# 转换VOC到YOLO格式
def convert_to_yolo(annotations_dir, images_dir, target_classes, output_dir, output_img_dir):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建类别索引映射
    class_idx = {cls: idx for idx, cls in enumerate(target_classes)}
    
    # 创建图片输出目录
    os.makedirs(output_img_dir, exist_ok=True)
    
    
    # 遍历所有XML文件
    for xml_file in glob.glob(os.path.join(annotations_dir, "*.xml")):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # 获取对应的图片文件
        base_name = os.path.splitext(os.path.basename(xml_file))[0]
        img_path = find_image_file(images_dir, base_name)
        
        if not img_path:
            continue
            
        # 获取图片尺寸
        img_w, img_h = get_image_size(img_path)
        if img_w == 0 or img_h == 0:
            continue
            
        yolo_lines = []
        
        # 解析每个object
        for obj in root.iter('object'):
            name_elem = obj.find('name')
            if name_elem is not None and name_elem.text:
                cls_name = name_elem.text.strip()
                if cls_name in class_idx:
                    # 解析边界框
                    bbox = obj.find('bndbox')
                    if bbox is not None:
                        # 添加坐标值存在性检查
                        xmin_elem = bbox.find('xmin')
                        ymin_elem = bbox.find('ymin')
                        xmax_elem = bbox.find('xmax')
                        ymax_elem = bbox.find('ymax')
                        
                        if all(elem is not None and elem.text for elem in [xmin_elem, ymin_elem, xmax_elem, ymax_elem]):
                            try:
                                # 转换为浮点数前去除空白字符
                                xmin = float(xmin_elem.text.strip())
                                ymin = float(ymin_elem.text.strip())
                                xmax = float(xmax_elem.text.strip())
                                ymax = float(ymax_elem.text.strip())
                                
                                # 验证坐标值有效性
                                if xmin >= xmax or ymin >= ymax:
                                    continue
                                    
                                # 转换到YOLO格式
                                x_center = (xmin + xmax) / 2 / img_w
                                y_center = (ymin + ymax) / 2 / img_h
                                width = (xmax - xmin) / img_w
                                height = (ymax - ymin) / img_h
                                
                                # 验证归一化后的值是否在[0,1]范围内
                                if not (0 <= x_center <= 1 and 0 <= y_center <= 1):
                                    continue
                                
                                yolo_lines.append(f"{class_idx[cls_name]} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
                            except (ValueError, TypeError):
                                continue
        
        # 写入YOLO标注文件
        if yolo_lines:
            output_path = os.path.join(output_dir, f"{base_name}.txt")
            with open(output_path, 'w') as f:
                f.write('\n'.join(yolo_lines))
            
            # 复制图片到目标目录
            if img_path:
                try:
                    # 保持原始文件名
                    img_filename = os.path.basename(img_path)
                    dest_path = os.path.join(output_img_dir, img_filename)
                    shutil.copyfile(img_path, dest_path)
                except Exception as e:
                    print(f"复制图片失败: {img_path} -> {dest_path} ({str(e)})")

# 辅助函数：查找图片文件
def find_image_file(img_dir, base_name):
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        img_path = os.path.join(img_dir, base_name + ext)
        if os.path.exists(img_path):
            return img_path
    return None

# 辅助函数：获取图片尺寸
def get_image_size(img_path):
    try:
        import cv2
        img = cv2.imread(img_path)
        if img is not None:
            return img.shape[1], img.shape[0]  # (width, height)
    except:
        pass
    return 0, 0

def rename_voc_classes(src_annotations_dir, dst_annotations_dir):
    """重命名VOC标注文件中的类别并保存到新目录"""
    class_mapping = {
        'boat': 'ship',
        'grass': 'rubbish',
        'harbor': 'wharf'
    }
    
    # 创建目标目录
    os.makedirs(dst_annotations_dir, exist_ok=True)
    
    # 遍历所有XML文件
    for xml_file in glob.glob(os.path.join(src_annotations_dir, "*.xml")):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # 修改类别名称
        for obj in root.iter('object'):
            name_elem = obj.find('name')
            if name_elem is not None and name_elem.text:
                original_cls = name_elem.text.strip()
                # 如果存在映射关系则替换
                if original_cls in class_mapping:
                    name_elem.text = class_mapping[original_cls]
        
        # 保存到新路径
        dst_path = os.path.join(dst_annotations_dir, os.path.basename(xml_file))
        tree.write(dst_path, encoding='utf-8')

if __name__ == "__main__":
    annotations_path = "E:/dataset/WSODD USV_dataset/annotation"
    
    # ['animal', 'ball', 'boat', 'bridge', 'buoy', 'grass', 'harbor', 'mast', 'person', 'platform', 'rock', 'rubbish', 'ship', 'tree']
    # 删：animal，ball，bridge,mast,person,platform,rock,tree
    # boat改成ship,grass改成rubbish,harbor改成wharf,
    # 保留：buoy,rubbish,ship,wharf
    # target_classes = [, 'platform', 'rock', 'rubbish', 'ship', 'tree']
    target_classes = ['ship','rubbish','buoy', 'platform', 'wharf', 'pier']
    images_dir = "E:/dataset/WSODD USV_dataset/image"
    output_dir = "E:/dataset/WSODD USV_dataset/yolo_labels"
    output_img_dir = "E:/dataset/WSODD USV_dataset/yolo_images"
    
    dst_annotations_dir = "E:/dataset/WSODD USV_dataset/annotation_renamed"
    # rename_voc_classes(annotations_path, dst_annotations_dir)
    # print(f"已生成重命名后的标注文件到 {dst_annotations_dir}")
    defect_classes = get_all_classes(dst_annotations_dir)
    print("发现缺陷类别:", defect_classes)
    print("缺陷类别数量:", len(defect_classes))
    
    # convert_to_yolo(dst_annotations_dir, images_dir, target_classes, output_dir, output_img_dir)
    # print(f"已生成YOLO标注文件到 {output_dir}")
    # print(f"已复制相关图片到 {output_img_dir}")