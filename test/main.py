import os.path

import pandas as pd

summary_files = []  # 存储各班汇总表文件夹中的表格路径
summary_data = pd.DataFrame(columns=['学号', '班级', '姓名'])  # 存储从各班汇总表中读取的数据，避免保存学生身份证号等敏感信息


def open_summary_files():
    folder_summary = os.path.abspath('../data/2024年春校内奖学金/各班汇总表')
    if not folder_summary:
        print('为选择文件')
        return

