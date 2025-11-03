from PIL import Image
import os

def add_white_border(image_path, border_width, output_path=None):
    """
    在图像周围添加指定宽度的白色边框
    
    Args:
        image_path (str): 输入图像路径
        border_width (int): 边框宽度（像素）
        output_path (str, optional): 输出图像路径，如果为None则自动生成
    
    Returns:
        str: 输出图像路径，如果处理失败返回None
    """
    try:
        # 打开原始图像
        original_image = Image.open(image_path)
        print(f"成功加载图像: {image_path}")
        print(f"原始图像尺寸: {original_image.size}")
        print(f"边框宽度: {border_width} 像素")
        
        # 获取原始图像尺寸
        width, height = original_image.size
        
        # 计算新图像的尺寸（四周都添加边框）
        new_width = width + 2 * border_width
        new_height = height + 2 * border_width
        
        # 创建新的白色背景图像
        if original_image.mode == 'RGBA':
            # 对于RGBA图像，使用白色透明背景
            new_image = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 255))
        else:
            # 对于其他模式，使用白色背景
            # 修复：使用正确的颜色格式
            if original_image.mode == 'L':  # 灰度图像
                background_color = 255
            elif original_image.mode == 'RGB':
                background_color = (255, 255, 255)
            elif original_image.mode == 'P':  # 调色板模式
                background_color = 255
            else:
                # 默认转换为RGB模式
                original_image = original_image.convert('RGB')
                background_color = (255, 255, 255)
            
            new_image = Image.new(original_image.mode, (new_width, new_height), background_color)
        
        # 将原始图像粘贴到新图像的中心
        paste_position = (border_width, border_width)
        new_image.paste(original_image, paste_position)
        
        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_with_border_{border_width}px{ext}"
        
        # 保存结果
        new_image.save(output_path)
        print(f"边框添加完成！输出路径: {output_path}")
        print(f"新图像尺寸: {new_image.size}")
        
        return output_path
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {image_path}")
        return None
    except Exception as e:
        print(f"处理图像时发生错误: {e}")
        return None

def add_white_border_custom(image_path, top_border, right_border, bottom_border, left_border, output_path=None):
    """
    在图像周围添加不同宽度的白色边框（可分别指定四个边的宽度）
    
    Args:
        image_path (str): 输入图像路径
        top_border (int): 上边框宽度（像素）
        right_border (int): 右边框宽度（像素）
        bottom_border (int): 下边框宽度（像素）
        left_border (int): 左边框宽度（像素）
        output_path (str, optional): 输出图像路径，如果为None则自动生成
    
    Returns:
        str: 输出图像路径，如果处理失败返回None
    """
    try:
        # 打开原始图像
        original_image = Image.open(image_path)
        print(f"成功加载图像: {image_path}")
        print(f"原始图像尺寸: {original_image.size}")
        print(f"边框宽度: 上={top_border}, 右={right_border}, 下={bottom_border}, 左={left_border} 像素")
        
        # 获取原始图像尺寸
        width, height = original_image.size
        
        # 计算新图像的尺寸
        new_width = width + left_border + right_border
        new_height = height + top_border + bottom_border
        
        # 创建新的白色背景图像
        if original_image.mode == 'RGBA':
            new_image = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 255))
        else:
            # 修复：使用正确的颜色格式
            if original_image.mode == 'L':  # 灰度图像
                background_color = 255
            elif original_image.mode == 'RGB':
                background_color = (255, 255, 255)
            elif original_image.mode == 'P':  # 调色板模式
                background_color = 255
            else:
                # 默认转换为RGB模式
                original_image = original_image.convert('RGB')
                background_color = (255, 255, 255)
            
            new_image = Image.new(original_image.mode, (new_width, new_height), background_color)
        
        # 将原始图像粘贴到新图像的正确位置
        paste_position = (left_border, top_border)
        new_image.paste(original_image, paste_position)
        
        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_with_custom_border{ext}"
        
        # 保存结果
        new_image.save(output_path)
        print(f"自定义边框添加完成！输出路径: {output_path}")
        print(f"新图像尺寸: {new_image.size}")
        
        return output_path
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {image_path}")
        return None
    except Exception as e:
        print(f"处理图像时发生错误: {e}")
        return None

def process_folder_with_border(input_folder, border_width, output_folder=None):
    """
    处理文件夹中的所有图像，为每张图像添加白色边框
    
    Args:
        input_folder (str): 输入文件夹路径
        border_width (int): 边框宽度（像素）
        output_folder (str, optional): 输出文件夹路径
    
    Returns:
        int: 成功处理的图像数量
    """
    # 支持的图像格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # 确保输出文件夹存在
    if output_folder is None:
        output_folder = os.path.join(input_folder, f'with_border_{border_width}px')
    
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
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_with_border_{border_width}px{os.path.splitext(filename)[1]}")
            
            # 处理图像
            result = add_white_border(file_path, border_width, output_path)
            if result:
                processed_count += 1
    
    print(f"\n处理完成！共处理 {processed_count} 张图像")
    return processed_count

def white_border_demo():
    """
    演示函数：展示如何使用白色边框功能
    """
    print("白色边框功能演示")
    print("=" * 50)
    
    # 示例1：为单张图像添加等宽边框
    print("示例1：为单张图像添加等宽边框")
    
    # 替换为你的实际图像路径
    input_image = "E:/work/车门门环拼接/image/test/cropped_img_mirrored_stitched.bmp"
    result = add_white_border(input_image, 50)  # 添加50像素宽的边框
    print(f"处理结果: {result}")
    
    # 示例2：为单张图像添加自定义边框
    # print("\n示例2：为单张图像添加自定义边框")
    # result = add_white_border_custom(input_image, 20, 40, 60, 80)  # 上20,右40,下60,左80像素
    # print(f"处理结果: {result}")
    
    # 示例3：处理文件夹
    # print("\n示例3：处理文件夹")
    # input_folder = "path/to/your/folder"
    # count = process_folder_with_border(input_folder, 30)  # 为所有图像添加30像素边框
    # print(f"成功处理 {count} 张图像")
    
if __name__ == "__main__":
    # 直接运行演示函数
    white_border_demo()