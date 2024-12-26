########## ここから初期設定 ##########
# devcontainerでshファイルを読み込ませてスクリプトを起動時に実行しているため起動すれば立ち上がるはず。
# ダメな場合はstreamlit run main.pyで起動する
# 上記で起動しない場合はポートを手動で追加する

########## ここから初期設定 ##########

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import glob

print('Hello')