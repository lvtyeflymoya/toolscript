import os
import glob

def adjust_yolo_labels(input_file, output_file):
    """
    读取YOLO格式的标注文件，将类别编号减1，并保存到新的文件中。

    :param input_file: 输入的YOLO格式标注文件路径
    :param output_file: 输出的YOLO格式标注文件路径
    """
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                parts = line.strip().split()
                if len(parts) < 5:
                    print(f"跳过无效行: {line.strip()}")
                    continue
                try:
                    class_id = int(parts[0]) - 1  # 类别编号减1
                    if class_id < 0:
                        print(f"警告: 类别编号小于0，跳过行: {line.strip()}")
                        continue
                    new_line = f"{class_id} " + " ".join(parts[1:]) + "\n"
                    outfile.write(new_line)
                except ValueError:
                    print(f"跳过无法解析的行: {line.strip()}")
    
        print(f"处理完成，结果已保存到 {output_file}")
    except FileNotFoundError:
        print(f"文件 {input_file} 未找到！")
    except Exception as e:
        print(f"发生错误: {e}")

def adjust_yolo_labels_in_directory(input_dir, output_dir):
    """
    处理一个文件夹下的所有YOLO格式的标注文件，将类别编号减1，并保存到新的文件中。

    :param input_dir: 输入的文件夹路径，包含YOLO格式标注文件
    :param output_dir: 输出的文件夹路径，用于保存处理后的文件
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取文件夹下所有txt文件
    input_files = glob.glob(os.path.join(input_dir, "*.txt"))

    for input_file in input_files:
        # 获取文件名
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, file_name)

        # 调用单文件处理函数
        adjust_yolo_labels(input_file, output_file)

if __name__ == "__main__":
    # 输入文件路径
    input_file = "E:/work/图纸解析/dataset/simple_angle_steel_images/YOLO_Format/labels/val/253_26_roi5.txt"  # 替换为你的输入文件路径
    # 输出文件路径
    output_file = "output.txt"  # 替换为你的输出文件路径

    # 调用函数处理文件
    # adjust_yolo_labels(input_file, output_file)

    # 输入文件夹路径
    input_dir = "E:/work/图纸解析/dataset/complex_angle_steel_images/label/YOLO"  # 替换为你的输入文件夹路径
    # 输出文件夹路径
    output_dir = "label_txt_processed"  # 替换为你的输出文件夹路径

    # 调用函数处理文件夹
    adjust_yolo_labels_in_directory(input_dir, output_dir)