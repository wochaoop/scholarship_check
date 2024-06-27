import pandas as pd
from sqlalchemy import create_engine

# 读取Excel文件
file_path = r'D:\Users\Xiwangly\Documents\固定资产导出报表20240531194957.xls'
df = pd.read_excel(file_path, header=1)

# 数据库连接配置
user = 'root'
password = 'mysql_7snJrJ'
host = '59.53.89.9'
port = '10001'
database = 'aihpt'

# 打印Excel文件的列名
# print("Excel文件的列名：")
# print(df.columns)
# print("列数：", len(df.columns))

# 创建数据库引擎
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

# 将数据写入数据库表
table_name = 'hrp_card'

# 列名映射
columns_mapping = {
    '资产编号': 'card_number',
    '资产名称': 'card_name',
    '单位名称': 'dept_name',
    '一级分类': 'class_name',
    '资产分类': 'class_name2',
    '财政分类': 'class_name3',
    '型号规格': 'card_spec',
    '计量单位': 'unit_name',
    '使用科室': 'dept_name2',
    '使用状态': 'use_status',
    '资产价值': 'price',
    '累计折旧': 'depreciation',
    '账面净值': 'net_value',
    '月折旧额': 'month_depreciation',
    '折旧状态': 'depreciation_status',
    '折旧年限': 'depreciation_life',
    '购置日期': 'purchase_date',
    '入账日期': 'account_date',
    '使用日期': 'use_date',
    '报废时间': 'scrap_date',
    '供应商': 'vender_name',
    '厂家名称': 'vender_name2',
    '备注': 'remark',
    '卡片编号': 'card_number2',
    '保管人': 'keeper',
    '累计折旧月数': 'month_depreciation_num',
    '财政专用': 'finance_special',
    '财政专用_月折旧额': 'finance_special_month_depreciation',
    '财政专用_累计折旧': 'finance_special_depreciation',
    '财政专用_净值': 'finance_special_net_value',
    '非同级财政': 'finance_special2',
    '非同级财政_月折旧额': 'finance_special2_month_depreciation',
    '非同级财政_净值': 'finance_special2_net_value',
    '非同级财政_累计折旧': 'finance_special2_depreciation',
    '自有资金': 'finance_special3',
    '自有资金_月折旧额': 'finance_special3_month_depreciation',
    '自有资金_累计折旧': 'finance_special3_depreciation',
    '自有资金_净值': 'finance_special3_net_value',
    '科研基金': 'finance_special4',
    '科研基金_月折旧额': 'finance_special4_month_depreciation',
    '科研基金_累计折旧': 'finance_special4_depreciation',
    '科研基金_净值': 'finance_special4_net_value',
    '财政基本': 'finance_special5',
    '财政基本_月折旧额': 'finance_special5_month_depreciation',
    '财政基本_净值': 'finance_special5_net_value',
    '预算号': 'budget_number',
    '合同编码': 'contract_number',
    '采购员': 'buyer',
    '采购明细guid': 'purchase_detail_guid',
    '旧资产编号': 'old_card_number',
    '存放地点': 'storage_place',
    '设备真实状态': 'device_real_status',
    '到期日期': 'expire_date',
    '出厂编号': 'factory_number',
    '资金来源': 'fund_source',
    '仓库': 'warehouse',
    '供货人': 'supplier',
    '供货人联系方式': 'supplier_contact',
    '报修联系人': 'repair_contact',
    '报修联系电话': 'repair_contact_phone',
    '设备论证号': 'device_proof_number',
    '财政编码': 'finance_code',
    '招标日期': 'tender_date',
    '合同签订日期': 'contract_sign_date',
    '管理科室': 'manage_dept',
    '发票号': 'invoice_number',
    '经过部门调拨': 'pass_dept_transfer',
    '发票重复': 'invoice_repeat',
    '数量': 'number',
    '金额': 'amount',
    '已使用年限': 'used_years',
    '生产日期': 'produce_date',
    '序列号': 'serial_number',
    '管理人': 'manager',
    '原单位': 'old_dept',
    '档案号': 'file_number',
    '开户行': 'bank_name',
    '银行账号': 'bank_account',
    '杀毒软件': 'antivirus_software',
    '办公软件': 'office_software',
    '使用人': 'user_name',
    '取得方式': 'acquire_way',
    '来源': 'source',
    '有效期(年)': 'valid_period',
    '入库自有资金科目名称': 'own_fund_subject_name',
    '自有资金折旧科目名称': 'own_fund_depreciation_subject_name',
    '品名': 'product_name',
    '最新调拨日期': 'latest_transfer_date',
    '使用年限': 'use_years'
}

# 重命名列
df.rename(columns=columns_mapping, inplace=True)

# 删除包含“合计”的最后一行
df = df[~df['card_number'].astype(str).str.contains('合计')]

# 将所有NaN值转换为空字符串
df = df.fillna('')

# 将数据类型转换为字符串
df = df.astype(str)

# 将数据写入数据库表
df.to_sql(table_name, engine, if_exists='append', index=False)

print("数据导入成功！")
