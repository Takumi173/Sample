import streamlit as st
import pandas as pd
import json
import xml.etree.ElementTree as ET
from st_aggrid import AgGrid, GridOptionsBuilder
import os

# 指定ディレクトリのパス
directory_path = 'DatasetJSON/'

# 指定ディレクトリ内のJSONファイルをリストで取得
json_files = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.json')]

# XMLファイルのパス
xml_path = 'DatasetJSON/define.xml'

# XMLファイルの読み込み
tree = ET.parse(xml_path)
root = tree.getroot()

# 各Originごとに変数を取得
origin_vars = {}
for itemdef in root.findall('.//{http://www.cdisc.org/ns/odm/v1.2}ItemDef'):
    origin = itemdef.get('Origin', 'Other')
    # originがCRFで始まる場合、originをCRFに設定
    if origin.startswith('CRF'):
        origin = 'CRF'
    if origin not in origin_vars:
        origin_vars[origin] = []
    origin_vars[origin].append((itemdef.get('OID'), itemdef.get('Name')))

# チェックボックスの並び順
checkbox_order = ["CRF", "eDT", "Assigned", "Derived", "Protocol"]

# テーブルの幅を設定するCSS
table_style = """
<style>
    .block-container {
        width: 95%;
        max-width: 95%;
        padding-left: 0;
        padding-right: 0;
        margin-left: auto;
        margin-right: auto;
    }
</style>
"""

# CSSスタイルを適用
st.markdown(table_style, unsafe_allow_html=True)

def readJSON(domain):
    # JSONファイルの読み込み
    with open(directory_path + domain + ".json", 'r') as file:
        data = json.load(file)

    # 列名からラベルへのマッピングを作成
    column_labels = {col['itemOID']: f"{col['name']} ({col['label']})" for col in data['columns']}

    # データフレームの作成
    columns = [col['itemOID'] for col in data['columns']]
    df = pd.DataFrame(data['rows'], columns=columns)

    # 列名を「変数名 (ラベル)」の形式に変更
    df = df.rename(columns=column_labels)
    return df, column_labels

# USUBJIDを取得するJSONファイルの読み込み
with open(directory_path+'dm.json', 'r') as file:
    usubjid_source_data = json.load(file)

# USUBJIDのリストを取得
usubjid_list = [row[2] for row in usubjid_source_data['rows']]


# 各Originごとにチェックボックスを作成
show_vars = {}
for origin in checkbox_order:
    if origin in origin_vars:
        show_vars[origin] = st.sidebar.checkbox(f'Show {origin} variables', value=True)

# STUDYIDを読み込まないオプションのチェックボックス
show_studyid = st.sidebar.checkbox('Show STUDYID', value=True)

# フィルタリングされたファイルのリストを取得
files_to_display = json_files

# 優先順序のリスト
priority_order_0 = ['dm', 'mh', 'sc', 'ds', 'ex']
priority_order_1 = ['vs', 'lb', ]
priority_order_2 = ['ae', 'cm', ]
priority_order_9 = ["sv", "se", "ta", "te", "ts", "ti", "tv",]

# カスタムキーを定義
def custom_sort_key(item):
    if item in priority_order_0:
        return (0, priority_order_0.index(item))
    if item in priority_order_1:
        return (1, priority_order_1.index(item))
    if item in priority_order_2:
        return (3, priority_order_2.index(item))
    if item in priority_order_9:
        return (9, priority_order_9.index(item))
    elif item.startswith('supp'):
        return (4, item)
    elif item.startswith('relrec'):
        return (5, item)
    else:
        return (2, item)

# 並べ替え
files_to_display = sorted(files_to_display, key=custom_sort_key)


# データの表示
for file in files_to_display:
    st.header(file.upper())
    st.sidebar.markdown('[' + file.upper() + '](#' + file + ')')
    df = {}
    labels = {}
    df[file], labels[file] = readJSON(file)

    # チェックボックスに基づいて変数をフィルタリング
    columns_to_show = []
    for origin, show in show_vars.items():
        if show:
            for oid, name in origin_vars[origin]:
                file_name, var_name = oid.split('.')[0], oid.split('.')[1]
                if file == file_name.lower() and oid in labels[file]:
                    columns_to_show.append(labels[file][oid])

    # フィルタリングされた列だけを表示
    df[file] = df[file][columns_to_show]

    # STUDYIDを除外する場合、列を削除
    if show_studyid == False and 'STUDYID (Study Identifier)' in df[file].columns:
        df[file] = df[file].drop(columns=['STUDYID (Study Identifier)'])

    # AgGridのオプションを設定
    gb = GridOptionsBuilder.from_dataframe(df[file])
    gb.configure_default_column(editable=False, filter=True)
    grid_options = gb.build()

    # AgGridを表示（一意のキーを指定）
    AgGrid(df[file], gridOptions=grid_options, enable_enterprise_modules=True, key=file)
