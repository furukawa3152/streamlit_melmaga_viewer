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



# パスワード認証
def authenticate(password):
    return password == "ocomoji0616"


# UIの作成
def app():
    st.title('melmaga_viewer')
    # サイドバーにパスワード入力を配置
    password = st.sidebar.text_input("パスワードを入力してください", type="password")

    if not authenticate(password):
        st.sidebar.error("パスワードが間違っています")
        return

    st.sidebar.success("パスワードが認証されました！")

    # 日付のドロップダウン
    unique_dates = df["ymd"].unique()
    selected_date = st.selectbox("日付を選択してください", unique_dates)

    # 選択した日付に基づいて見出しを取得
    filtered_df = df[df["ymd"] == selected_date]

    if filtered_df.empty:
        st.write("選択した日付には記事がありません。")
        return

    # タブの作成
    tabs = st.tabs(["PC", "mobile"])

    # タブ1: Radioボタン形式
    with tabs[0]:
        # st.subheader("Radioボタン形式の表示")
        # 見出しをサイドバーに一覧表示（radioボタン形式）
        selected_title = st.sidebar.radio("title", filtered_df["title"])

        # 選択した見出しに基づいて本文を表示
        if selected_title:
            st.subheader(selected_title)
            selected_article = filtered_df[filtered_df["title"] == selected_title]["value"].values[0]
            st.write(selected_article)

    # タブ2: Expander形式
    with tabs[1]:
        # st.subheader("Expander形式の表示")
        # 各見出しごとにExpanderを作成し、本文を表示
        for index, row in filtered_df.iterrows():
            with st.expander(row["title"]):
                st.write(row["value"])



# Streamlitアプリを実行
if __name__ == "__main__":
    app()