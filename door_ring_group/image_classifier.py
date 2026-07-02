"""
图片分类标注工具：将图片分配到不同的子工件类别
"""

import argparse
import json
import tkinter as tk
from pathlib import Path
from typing import Dict, List, Set

import cv2
from PIL import Image, ImageTk

# 支持的图像格式
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}


class ImageClassifierApp:
    """图片分类标注应用"""

    def __init__(self, image_dir: str, categories: List[str], output_path: str):
        self.image_dir = Path(image_dir)
        self.output_path = Path(output_path)
        self.categories = categories

        # 收集所有图像文件
        self.image_files = sorted([
            f for f in self.image_dir.glob('*')
            if f.suffix.lower() in IMAGE_EXTENSIONS
        ])

        if not self.image_files:
            raise ValueError(f"在 {image_dir} 中未找到图像文件")

        # 分类数据：每个类别包含的图片索引集合
        self.category_images: Dict[str, Set[int]] = {
            cat: set() for cat in categories
        }

        # 当前图片索引
        self.current_index = 0

        # 当前图片的选中类别
        self.current_selection: Set[str] = set()

        # 图片缓存
        self.image_cache: Dict[int, Image.PhotoImage] = {}

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("图片分类标注工具")
        self.root.geometry("1200x800")

        self._setup_ui()
        self._load_current_image()

    def _setup_ui(self):
        """设置UI界面"""
        # 顶部信息栏
        info_frame = tk.Frame(self.root, pady=10)
        info_frame.pack(fill=tk.X)

        self.info_label = tk.Label(
            info_frame,
            text="",
            font=("Arial", 12)
        )
        self.info_label.pack()

        # 图片显示区域
        image_frame = tk.Frame(self.root)
        image_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        self.image_label = tk.Label(image_frame, bg="#f0f0f0")
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # 类别选择区域
        category_frame = tk.Frame(self.root, pady=10)
        category_frame.pack(fill=tk.X)

        tk.Label(
            category_frame,
            text="选择该图片所属的子工件（可多选）：",
            font=("Arial", 10, "bold")
        ).pack()

        checkboxes_frame = tk.Frame(category_frame)
        checkboxes_frame.pack()

        self.category_vars: Dict[str, tk.BooleanVar] = {}
        for i, category in enumerate(self.categories):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(
                checkboxes_frame,
                text=category,
                variable=var,
                command=self._on_category_change,
                font=("Arial", 11)
            )
            chk.grid(row=i // 4, column=i % 4, padx=15, pady=5, sticky="w")
            self.category_vars[category] = var

        # 按钮区域
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack(fill=tk.X)

        tk.Button(
            button_frame,
            text="上一张",
            command=self._prev_image,
            width=12,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="下一张",
            command=self._next_image,
            width=12,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="保存并退出",
            command=self._save_and_exit,
            width=15,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white"
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            button_frame,
            text="不保存退出",
            command=self.root.quit,
            width=15,
            font=("Arial", 10),
            bg="#f44336",
            fg="white"
        ).pack(side=tk.RIGHT, padx=10)

        # 键盘快捷键
        self.root.bind("<Left>", lambda e: self._prev_image())
        self.root.bind("<Right>", lambda e: self._next_image())
        self.root.bind("<Escape>", lambda e: self.root.quit())
        self.root.bind("<s>", lambda e: self._save_and_exit())
        self.root.protocol("WM_DELETE_WINDOW", self._save_and_exit)

    def _load_current_image(self):
        """加载当前图片"""
        if not self.image_files:
            return

        current_file = self.image_files[self.current_index]
        total = len(self.image_files)

        # 更新信息栏
        self.info_label.config(
            text=f"图片 {self.current_index + 1} / {total}: {current_file.name}"
        )

        # 加载图片
        if self.current_index in self.image_cache:
            photo = self.image_cache[self.current_index]
        else:
            # 中文路径兼容读取
            img = cv2.imread(str(current_file))
            if img is None:
                img_array = np.fromfile(str(current_file), dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if img is None:
                self.image_label.config(text=f"无法读取图片：{current_file.name}")
                return

            # 转换颜色空间
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # 缩放到合适大小（保持宽高比）
            h, w = img_rgb.shape[:2]
            max_size = 600
            scale = min(max_size / w, max_size / h, 1.0)
            new_w = int(w * scale)
            new_h = int(h * scale)

            if scale < 1.0:
                img_rgb = cv2.resize(img_rgb, (new_w, new_h),
                                   interpolation=cv2.INTER_AREA)

            # 转换为PIL Image
            pil_image = Image.fromarray(img_rgb)
            photo = ImageTk.PhotoImage(pil_image)
            self.image_cache[self.current_index] = photo

        self.image_label.config(image=photo, text="")

        # 更新类别选择状态
        self._update_category_checkboxes()

    def _update_category_checkboxes(self):
        """更新类别复选框状态"""
        # 清除当前选择
        self.current_selection.clear()

        # 检查当前图片已在哪些类别中
        for category in self.categories:
            if self.current_index in self.category_images[category]:
                self.category_vars[category].set(True)
                self.current_selection.add(category)
            else:
                self.category_vars[category].set(False)

    def _on_category_change(self):
        """类别选择改变时的处理"""
        # 获取之前的选择
        previous_selection = self.current_selection.copy()

        # 更新当前选择
        self.current_selection.clear()
        for category, var in self.category_vars.items():
            if var.get():
                self.current_selection.add(category)

        # 更新分类数据：移除之前的选择，添加新的选择
        for category in self.categories:
            if category in previous_selection and category not in self.current_selection:
                self.category_images[category].discard(self.current_index)
            elif category not in previous_selection and category in self.current_selection:
                self.category_images[category].add(self.current_index)

    def _prev_image(self):
        """显示上一张图片"""
        if self.current_index > 0:
            self.current_index -= 1
            self._load_current_image()

    def _next_image(self):
        """显示下一张图片"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self._load_current_image()

    def _save_and_exit(self):
        """保存结果并退出"""
        # 构建结果数据：每个类别包含的图片路径列表
        result: Dict[str, List[str]] = {
            category: [
                str(self.image_files[idx])
                for idx in sorted(self.category_images[category])
            ]
            for category in self.categories
        }

        # 添加未分类的图片
        all_classified = set()
        for indices in self.category_images.values():
            all_classified.update(indices)

        unclassified = [
            str(self.image_files[i])
            for i in range(len(self.image_files))
            if i not in all_classified
        ]

        if unclassified:
            result["未分类"] = unclassified

        # 保存JSON
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"结果已保存到：{self.output_path}")

        # 打印统计信息
        print("\n分类统计：")
        for category, images in result.items():
            print(f"  {category}: {len(images)} 张")

        self.root.destroy()

    def run(self):
        """运行应用"""
        print(f"加载了 {len(self.image_files)} 张图片")
        print(f"子工件类别：{', '.join(self.categories)}")
        print("\n快捷键：")
        print("  ← → : 上一张/下一张")
        print("  S : 保存并退出")
        print("  ESC : 不保存退出")

        self.root.mainloop()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='图片分类标注工具：将图片分配到不同的子工件类别'
    )
    parser.add_argument('--input', '-i', type=str, default=r"E:\work\Car_door_ring_splicing\image\背面打光\260622\cropped",
                        help='输入图片文件夹')
    parser.add_argument('--output', '-o', type=str, default=r"E:\work\Car_door_ring_splicing\image\背面打光\260622\cropped\group.json",
                        help='输出JSON文件路径')
    parser.add_argument('--categories', '-c', nargs='+', default=['1', '2', '3', '4', '5', '6', '7'],
                        help='子工件类别列表（可多个）')

    args = parser.parse_args()

    # 验证输入目录
    input_dir = Path(args.input)
    if not input_dir.is_dir():
        parser.error(f"输入目录不存在：{args.input}")

    # 确保类别都是字符串
    categories = [str(c) for c in args.categories]

    # 运行应用
    app = ImageClassifierApp(
        image_dir=args.input,
        categories=categories,
        output_path=args.output
    )
    app.run()


if __name__ == '__main__':
    # Windows下高DPI支持
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    import numpy as np
    main()
