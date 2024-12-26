import streamlit as st
import pandas as pd
import json
import xml.etree.ElementTree as ET
from st_aggrid import AgGrid, GridOptionsBuilder
import os

# 指定ディレクトリのパス
directory_path = '/workspace/sdtm-adam-pilot-project/updated-pilot-submission-package/900172/m5/datasets/cdiscpilot01/tabulations/sdtm/'

# 指定ディレクトリ内のJSONファイルをリストで取得
json_files = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.json')]

# XMLファイルのパス
xml_path = '/workspace/sdtm-adam-pilot-project/updated-pilot-submission-package/900172/m5/datasets/cdiscpilot01/tabulations/sdtm/define.xml'

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
with open('/workspace/sdtm-adam-pilot-project/updated-pilot-submission-package/900172/m5/datasets/cdiscpilot01/tabulations/sdtm/dm.json', 'r') as file:
    usubjid_source_data = json.load(file)

# USUBJIDのリストを取得
usubjid_list = [row[2] for row in usubjid_source_data['rows']]

# ページの選択
page = st.sidebar.selectbox("Select Page", ["Study Data", "Trial Domains"])

# 各Originごとにチェックボックスを作成
show_vars = {}
for origin in checkbox_order:
    if origin in origin_vars:
        show_vars[origin] = st.sidebar.checkbox(f'Show {origin} variables', value=(origin in ["CRF", "eDT"]))

# USUBJIDの選択（Study Dataページのみ）
if page == "Study Data":
    st.sidebar.markdown('[USUBJID](#usubjid)')
    st.header("USUBJID")
    usubjid = st.selectbox('Select USUBJID', usubjid_list)

# データのフィルタリング関数
def filter_files(page, json_files):
    if page == "Study Data":
        filtered_files = [f for f in json_files if f[:2] not in ["ta", "te", "ts", "ti", "tv", "sv", "se"]]
    else:  # Trial Domains
        filtered_files = [f for f in json_files if f[:2] in ["ta", "te", "ts", "ti", "tv", "sv", "se"]]
    return filtered_files

# フィルタリングされたファイルのリストを取得
files_to_display = filter_files(page, json_files)
# データの表示
for file in files_to_display:
    st.header(file.upper())
    st.sidebar.markdown('[' + file.upper() + '](#' + file + ')')
    df = {}
    labels = {}
    df[file], labels[file] = readJSON(file)

    if page == "Study Data":
        # Study DataページのみUSUBJIDでフィルタリング
        df[file] = df[file][df[file][labels[file][file.upper()+'.USUBJID']] == usubjid]

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

    # AgGridのオプションを設定
    gb = GridOptionsBuilder.from_dataframe(df[file])
    gb.configure_default_column(editable=False, filter=True)
    grid_options = gb.build()

    # AgGridを表示（一意のキーを指定）
    AgGrid(df[file], gridOptions=grid_options, enable_enterprise_modules=True, key=file)
