import os
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttks


def create_window():
    style = ttks.Style('darkly')
    root_window = style.master
    root_window.title('成绩核查')
    root_window.rowconfigure(0, weight=1)
    root_window.columnconfigure(0, weight=1)
    return root_window


def create_text_widget(root_window):
    output_text = tk.Text(root_window, state='disabled', font=('Arial', 12))  # 创建一个只读的Text控件，并设置字体和大小
    output_text.grid(row=0, column=0, sticky='nsew')
    return output_text


def create_buttons(root_window, output_text, open_file, open_folder, query_csv):
    style = ttk.Style()
    style.configure('Custom.TButton', borderwidth=2, relief='raised')
    button = ttk.Button(root_window, text='上传一个Excel汇总表文件', command=lambda: open_file(output_text),
                        style='Custom.TButton')  # 使用自定义样式
    button.grid(row=1, column=0, sticky='nsew')  # 使用grid布局管理器，并使得Button控件填充其单元格
    button2 = ttk.Button(root_window, text='上传包含各班级的Excel成绩表的文件夹',
                         command=lambda: open_folder(output_text), style='Custom.TButton')  # 使用自定义样式
    button2.grid(row=2, column=0, sticky='nsew')  # 使用grid布局管理器，并使得Button控件填充其单元格
    button3 = ttk.Button(root_window, text='开始核查', command=lambda: query_csv(output_text),
                         style='Custom.TButton')  # 使用自定义样式
    button3.grid(row=3, column=0, sticky='nsew')  # 使用grid布局管理器，并使得Button控件填充其单元格


def print_to_text(output_text, s):
    output_text.config(state='normal')  # 允许写入
    output_text.insert('end', s + '\n')  # 在Text控件的末尾插入文本
    output_text.config(state='disabled')  # 禁止写入
    output_text.see('end')  # 自动滚动到Text控件的末尾


def clear_text(output_text):
    output_text.config(state='normal')  # 允许写入
    output_text.delete('1.0', 'end')  # 清空Text控件
    output_text.config(state='disabled')  # 禁止写入


def print_folder_tree(output_text, folder_path, prefix=''):
    files = []
    if os.path.isdir(folder_path):
        files = os.listdir(folder_path)
    else:
        files.append(folder_path)

    for i in range(min(len(files), 3)):  # 只列出前三个文件或子文件夹
        if i == len(files) - 1 or i == 2:  # 如果是最后一个或者已经列出了三个
            print_to_text(output_text, f"{prefix}└─{files[i]}")
            if os.path.isdir(os.path.join(folder_path, files[i])):
                print_folder_tree(output_text, os.path.join(folder_path, files[i]), prefix + "    ")
        else:
            print_to_text(output_text, f"{prefix}├─{files[i]}")
            if os.path.isdir(os.path.join(folder_path, files[i])):
                print_folder_tree(output_text, os.path.join(folder_path, files[i]), prefix + "│   ")

    if len(files) > 3:  # 如果文件或子文件夹数超过三个，输出省略号
        print_to_text(output_text, f"{prefix}├─...")
