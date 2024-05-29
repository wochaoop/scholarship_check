import os
import re
import tkinter as tk
import warnings
from tkinter import filedialog

import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

summary_files = []  # 存储各班汇总文件中的表格的路径
summary_data = pd.DataFrame(columns=["学号", "班级", "姓名"])  # 存储从各班汇总表格中汇总出来的数据，只存储姓名，学号，班级
header = 0  # 在读取各班汇总文件的时候动态获取表头位置：表头，忽略标题
gpa_files = []  # 存储绩点文件总表格的路径


# 根据用户选择的汇总文件夹，读取其中的 excel 文件的路径，然后保存到 summary_files 字典中
def save_summary_path(path):
    for file in os.listdir(path):  # 循环文件夹中的文件
        if os.path.isdir(os.path.join(path, file)):  # 如果文件夹中的文件依旧是文件夹，则进行递归操作
            save_summary_path(os.path.join(path, file))  # 一个简单的递归
        else:
            if file.endswith(".xlsx") or file.endswith(".xls") or file.endswith(".xlsm") or file.endswith(".xlsb"):
                # 如果文件夹中的文件为表格文件，则将其保存到 summary_files 字典中
                summary_files.append(os.path.join(path, file))
            else:
                print(file, '不是一个 excel 文件')  # 如果包含的文件不是 excel 文件，则给用户提示报错


# 处理学号格式问题
def process_student_id(student_id):
    if isinstance(student_id, float):  # 如果数据格式为浮点数，则给他先转为整数再转为字符串
        student_id = int(student_id)
    if isinstance(student_id, str):  # 如果数据格式为字符串，则需要给他去除首尾空格
        student_id = int(student_id.strip())
    return student_id


# 处理姓名格式问题
def process_name(name):
    name = name.strip()  # 去除首尾空格
    name = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', name)  # 将两个字中间的空格删除
    return name


# 处理班级格式问题
def process_grade(grade):
    grade = grade.strip()  # 去除班级前面的空格
    grade = re.sub(r'班$', '', grade)
    return grade


# 删除班级数据中的空格及其中的内容
def remove_parentheses_and_contents(grade):
    # 替换括号内恰好为“技能”的内容为“本科”
    grade = re.sub(r'(（技能）)', '本科', grade)
    grade = re.sub(r'(\(技能\))', '本科', grade)
    # 删除其他所有括号及其内容
    grade = re.sub(r'（[^（）]*）', '', grade)
    grade = re.sub(r'\([^()]*\)', '', grade)
    return grade


# 检查班级中的数据最后两位是否是数字
def standardize_grade(grade):
    # 使用正则表达式匹配末尾的一位或两位数字
    match = re.search(r'(\d{1,2})$', grade)
    if match:
        # 如果有匹配，则获取班级编号
        class_suffix = match.group()
        # 如果班级编号只有一位数字，则在其前面添加0
        if len(class_suffix) == 1:
            class_suffix = '0' + class_suffix
        # 替换原始字符串中的最后一位或两位数字为标准化的班级编号
        return re.sub(r'(\d{1,2})$', class_suffix, grade)
    else:
        # 如果没有匹配到数字，则返回原始字符串（或者根据需求进行其他处理）
        return grade


# 打开各班汇总文件
# 此函数的目的是在用户选择各班汇总文件夹后，将内部的所有 excel 文件的文件路径保存到 summary_file 中，
# 然后根据文件路径，将所有的姓名、学号、班级信息汇总成一个字典 summary_data
def open_summary():
    global summary_data, header
    folder_summary = filedialog.askdirectory()  # 打开文件选择器，让用户选择文件夹
    if not folder_summary:
        print("没有选择文件")  # 若用户未打开文件夹，则显示报错，并 return 出函数
        return
    save_summary_path(folder_summary)
    # 使用 save_summary_path 函数将文件夹中的所有 excel 文件的路径保存到 summary_files 中
    for file_path in summary_files:
        header_data = pd.read_excel(file_path)  # 先读取一次表格，根据学号所在的行，确定表头位置
        for index, row in header_data.iterrows():
            if "学号" in row.values:
                header = index  # 保存表头位置
                break
        file_data = pd.read_excel(file_path, header=header + 1)  # 根据保存的表头位置，排除表格中的标题
        filtered_rows = file_data[~pd.isna(file_data["学号"])]  # 排除学号为空的行
        # 将表格中的姓名、学号、班级等信息保存到 summary_data 字典中
        summary_data = pd.concat([summary_data, filtered_rows[["姓名", "学号", "班级"]]], ignore_index=True)
    # 由于该数据表格是手打收集的，所以我们拿到的数据可能会参差不齐，所以需要我们对每个数据进行处理
    summary_data['学号'] = summary_data['学号'].apply(process_student_id)
    summary_data['姓名'] = summary_data['姓名'].apply(process_name)
    summary_data['班级'] = summary_data['班级'].apply(process_grade)
    summary_data['班级'] = summary_data['班级'].apply(remove_parentheses_and_contents)
    summary_data['班级'] = summary_data['班级'].apply(standardize_grade)
    print(summary_data)


# 这个函数和上面的 save_summary_path 函数的效果是一样的
# 只不过这个函数是保存绩点文件的路径，上个 save_summary_path 保存的是各班汇总文件的路径
def save_gpa_path(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            save_gpa_path(os.path.join(path, file))
        else:
            if file.endswith(".xlsx") or file.endswith(".xls") or file.endswith(".xlsm") or file.endswith(".xlsb"):
                gpa_files.append(os.path.join(path, file))
            else:
                print(os.path.join(path, file), '不是一个 excel 文件')


# 打开绩点文件夹，保存绩点文件中的 excel 表格的路径
def open_gpa():
    global gpa_files
    folder_gpa = filedialog.askdirectory()  # 打开文件选择器，让用户选择文件夹
    if not folder_gpa:  # 若用户未选择文件，则弹出报错
        print("没有选择文件")
        return
    save_gpa_path(folder_gpa)
    # 使用 save_gpa_path 函数将文件夹中的所有 excel 文件的路径保存到 gpa_files 字典中
    print(gpa_files)


# 开始进行核查操作
def check():
    global summary_data, gpa_files
    success_student = pd.DataFrame(columns=['学号', '班级', '姓名'])
    rows_to_drop = []
    total = 0
    for gpa_file_path in gpa_files:  # 循环保存好的 gpa_files 字典数据，根据每一项的路径读取该文件
        gpa_data = pd.read_excel(gpa_file_path, header=0)
        grade = remove_parentheses_and_contents(gpa_data['班级'].iloc[0])
        filtered_data = summary_data.loc[summary_data['班级'] == grade]
        if len(filtered_data) == 0:
            print('============请检查', grade, '在各班汇总表中的写法是否符合绩点文件中的写法===========')
        else:
            success_student = pd.concat([success_student, filtered_data], ignore_index=True)
            rows_to_drop.extend(filtered_data.index.tolist())
    print(success_student)
    summary_data = summary_data.drop(rows_to_drop)
    print(summary_data, '这些数据是含有问题的数据')


window = tk.Tk()
window.title('成绩核查')
window.geometry('600x500')

button1 = tk.Button(text="上传各班汇总文件", command=lambda: open_summary())
button1.pack()

button2 = tk.Button(text="上传绩点文件", command=lambda: open_gpa())
button2.pack()

button3 = tk.Button(text="核查", command=lambda: check())
button3.pack()

window.mainloop()
