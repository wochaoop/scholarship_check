import os
import re

import pandas as pd
from tkinter import filedialog

from utils.ui_operations import print_to_text, clear_text, print_folder_tree

check_files = []
student_ids = ''
file_selected = False  # 添加一个全局变量来跟踪用户是否已经选择了一个文件或文件夹


def query_xlsx(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            query_xlsx(os.path.join(path, file))
        else:
            if file.endswith(".xlsx") or file.endswith(".xls") or file.endswith(".xlsm") or file.endswith(".xlsb"):
                check_files.append(os.path.join(path, file))


def open_file(output_text):
    global student_ids, file_selected
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls;*.xlsm;*.xlsb")])
    if not file_path:
        print_to_text(output_text, "你没有选择文件")
        return
    file_selected = True  # 用户已经选择了一个文件
    if not os.path.isfile(file_path):
        print_to_text(output_text, "你选择的文件不存在")
        return
    if not file_path.endswith((".xlsx", ".xls", ".xlsm", ".xlsb")):
        print_to_text(output_text, "你选择的文件不是Excel文件")
        return
    print_to_text(output_text, f"你选择的文件是: {os.path.basename(file_path)}")
    try:
        # 读取汇总表
        expected_columns = ['学号']  # 期望的列名
        header_row = find_header_row(file_path, expected_columns)
        if header_row is not None:
            data = pd.read_excel(file_path, header=header_row)
            student_ids = data['学号'].astype(str).str.strip().str.replace(r'\W+', '')  # 移除头尾空格和tab，移除特殊符号
        else:
            print_to_text(output_text, "未在文件的前20行中找到期望的列名")
    except Exception as e:
        print_to_text(output_text, f"在处理文件{file_path}时出现了错误: {e}")


def open_folder(output_text):
    global file_selected
    folder_path = filedialog.askdirectory()
    if not folder_path:
        print_to_text(output_text, "你没有选择文件夹")
        return
    file_selected = True  # 用户已经选择了一个文件夹
    print_to_text(output_text, f"你选择的文件夹的结构预览: {os.path.basename(folder_path)}")
    print_folder_tree(output_text, folder_path)
    query_xlsx(folder_path)


def query_excel(output_text):
    global file_selected
    clear_text(output_text)  # 在开始核查之前清空Text控件
    issue_count = 0
    error_count = 0
    found_students_set = set()  # 创建一个集合来存储在所有文件中找到的学生
    expected_columns = ['学号']  # 期望的列名
    if not file_selected:
        print_to_text(output_text, "你没有选择任何文件（夹）进行核查")
        return
    for file in check_files:
        try:
            # 读取各班级成绩表
            header_row = find_header_row(file, expected_columns)
            if header_row is not None:
                pending_processing = pd.read_excel(file, header=header_row)
                found_students = pending_processing['学号'].astype(str)
                found_students_set.update(found_students.values)  # 将在当前文件中找到的学生添加到集合中
                pending_processing = pending_processing[found_students.isin(student_ids)]
                for index, rows in pending_processing.iterrows():
                    name = rows['姓名']
                    student_id = rows['学号']
                    team = rows['班级']
                    elective_exists = False  # 用于跟踪是否存在选修科目
                    elective_chosen = False  # 用于跟踪学生是否选择了至少一个选修科目
                    for column in pending_processing.columns:
                        match = re.search(r'\[(\d+)]$', column)
                        if match:
                            if rows[column] in ['优秀', '良好']:
                                rows[column] = 80
                            elif rows[column] in ['及格']:
                                rows[column] = 60
                            elif rows[column] in ['不及格']:
                                rows[column] = 50
                            else:
                                rows[column] = pd.to_numeric(rows[column], errors='coerce')
                            if '选修' in column:
                                # 这是一个选修科目
                                elective_exists = True
                                if not pd.isna(rows[column]):
                                    elective_chosen = True
                                    # 如果分数是NaN，将其替换为 100
                                    if pd.isna(rows[column]):
                                        rows[column] = 100
                                    if rows[column] < 70:
                                        print_to_text(output_text, f"学生姓名: {name}\n"
                                                                   f"学生学号: {student_id}\n"
                                                                   f"班级: {team}\n"
                                                                   f"选修科目分数不满足条件: {column}\n"
                                                                   f"分数: {rows[column]}\n"
                                                                   f"----------------------------------------------------------------------------")
                                        issue_count += 1
                                    else:
                                        issue_count += 0
                            else:
                                # 这是一个必修科目
                                if not pd.isna(rows[column]):
                                    # 如果分数是NaN，将其替换为 0
                                    if pd.isna(rows[column]):
                                        rows[column] = 0
                                    if rows[column] < 70:
                                        print_to_text(output_text, f"学生姓名: {name}\n"
                                                                   f"学生学号: {student_id}\n"
                                                                   f"班级: {team}\n"
                                                                   f"必修科目分数不满足条件: {column}\n"
                                                                   f"分数: {rows[column]}\n"
                                                                   f"----------------------------------------------------------------------------")
                                        issue_count += 1
                                    else:
                                        issue_count += 0
                    if elective_exists and not elective_chosen:
                        print_to_text(output_text, f"学生姓名: {name}\n"
                                                   f"学生学号: {student_id}\n"
                                                   f"班级: {team}\n"
                                                   f"学生没有选择任何一个选修科目\n"
                                                   f"----------------------------------------------------------------------------")
                        issue_count += 1
            else:
                print_to_text(output_text, f"在文件{file}的前20行中未找到期望的列名")
                error_count += 1
        except FileNotFoundError:
            print_to_text(output_text, f"在处理文件{file}时出现了错误: 文件不存在")
            error_count += 1
        except pd.errors.EmptyDataError:
            print_to_text(output_text, f"在处理文件{file}时出现了错误: 文件为空")
            error_count += 1
        except pd.errors.ParserError:
            print_to_text(output_text, f"在处理文件{file}时出现了错误: 文件格式错误")
            error_count += 1
        except PermissionError:
            print_to_text(output_text, f"在处理文件{file}时出现了错误: 文件被占用。请关闭所有打开的Excel表格并重试")
            error_count += 1
        except Exception as e:
            print_to_text(output_text, f"在处理文件{file}时出现了错误: {e}")
            error_count += 1
    not_found_students = [student_id for student_id in student_ids if
                          student_id not in found_students_set]  # 找出在所有文件中都没有找到的学生
    not_found_count = len(not_found_students)
    for student_id in not_found_students:
        print_to_text(output_text, f"学生学号: {student_id} 在所有文件中都没有找到")
    if error_count > 0:
        print_to_text(output_text, f'有 {error_count} 个文件无法处理')
    if not_found_count > 0:
        print_to_text(output_text, f'有 {not_found_count} 个学生没有找到')
    if issue_count == 0:
        print_to_text(output_text, '程序运行完毕，所有学生的成绩都满足要求')
    else:
        print_to_text(output_text, f'有 {issue_count} 处学生的成绩不满足要求')


def find_header_row(file_path, expected_columns):
    for i in range(20):  # 遍历前20行
        df = pd.read_excel(file_path, header=i)
        if set(expected_columns).issubset(df.columns):
            return i
    return None
