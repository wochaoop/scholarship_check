import os
import re
import tkinter as tk
import warnings
from tkinter import filedialog

import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

summary_files = []
summary_data = pd.DataFrame(columns=["姓名", "学号", "班级"])
header = -1


def save_summary_path(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            save_summary_path(os.path.join(path, file))
        else:
            if file.endswith(".xlsx") or file.endswith(".xls") or file.endswith(".xlsm") or file.endswith(".xlsb"):
                summary_files.append(os.path.join(path, file))
            else:
                print(file, '不是一个表格文件')


def open_summary():
    global summary_data, header
    folder_summary = filedialog.askdirectory()
    if not folder_summary:
        print("没有选择文件")
        return
    save_summary_path(folder_summary)
    for file_path in summary_files:
        header_data = pd.read_excel(file_path)
        for index, row in header_data.iterrows():
            if "学号" in row.values:
                header = index
        if header == -1:
            print("请确认上传的文件：", file_path)
        file_data = pd.read_excel(file_path, header=header+1)
        filtered_rows = file_data[~pd.isna(file_data["学号"])]
        summary_data = pd.concat([summary_data, filtered_rows[["姓名", "学号", "班级"]]], ignore_index=True)
    print(summary_data)


window = tk.Tk()
window.title('成绩核查')
window.geometry('600x500')

button1 = tk.Button(text="上传各班汇总文件", command=lambda: open_summary())
button1.pack()

button2 = tk.Button(text="上传绩点文件", command=lambda: open_summary())
button2.pack()

window.mainloop()
