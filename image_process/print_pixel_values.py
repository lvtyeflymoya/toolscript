from PIL import Image

def print_pixel_values(image_path):
    # 打开图片
    img = Image.open(image_path)
    
    # 获取图片的宽度和高度
    width, height = img.size
    
    # 获取图片的像素数据
    pixels = img.load()
    
    sum = 0
    # 遍历每个像素并打印其值
    for y in range(height):
        for x in range(width):
            pixel_value = pixels[x, y]
            if pixel_value > 0:
                sum += pixel_value
                print(f"Pixel at ({x}, {y}): {pixel_value}")
    if sum == 0:
        print("The image is empty.")
    else:
        print(sum)

# 使用示例
image_path = 'D:/zll/ImageDataSet/RuiQiSenior/SegmentationClass1\\000000.png'  # 替换为你的图片路径
print_pixel_values(image_path)
