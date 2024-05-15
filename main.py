import os
import re
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttks
import warnings
from tkinter import filedialog
import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning)

check_files = []
student_ids = ''
issue_count = 0

style = ttks.Style('darkly')
root_window = style.master
root_window.title('成绩核查')

# 创建新的样式
style.configure('Custom.TButton', borderwidth=2, relief='raised')

# 使用grid布局管理器
root_window.rowconfigure(0, weight=1)
root_window.columnconfigure(0, weight=1)

output_text = tk.Text(root_window, state='disabled', font=('Arial', 12))  # 创建一个只读的Text控件，并设置字体和大小
output_text.grid(row=0, column=0, sticky='nsew')


def print_to_text(s):
    output_text.config(state='normal')  # 允许写入
    output_text.insert('end', s + '\n')  # 在Text控件的末尾插入文本
    output_text.config(state='disabled')  # 禁止写入
    output_text.see('end')  # 自动滚动到Text控件的末尾


def query_xlsx(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            query_xlsx(os.path.join(path, file))
        else:
            if file.endswith(".xlsx"):
                check_files.append(os.path.join(path, file))


def open_file():
    global student_ids
    check_files.clear()  # 清空check_files列表
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        print_to_text("你没有选择文件")
        return
    try:
        data = pd.read_excel(file_path, header=1)
        student_ids = data['学号'].astype(str)
    except Exception as e:
        print_to_text(f"在处理文件{file_path}时出现了错误: {e}")


def open_folder():
    check_files.clear()  # 清空check_files列表
    folder_path = filedialog.askdirectory()
    if not folder_path:
        print_to_text("你没有选择文件夹")
        return
    query_xlsx(folder_path)


def query_csv():
    global issue_count
    issue_count = 0
    if not check_files:
        print_to_text("你没有选择任何文件（夹）进行核查")
        return
    for file in check_files:
        try:
            pending_processing = pd.read_excel(file)
            pending_processing = pending_processing[pending_processing['学号'].astype(str).isin(student_ids)]
            for index, rows in pending_processing.iterrows():
                name = rows['姓名']
                student_id = rows['学号']
                team = rows['班级']
                for column in pending_processing.columns:
                    match = re.search(r'\[(\d+)]$', column)
                    if match:
                        if rows[column] in ['优秀', '良好']:
                            rows[column] = 100
                        if rows[column] in ['及格']:
                            rows[column] = 60
                        if not pd.isna(rows[column]):
                            if rows[column] < 70:
                                print_to_text(f"{name} {student_id} {team}\n{column} {rows[column]}")
                                issue_count += 1
                            else:
                                issue_count += 0
        except Exception as e:
            print_to_text(f"在处理文件{file}时出现了错误: {e}")
    if issue_count == 0:
        print_to_text('全部通过')
    else:
        print_to_text(f'有{issue_count}处问题')


button = ttk.Button(text='上传核查表Excel文件', command=lambda: open_file(), style='Custom.TButton')  # 使用自定义样式
button.grid(row=1, column=0, sticky='nsew')  # 使用grid布局管理器，并使得Button控件填充其单元格

button2 = ttk.Button(text='上传包含各班级的Excel成绩表的文件夹', command=lambda: open_folder(), style='Custom.TButton')  # 使用自定义样式
button2.grid(row=2, column=0, sticky='nsew')  # 使用grid布局管理器，并使得Button控件填充其单元格

button3 = ttk.Button(text='开始核查', command=lambda: query_csv(), style='Custom.TButton')  # 使用自定义样式
button3.grid(row=3, column=0, sticky='nsew')  # 使用grid布局管理器，并使得Button控件填充其单元格

root_window.mainloop()
