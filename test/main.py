import os.path
import re
import warnings
from tkinter import filedialog

import pandas as pd

# 忽略一些警告
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

summary_files = []  # 存储各班汇总表文件夹中的表格路径
summary_data = pd.DataFrame(columns=['学号', '班级', '姓名'])  # 存储从各班汇总表中读取的数据，避免保存学生身份证号等敏感信息
gpa_files = []  # 存储绩点文件夹中的表格路径
success_student = pd.DataFrame(columns=['学号', '班级', '姓名'])  # 上传绩点文件之后，将从汇总文件读取的学生数据与汇总文件进行比对，核对成功的数据保存到这个变量中


# 汇总文件中的学号数据有的为浮点类型，有的为字符串类型，这时候需要把它们全部转变为整形，以便后面的与绩点文件中的数据做读取
def process_student_id(student_id):
    if isinstance(student_id, float):  # 当检测到学号为浮点类型，直接转换为整形即可
        student_id = int(student_id)
    if isinstance(student_id, str):  # 当检测到学号为字符串类型，需要增加一个去除首尾空格的操作，这是汇总表中常见的错误
        try:  # 这里加入 try 是为了防止汇总表中的学号中间出现空格的情况，因为这种情况过于罕见，所以直接提示出来让用户手动修改
            student_id = int(student_id.strip())
        except ValueError:
            print('警告！！！' + student_id + '不是合法的学号格式===============')
    return student_id  # 不要忘记将处理好的数据 return 出来


# 汇总文件中的学生姓名的数据可能出现了首位存在空格或姓名中间出现空格的情况，需要全部清除
def process_student_name(student_name):
    student_name = student_name.strip()  # 去除首尾空格
    student_name = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', student_name)  # 去除两个字中间的空格
    return student_name  # 将处理的结果输出出来


# 班级数据最难处理，因为很可能出现以下情况
# 1. 首尾出现空格
# 2. 在我们学校的数据中班级名称的最后一个字是没有班的，有可能会出现班这个字
# 3. 班级的最后两位应为数字，即 01 或 02，可能会出现有些班级的数字只有一位
# 4. 有些班级的名字中出现括号表示班级名称，但是汇总文件中不一定会按照标准来写
# 对于第四点，这里的做法是采用移除汇总文件和绩点文件中的括号及其内部的内容，但是因为存在移除后会出现班级名称重叠的情况，所以需要对部分的括号内的内容做特殊处理
def process_student_class(student_class):
    # 解决第一个问题，处理首尾空格
    student_class = student_class.strip()
    # 解决第二个问题，处理删除名称后的最后一个班字
    student_class = re.sub(r'班$', '', student_class)
    # 解决第三个问题，检查班级名称的最后两个字符是否为数字，若不是则做处理
    match = re.search(r'(\d{1,2})$', student_class)  # 使用正则表达式匹配末尾的一位或两位数字
    if match:
        class_suffix = match.group()  # 如果有匹配，则将其暂时保存到 class_suffix 变量中
        if len(class_suffix) == 1:  # 如果这个数据只有一位数字，则在其前面添加 0
            class_suffix = '0' + class_suffix
        student_class = re.sub(r'(\d{1,2})$', class_suffix, student_class)  # 将处理好的数据重新拼接回原数据中
    # 解决第四个问题，处理班级名称中出现括号的问题
    # 替换括号内恰好为“技能”的内容为“本科”
    student_class = re.sub(r'(（技能）)', '本科', student_class)
    student_class = re.sub(r'(\(技能\))', '本科', student_class)
    # 删除其他所有括号及其内容
    student_class = re.sub(r'（[^（）]*）', '', student_class)
    student_class = re.sub(r'\([^()]*\)', '', student_class)
    return student_class  # 最后将处理好的班级名称 return 出去


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
    # 当读取到所有的汇总数据时，发现格式并不统一，以下的操作为处理数据
    summary_data['学号'] = summary_data['学号'].apply(process_student_id)
    summary_data['姓名'] = summary_data['姓名'].apply(process_student_name)
    summary_data['班级'] = summary_data['班级'].apply(process_student_class)


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
    # folder_summary = filedialog.askdirectory()  # 打开文件夹选择器，让用户自主选择各班汇总文件夹所在的文件路径
    if not folder_summary:  # 如果用户未选择任何文件夹，则显示报错，并 return 出该函数
        print('未选择文件夹')
        return
    save_file_path(folder_summary, summary_files)  # 调用配置好的函数将 folder_summary 的子表格文件存储到 summary_files 中
    read_summary_files_data()  # 读取汇总文件夹中的所有学生信息
    # 统计输出读取到的学生数据
    print('总共读取到' + str(len(summary_data)) + '位学生数据')


