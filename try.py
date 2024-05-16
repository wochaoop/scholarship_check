import os
import tkinter as tk
import warnings
from tkinter import filedialog

import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning)

summary_files = []
summary_data = []


def save_summary_path(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            save_summary_path(os.path.join(path, file))
        else:
            if file.endswith(".xlsx") or file.endswith(".xls") or file.endswith(".xlsm") or file.endswith(".xlsb"):
                summary_files.append(os.path.join(path, file))
            else:
                print(file,'不是一个表格文件')


def open_summary():
    global summary_data
    folder_summary = filedialog.askdirectory()
    if not folder_summary:
        print("没有选择文件")
        return
    save_summary_path(folder_summary)
    for path in summary_files:
        data = pd.read_excel(path)
        print(data.columns)
        # for index, row in data.iterrows():
        #     if pd.isnull(row["学号"]):
        #         pass
        #     else:
        #         print(row["学号"].astype(int), row["姓名"].astype(str), row["班级"].astype(str))


window = tk.Tk()
window.title('成绩核查')
window.geometry('600x500')

button1 = tk.Button(text="上传汇总文件", command=lambda: open_summary())
button1.pack()

window.mainloop()
