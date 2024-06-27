from sqlalchemy import create_engine, MetaData, Table
import pandas as pd
from sqlalchemy.orm import collections

# 创建数据库引擎
user = 'root'
password = 'mysql_7snJrJ'
host = '59.53.89.9'
port = '10001'
database = 'aihpt'
table_name = 'hrp_card'
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

# 反射表结构
metadata = MetaData()
table = Table(table_name, metadata, autoload_with=engine)

# 创建列名映射
assert isinstance(table.columns, collections.Iterable)
columns_mapping = {column.comment: column.name for column in table.columns}

# 读取Excel文件
file_path = r'D:\Users\Xiwangly\Documents\固定资产导出报表20240531194957.xls'
df = pd.read_excel(file_path, header=1)

# 重命名列
df.rename(columns=columns_mapping, inplace=True)

# 删除包含“合计”的最后一行
df = df[~df['card_number'].astype(str).str.contains('合计')]

# 将所有NaN值转换为空字符串
df = df.fillna('')

# 将数据类型转换为字符串
df = df.astype(str)

# 将数据写入数据库表
df.to_sql(table_name, con=engine, if_exists='replace', index=False)

print("数据导入成功！")
