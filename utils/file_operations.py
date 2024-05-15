import os
import re

import pandas as pd
from tkinter import filedialog

from utils.ui_operations import print_to_text, clear_text, print_folder_tree

check_files = []
student_ids = ''


def query_xlsx(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            query_xlsx(os.path.join(path, file))
        else:
            if file.endswith(".xlsx") or file.endswith(".xls") or file.endswith(".xlsm") or file.endswith(".xlsb"):
                check_files.append(os.path.join(path, file))


def open_file(output_text):
    global student_ids
    check_files.clear()  # 清空check_files列表
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls;*.xlsm;*.xlsb")])
    if not file_path:
        print_to_text(output_text, "你没有选择文件")
        return
    if not os.path.isfile(file_path):
        print_to_text(output_text, "你选择的文件不存在")
        return
    if not file_path.endswith((".xlsx", ".xls", ".xlsm", ".xlsb")):
        print_to_text(output_text, "你选择的文件不是Excel文件")
        return
    print_to_text(output_text, f"你选择的文件是: {os.path.basename(file_path)}")
    try:
        data = pd.read_excel(file_path, header=1)
        student_ids = data['学号'].astype(str)
    except Exception as e:
        print_to_text(output_text, f"在处理文件{file_path}时出现了错误: {e}")


def open_folder(output_text):
    check_files.clear()  # 清空check_files列表
    folder_path = filedialog.askdirectory()
    if not folder_path:
        print_to_text(output_text, "你没有选择文件夹")
        return
    print_to_text(output_text, f"你选择的文件夹的结构预览: {os.path.basename(folder_path)}")
    print_folder_tree(output_text, folder_path)
    query_xlsx(folder_path)


def query_excel(output_text):
    clear_text(output_text)  # 在开始核查之前清空Text控件
    issue_count = 0
    error_count = 0
    if not check_files:
        print_to_text(output_text, "你没有选择任何文件（夹）进行核查")
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
                                print_to_text(output_text, f"学生姓名: {name}\n"
                                                           f"学生学号: {student_id}\n"
                                                           f"班级: {team}\n"
                                                           f"科目: {column}\n"
                                                           f"成绩: {rows[column]}\n"
                                                           f"-------------------------\n")
                                issue_count += 1
                            else:
                                issue_count += 0
        except Exception as e:
            error_count += 1
            print_to_text(output_text, f"在处理文件{file}时出现了错误: {e}")
    if error_count > 0:
        print_to_text(output_text, f'有{error_count}个文件无法处理')
    if issue_count == 0:
        print_to_text(output_text, '全部通过')
    else:
        print_to_text(output_text, f'有{issue_count}处问题')
