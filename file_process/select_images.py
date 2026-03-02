import os
import shutil

def select_images(source_folder, destination_folder, interval=5):
    """
    Select every nth image from the source folder and copy it to the destination folder.

    :param source_folder: Path to the source folder containing images.
    :param destination_folder: Path to the destination folder where selected images will be copied.
    :param interval: The interval at which images are selected (default is 5).
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    images = [f for f in os.listdir(source_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
    # images.sort()  # Sort images to maintain order

    for i in range(4, len(images), interval):
        source_path = os.path.join(source_folder, images[i])
        destination_path = os.path.join(destination_folder, images[i])
        shutil.copy2(source_path, destination_path)
        print(f"Copied {images[i]} to {destination_folder}")

if __name__ == "__main__":
    source_folder = "E:/work/图纸解析/dataset/tabels_and_graphes"
    destination_folder = "E:/work/图纸解析/dataset/only_graphes"
    interval = 5

    select_images(source_folder, destination_folder, interval)
    print("Image selection and copying completed.")