# 核查汇总表中的学生是否在绩点文件中都能找到，确保班级、姓名、学号信息无误
def check_student_exist():
    global summary_data, gpa_files, success_student
    check_fail_student_id = pd.DataFrame(columns=['学号', '班级', '姓名'])  # 保存学号核对不上的学生数据
    check_fail_student_name = pd.DataFrame(columns=['学号', '班级', '姓名'])  # 保存姓名核对不上的学生数据
    gpa_student_name = pd.DataFrame(columns=['学号', '班级', '姓名'])  # 由于学生姓名核对不上可能会出现两种情况，所以这个时候保存以下绩点文件中的准确数据，方便用户做比对
    fail_student_number = 0  # 保存核对失败的学生数量
    for gpa_file in gpa_files:  # 循环保存好的 gpa_files 字典数据，根据每一项的路径读取该文件
        gpa_data = pd.read_excel(gpa_file, header=0)  # 读取表格中的数据
        file_class = process_student_class(gpa_data['班级'].iloc[0])  # 确认本次循环读取的表格是那个班级的绩点数据
        process_student = summary_data.loc[summary_data['班级'] == file_class]  # 将属于这个班级的学生数据读取出来，单独处理
        # 此处已比对班级数据
        summary_data = summary_data.drop(process_student.index.tolist())  # 将每一次班级匹配上的数据从 summary_data 中删除，最后剩下的数据就是班级有问题的数据
        for index, row in process_student.iterrows():  # 循环这个班级的学生数据
            state = False  # 定义一个变量来判断该学生的学号是否在该班级中找到
            # 内部循环该班级的绩点文件，实现双层循环
            for index2, row2 in gpa_data.iterrows():
                if row['学号'] == row2['学号'] and row['姓名'] != row2['姓名']:  # 当出现学号匹配对但是姓名不对的情况，有可能是学号写错或姓名写错，这时候要将错误信息和绩点中的数据都保存起来，方便做比对
                    check_fail_student_name = pd.concat([check_fail_student_name, pd.DataFrame(row).T], ignore_index=True)
                    gpa_student_name = pd.concat([gpa_student_name, pd.DataFrame(row2[['学号', '班级', '姓名']]).T], ignore_index=True)
                if row['学号'] == row2['学号']:
                    state = True  # 将可以学号查询通过的学生做一个标记，以排查根据学号查找不到的数据
            if not state:
                # 将通过学号未查询到的数据保存起来
                check_fail_student_id = pd.concat([check_fail_student_id, pd.DataFrame(row).T], ignore_index=True)
    fail_student_number = len(check_fail_student_id) + len(check_fail_student_name) + len(summary_data)
    if fail_student_number != 0:
        print('======================有' + str(fail_student_number) + '位学生数据出现问题，请处理==================')
        for index in check_fail_student_name.index:
            print('汇总表数据：', check_fail_student_name.iloc[index]['学号'],
                  check_fail_student_name.iloc[index]['班级'], check_fail_student_name.iloc[index]['姓名'])
            print('绩点表数据：', gpa_student_name.iloc[index]['学号'], gpa_student_name.iloc[index]['班级'],
                  gpa_student_name.iloc[index]['姓名'])
            print('')
        print('================以上为汇总表中姓名出现问题的学生，请检查是否为姓名写错或学号写错========================')
        for index in check_fail_student_id.index:
            print(check_fail_student_id.iloc[index]['学号'], check_fail_student_id.iloc[index]['班级'],
                  check_fail_student_id.iloc[index]['姓名'])
            print('')
        print('================以上为汇总表中学号出现问题的学生，请检查是否为学号写错========================')
        for index in summary_data.index:
            print(summary_data.loc[index]['学号'], summary_data.loc[index]['班级'], summary_data.loc[index]['姓名'])
            print('')
        print('================以上为汇总表中班级出现问题的学生，请检查是否为班级写错========================')
    else:
        print('所有数据准确无误，可以开始核查')


def open_gpa_files():
    folder_gpa = os.path.abspath('../data/2023年冬成绩绩点（以此为准）2023-2024-1学期')  # 和上方的方法一样，在开发过程中写一个固定的路径，方便使用
    # folder_gpa = filedialog.askdirectory()  # 打开文件夹选择器，让用户自主选择绩点文件夹所在的文件路径
    if not folder_gpa:
        print('为选择文件夹')
        return
    save_file_path(folder_gpa, gpa_files)  # 调用配置好的函数将 folder_gpa 的子表格文件存储到 gpa_files 中
    check_student_exist()  # 为确保汇总文件中的学生信息准确无误，这里需要核查汇总表中的学生数据是否在绩点文件中都可以找到


open_summary_files()

open_gpa_files()
