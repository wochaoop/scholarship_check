import os

from PyQt6.QtWidgets import QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('成绩核查')
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        self.button_open_file = QPushButton('选择一个Excel汇总表 文件', self)
        self.button_open_folder = QPushButton('选择包含各班级的Excel成绩表的 文件夹', self)
        self.button_query_csv = QPushButton('开始核查', self)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button_open_file)
        layout.addWidget(self.button_open_folder)
        layout.addWidget(self.button_query_csv)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

def print_to_text(self, s):
    self.text_edit.append(s)

def clear_text(self):
    self.text_edit.clear()

def print_folder_tree(self, folder_path, prefix=''):
    files = []
    if os.path.isdir(folder_path):
        files = os.listdir(folder_path)
    else:
        files.append(folder_path)

    for i in range(min(len(files), 3)):  # 只列出前三个文件或子文件夹
        if i == len(files) - 1 or i == 2:  # 如果是最后一个或者已经列出了三个
            self.print_to_text(f"{prefix}└─{files[i]}")
            if os.path.isdir(os.path.join(folder_path, files[i])):
                self.print_folder_tree(os.path.join(folder_path, files[i]), prefix + "    ")
        else:
            self.print_to_text(f"{prefix}├─{files[i]}")
            if os.path.isdir(os.path.join(folder_path, files[i])):
                self.print_folder_tree(os.path.join(folder_path, files[i]), prefix + "│   ")

    if len(files) > 3:  # 如果文件或子文件夹数超过三个，输出省略号
        self.print_to_text(f"{prefix}├─...")
