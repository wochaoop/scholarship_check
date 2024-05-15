import os
import re
import tkinter as tk
import warnings
from tkinter import filedialog
import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning)

check_files = []
student_ids = ''
issue_count = 0


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
        print("你没有选择文件")
        return
    try:
        data = pd.read_excel(file_path, header=1)
        student_ids = data['学号'].astype(str)
    except Exception as e:
        print(f"在处理文件{file_path}时出现了错误: {e}")


def open_folder():
    check_files.clear()  # 清空check_files列表
    folder_path = filedialog.askdirectory()
    if not folder_path:
        print("你没有选择文件夹")
        return
    query_xlsx(folder_path)


def query_csv():
    global issue_count
    issue_count = 0
    if not check_files:
        print("你没有选择任何文件（夹）进行核查")
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
                                print(name, student_id, team)
                                print(column, rows[column])
                                issue_count += 1
                            else:
                                issue_count += 0
        except Exception as e:
            print(f"在处理文件{file}时出现了错误: {e}")
    if issue_count == 0:
        print('全部通过')
    else:
        print('有{}处问题'.format(issue_count))


root_window = tk.Tk()
root_window.title('成绩核查')
root_window.geometry('600x500')

button = tk.Button(text='上传核查表Excel文件', command=lambda: open_file())
button.pack()

button2 = tk.Button(text='上传包含各班级的Excel成绩表的文件夹', command=lambda: open_folder())
button2.pack()

button3 = tk.Button(text='开始核查', command=lambda: query_csv())
button3.pack()

root_window.mainloop()
