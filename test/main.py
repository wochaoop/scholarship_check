import os.path
from tkinter import filedialog

import pandas as pd

summary_files = []  # 存储各班汇总表文件夹中的表格路径
summary_data = pd.DataFrame(columns=['学号', '班级', '姓名'])  # 存储从各班汇总表中读取的数据，避免保存学生身份证号等敏感信息


# 读取汇总文件的数据
def read_summary_files_data():
    global summary_files, summary_data
    for file_path in summary_files:
        # 由于汇总文件是各班接收上来的数据，导致数据表格的格式层次不齐，所以这里需要先读取一次表格用于获取表头的位置
        header_data = pd.read_excel(file_path)
        header = 0  # 保存每张表格的表头在第几行
        for index, row in header_data.iterrows():
            if '学号' in row.values:
                header = index
                break
        # 当获取到表头在那个位置之后就可以放心的读取表格数据，将获得奖学金的学生的班级、姓名、学号数据保存起来
        # 注意，不要保存学生的敏感数据，这样会造成不必要的麻烦
        file_data = pd.read_excel(file_path, header=header + 1)
        # 因为有些班级的上交的表格中的数据数据较少，这里我们需要去除学号为空的数据，以免浪费不必要的存储空间
        student_data = file_data[~pd.isna(file_data['学号'])]
        # 将获取的数据存储到 summary_data 中，方便我们的后续操作
        summary_data = pd.concat([summary_data, student_data[['学号', '班级', '姓名']]], ignore_index=True)


# 根据用户传入的文件夹路径和要将读取的文件路径存储的变量，将用户选择的文件夹的所有表格文件的路径保存起来
def save_file_path(path, save_path):
    for file in os.listdir(path):  # 循环文件夹中的文件
        if os.path.isdir(os.path.join(path, file)):  # 如果文件夹中的文件依旧为文件夹，则进行递归操作
            save_file_path(os.path.join(path, file), save_path)  # 一个简单的递归
        else:
            if file.endswith(".xlsx") or file.endswith(".xls") or file.endswith(".xlsm") or file.endswith(".xlsb"):
                # 如果文件夹中的文件为表格文件，则将其保存到给定的变量中字典中
                save_path.append(os.path.join(path, file))
            else:
                print(file, '不是一个 excel 文件')  # 如果包含的文件不是 excel 文件，则给用户提示报错


def open_summary_files():
    folder_summary = os.path.abspath('../data/2024年春校内奖学金/各班汇总表')  # 在开发过程中写一个固定的路径，方便我们使用
    # folder_summary = filedialog.askopenfilename()  # 打开文件选择器，让用户自主选择各班汇总文件所在的文件路径
    if not folder_summary:  # 如果用户未选择任何文件夹，则显示报错，并 return 出该函数
        print('为选择文件')
        return
    save_file_path(folder_summary, summary_files)
    read_summary_files_data()
    student_number = 0
    for index, row in summary_data.iterrows():
        print(row['学号'], row['班级'], row['姓名'])
        student_number += 1
    print('总共读取到{}位学生数据', student_number)


open_summary_files()