import streamlit as st
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定。
#デプロイ用
credentials = Credentials.from_service_account_info( st.secrets["gcp_service_account"], scopes=[ "https://www.googleapis.com/auth/spreadsheets", ],)

gc = gspread.authorize(credentials)

# スプレッドシートIDを変数に格納する。
SPREADSHEET_KEY = st.secrets["SPREADSHEET_KEY"]
# スプレッドシート（ブック）を開く
workbook = gc.open_by_key(SPREADSHEET_KEY)

# シートの一覧を取得する。（リスト形式）
worksheets = workbook.worksheets()
# シートを開く
sheet = workbook.worksheet('シート1')
data = sheet.get_all_values()
# Pandas DataFrameに変換
df = pd.DataFrame(data)
# 一行目をカラム名にする
df.columns = df.iloc[0]
# 一行目を削除する
df = df[1:]
st.title('melmaga_viewer')
st.dataframe(df,hide_index=True,)