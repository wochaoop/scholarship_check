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
    # folder_summary = filedialog.askopenfilename()  # 打开文件选择器，让用户自主选择各班汇总文件所在的文件路径
    if not folder_summary:  # 如果用户未选择任何文件夹，则显示报错，并 return 出该函数
        print('为选择文件')
        return
    save_file_path(folder_summary, summary_files)
    read_summary_files_data()
    # 统计输出读取到的学生数据
    print('总共读取到' + str(len(summary_data)) + '位学生数据')


open_summary_files()