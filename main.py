import os
import re
import tkinter as tk
import warnings
from tkinter import filedialog
import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning)

check = []
studentId = ''
determine = 0


def open_file():
    global studentId
    studentId = ''
    a = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    b = pd.read_excel(a, header=1)
    studentId = b['学号'].astype(str)


def query_xlsx(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            query_xlsx(os.path.join(path, file))
        else:
            if file.endswith(".xlsx"):
                check.append(os.path.join(path, file))
            else:
                print(file+'不是表格文件')


def open_folder():
    global check
    check = []
    a = filedialog.askdirectory()
    query_xlsx(a)


def query_csv():
    global determine
    determine = 0
    for file in check:
        pending_processing = pd.read_excel(file)
        pending_processing = pending_processing[pending_processing['学号'].astype(str).isin(studentId)]
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
                            determine += 1
                        else:
                            determine += 0
    if determine == 0:
        print('全部通过')
    else:
        print('有{}处问题'.format(determine))



root_window = tk.Tk()
root_window.title('成绩核查')
root_window.geometry('600x500')

button = tk.Button(text='上传核查表', command=lambda: open_file())
button.pack()

button2 = tk.Button(text='上传绩点文件', command=lambda: open_folder())
button2.pack()

button3 = tk.Button(text='开始核查', command=lambda: query_csv())
button3.pack()

root_window.mainloop()
