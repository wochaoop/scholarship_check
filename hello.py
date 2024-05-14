import re
import warnings

import numpy as np
import pandas as pd
import os
import os.path
import collections

warnings.filterwarnings('ignore', category=UserWarning)

fm = pd.read_excel('test.xlsx', header=1)
studentId = fm['学号']


def query(studentId, df):
    global team
    need = df[df['学号'].astype(str).isin(studentId)]
    tips = 0

    for index, rows in need.iterrows():
        name = rows['姓名']
        studentId = rows['学号']
        team = rows['班级']
        for column in need.columns:
            match = re.search(r'\[(\d+)]$', column)
            if match:
                if rows[column] in ['优秀', '良好']:
                    rows[column] = 100
                if rows[column] in ['及格']:
                    rows[column] = 60
                if not pd.isna(rows[column]):
                    if rows[column] < 70:
                        print(name, studentId, team)
                        print(column, rows[column])
                        tips = 1
    if tips == 0:
        print(team, '全部通过')


fileList = os.listdir('process')

for file in fileList:
    if file.endswith('.xlsx'):
        df = pd.read_excel('process/' + file)
        query(studentId, df)
    else:
        fileList2 = os.listdir('process/{}'.format(file))
        for file2 in fileList2:
            if file2.endswith('.xlsx'):
                df = pd.read_excel('process/{}/{}'.format(file, file2))
                query(studentId, df)
