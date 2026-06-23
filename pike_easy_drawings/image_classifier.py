"""PySide6 图片分类小工具：把源文件夹中的图片快速人工分类为「简单」和「困难」两类。

用法：python image_classifier.py
快捷键：← / → 切换上一张/下一张；1 = 复制到简单；2 = 复制到困难。
"""

from __future__ import annotations

import os
import shutil
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff", ".gif"}
)


class ImageClassifierApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("图片分类工具 - 简单 / 困难")
        self.resize(1100, 780)

        self.source_folder: str = ""
        self.simple_folder: str = ""
        self.hard_folder: str = ""
        self.image_files: list[str] = []
        self.classified: set[str] = set()
        self.current_index: int = -1
        self._current_pixmap: QPixmap | None = None

        self._build_ui()
        self._update_button_states()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # 顶部：源文件夹按钮 + 源路径 + 进度
        self.btn_open_source = QPushButton("打开源文件夹")
        self.btn_open_source.clicked.connect(self._select_source_folder)
        self.lbl_source = QLabel("源: (未选择)")
        self.lbl_source.setStyleSheet("color: #555;")
        self.lbl_progress = QLabel("进度: 0/0")
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.btn_open_source)
        top_bar.addWidget(self.lbl_source, stretch=1)
        top_bar.addWidget(self.lbl_progress)
        root.addLayout(top_bar)

        # 图片查看区
        self.image_label = QLabel("请先点击「打开源文件夹」")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2b2b2b; color: #bbb; font-size: 16px;")
        self.image_label.setMinimumHeight(420)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #2b2b2b; border: none; }")
        root.addWidget(self.scroll_area, stretch=1)

        # 目标文件夹行：用 QLabel 而非只读 QLineEdit，避免吃掉左右箭头键
        self.simple_label = self._make_folder_label()
        self.hard_label = self._make_folder_label()
        btn_pick_simple = QPushButton("选择")
        btn_pick_simple.clicked.connect(lambda: self._select_target_folder("simple"))
        btn_pick_hard = QPushButton("选择")
        btn_pick_hard.clicked.connect(lambda: self._select_target_folder("hard"))

        simple_row = QHBoxLayout()
        simple_row.addWidget(QLabel("简单文件夹:"))
        simple_row.addWidget(self.simple_label, stretch=1)
        simple_row.addWidget(btn_pick_simple)
        root.addLayout(simple_row)

        hard_row = QHBoxLayout()
        hard_row.addWidget(QLabel("困难文件夹:"))
        hard_row.addWidget(self.hard_label, stretch=1)
        hard_row.addWidget(btn_pick_hard)
        root.addLayout(hard_row)

        # 底部四个操作按钮，快捷键挂在按钮上以确保全局生效
        self.btn_prev = QPushButton("上一张  (←)")
        self.btn_prev.setShortcut(Qt.Key.Key_Left)
        self.btn_prev.clicked.connect(self._prev_image)

        self.btn_next = QPushButton("下一张  (→)")
        self.btn_next.setShortcut(Qt.Key.Key_Right)
        self.btn_next.clicked.connect(self._next_image)

        self.btn_copy_simple = QPushButton("复制到简单  (1)")
        self.btn_copy_simple.setShortcut(Qt.Key.Key_1)
        self.btn_copy_simple.clicked.connect(lambda: self._copy_to("simple"))

        self.btn_copy_hard = QPushButton("复制到困难  (2)")
        self.btn_copy_hard.setShortcut(Qt.Key.Key_2)
        self.btn_copy_hard.clicked.connect(lambda: self._copy_to("hard"))

        btn_row = QHBoxLayout()
        for btn in (self.btn_prev, self.btn_next, self.btn_copy_simple, self.btn_copy_hard):
            btn.setMinimumHeight(36)
            btn_row.addWidget(btn)
        root.addLayout(btn_row)

        self.setStatusBar(QStatusBar())

    @staticmethod
    def _make_folder_label() -> QLabel:
        label = QLabel("未选择")
        label.setStyleSheet(
            "padding: 6px 8px; border: 1px solid #bbb; border-radius: 3px; "
            "background: #f6f6f6; color: #333;"
        )
        label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        return label

    def _select_source_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "选择源图片文件夹", self.source_folder or "")
        if not folder:
            return
        self.source_folder = folder
        self.classified.clear()
        self.current_index = -1
        self._load_images()
        if self.image_files:
            self.current_index = 0
            self._show_current()
        else:
            self._current_pixmap = None
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("该文件夹中没有支持的图片")
        self.lbl_source.setText(f"源: {folder}")
        self._update_button_states()

    def _select_target_folder(self, kind: str) -> None:
        label_text = "简单" if kind == "simple" else "困难"
        folder = QFileDialog.getExistingDirectory(self, f"选择{label_text}目标文件夹", "")
        if not folder:
            return
        if kind == "simple":
            self.simple_folder = folder
            self.simple_label.setText(folder)
            self.simple_label.setStyleSheet(
                "padding: 6px 8px; border: 1px solid #4a9; border-radius: 3px; "
                "background: #f0fff5; color: #234;"
            )
        else:
            self.hard_folder = folder
            self.hard_label.setText(folder)
            self.hard_label.setStyleSheet(
                "padding: 6px 8px; border: 1px solid #c84; border-radius: 3px; "
                "background: #fff8f0; color: #421;"
            )
        self._update_button_states()

    def _load_images(self) -> None:
        self.image_files = []
        if not self.source_folder or not os.path.isdir(self.source_folder):
            return
        for name in sorted(os.listdir(self.source_folder)):
            if os.path.splitext(name)[1].lower() in SUPPORTED_EXTENSIONS:
                self.image_files.append(name)

    def _show_current(self) -> None:
        if not self.image_files or not (0 <= self.current_index < len(self.image_files)):
            return
        name = self.image_files[self.current_index]
        pix = QPixmap(os.path.join(self.source_folder, name))
        if pix.isNull():
            self._current_pixmap = None
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(f"无法加载图片: {name}")
        else:
            self._current_pixmap = pix
            self._render_scaled()

        total = len(self.image_files)
        position = self.current_index + 1
        mark = "   ✓ 已分类" if name in self.classified else ""
        self.lbl_progress.setText(f"进度: {position}/{total}{mark}")
        self.statusBar().showMessage(f"当前: {name}")
        self._update_button_states()

    def _render_scaled(self) -> None:
        if self._current_pixmap is None:
            return
        avail = self.scroll_area.viewport().size()
        if avail.width() <= 20 or avail.height() <= 20:
            return
        scaled = self._current_pixmap.scaled(
            avail.width() - 20,
            avail.height() - 20,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)

    def _next_image(self) -> None:
        if not self.image_files:
            return
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self._show_current()
        else:
            self.statusBar().showMessage("已经是最后一张")

    def _prev_image(self) -> None:
        if not self.image_files:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self._show_current()
        else:
            self.statusBar().showMessage("已经是第一张")

    def _copy_to(self, kind: str) -> None:
        if not self.image_files or not (0 <= self.current_index < len(self.image_files)):
            return
        if kind == "simple":
            target_folder = self.simple_folder
            label_text = "简单"
        else:
            target_folder = self.hard_folder
            label_text = "困难"
        if not target_folder:
            self.statusBar().showMessage(f"未设置{label_text}文件夹，请先点击「选择」")
            return

        name = self.image_files[self.current_index]
        src = os.path.join(self.source_folder, name)
        dst = os.path.join(target_folder, name)
        try:
            shutil.copy2(src, dst)
        except OSError as exc:
            self.statusBar().showMessage(f"复制失败: {exc}")
            return

        self.classified.add(name)
        self.statusBar().showMessage(f"已复制到{label_text}: {dst}")
        self._next_image()

    def _update_button_states(self) -> None:
        has_images = bool(self.image_files)
        self.btn_prev.setEnabled(has_images and self.current_index > 0)
        self.btn_next.setEnabled(has_images and self.current_index < len(self.image_files) - 1)
        self.btn_copy_simple.setEnabled(has_images and bool(self.simple_folder))
        self.btn_copy_hard.setEnabled(has_images and bool(self.hard_folder))

    def resizeEvent(self, event) -> None:  # noqa: D401 - signature fixed by Qt
        super().resizeEvent(event)
        self._render_scaled()


def main() -> None:
    app = QApplication(sys.argv)
    window = ImageClassifierApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
