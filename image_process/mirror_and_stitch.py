from PIL import Image
import os

def mirror_and_stitch_image(input_path, output_path=None):
    """
    将图像沿上边界镜像翻转后与原图像拼接
    
    Args:
        input_path (str): 输入图像路径
        output_path (str, optional): 输出图像路径，如果为None则自动生成
    
    Returns:
        str: 输出图像路径，如果处理失败返回None
    """
    try:
        # 打开原始图像
        original_image = Image.open(input_path)
        print(f"成功加载图像: {input_path}")
        print(f"图像尺寸: {original_image.size}")
        
        # 沿上边界镜像翻转（垂直翻转）
        mirrored_image = original_image.transpose(Image.FLIP_TOP_BOTTOM)
        
        # 获取图像尺寸
        width, height = original_image.size
        
        # 创建新的画布，高度为原图像的两倍
        new_height = height * 2
        new_image = Image.new(original_image.mode, (width, new_height))
        
        # 将镜像图像放在上方，原图像放在下方
        new_image.paste(mirrored_image, (0, 0))  # 上方：镜像图像
        new_image.paste(original_image, (0, height))  # 下方：原图像
        
        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            ext = os.path.splitext(input_path)[1]
            output_path = f"{base_name}_mirrored_stitched{ext}"
        
        # 保存结果
        new_image.save(output_path)
        print(f"镜像拼接完成！输出路径: {output_path}")
        print(f"新图像尺寸: {new_image.size}")
        
        return output_path
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_path}")
        return None
    except Exception as e:
        print(f"处理图像时发生错误: {e}")
        return None

def process_folder(input_folder, output_folder=None):
    """
    处理文件夹中的所有图像
    
    Args:
        input_folder (str): 输入文件夹路径
        output_folder (str, optional): 输出文件夹路径
    
    Returns:
        int: 成功处理的图像数量
    """
    # 支持的图像格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # 确保输出文件夹存在
    if output_folder is None:
        output_folder = os.path.join(input_folder, 'mirrored_stitched')
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")
    
    # 遍历文件夹中的所有文件
    processed_count = 0
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        
        # 检查是否为支持的图像文件
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in supported_formats:
            print(f"\n处理图像: {filename}")
            
            # 生成输出路径
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_mirrored_stitched{os.path.splitext(filename)[1]}")
            
            # 处理图像
            result = mirror_and_stitch_image(file_path, output_path)
            if result:
                processed_count += 1
    
    print(f"\n处理完成！共处理 {processed_count} 张图像")
    return processed_count

def mirror_and_stitch_demo():
    """
    演示函数：展示如何使用镜像拼接功能
    """
    print("镜像拼接功能演示")
    print("=" * 50)
    
    # 示例1：处理单个图像
    print("示例1：处理单个图像")
    # 替换为你的实际图像路径
    input_image = "E:/work/车门门环拼接/image/test/cropped_img.bmp"
    result = mirror_and_stitch_image(input_image)
    print(f"处理结果: {result}")
    
    # 示例2：处理文件夹
    print("\n示例2：处理文件夹")
    # 替换为你的实际文件夹路径
    # input_folder = "path/to/your/folder"
    # count = process_folder(input_folder)
    # print(f"成功处理 {count} 张图像")

if __name__ == "__main__":
    # 直接运行演示函数
    mirror_and_stitch_demo()