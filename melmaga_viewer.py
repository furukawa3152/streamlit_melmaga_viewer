import streamlit as st
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定。
# デプロイ用
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

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

    # タブの作成
    tabs = st.tabs(["PC", "mobile", "検索"])

    # タブ1: Radioボタン形式
    with tabs[0]:
        unique_dates = df["ymd"].unique()
        selected_date = st.selectbox("日付を選択してください", unique_dates, key="date_select_tab1")

        # 選択した日付に基づいてフィルタリング
        filtered_df = df[df["ymd"] == selected_date]
        if filtered_df.empty:
            st.write("選択した日付には記事がありません。")
        else:
            selected_title = st.sidebar.radio("title", filtered_df["title"], key="title_radio")
            if selected_title:
                st.subheader(selected_title)
                selected_article = filtered_df[filtered_df["title"] == selected_title]["value"].values[0]
                st.write(selected_article)

    # タブ2: Expander形式
    with tabs[1]:
        unique_dates = df["ymd"].unique()
        selected_date = st.selectbox("日付を選択してください", unique_dates, key="date_select_tab2")

        # 選択した日付に基づいてフィルタリング
        filtered_df = df[df["ymd"] == selected_date]
        if filtered_df.empty:
            st.write("選択した日付には記事がありません。")
        else:
            for index, row in filtered_df.iterrows():
                with st.expander(row["title"]):
                    st.write(row["value"])

    # タブ3: 検索機能（全データ対象）
    with tabs[2]:
        search_query = st.text_input("検索キーワードを入力してください", key="search_input")
        if search_query:
            # `value`カラムにキーワードが含まれている行を全データから抽出
            search_results = df[df["value"].str.contains(search_query, na=False)]
            if search_results.empty:
                st.write("検索結果が見つかりませんでした。")
            else:
                for index, row in search_results.iterrows():
                    expander_title = f"{row['ymd']} - {row['title']}"  # ymdとtitleを結合して表示
                    with st.expander(expander_title):
                        st.write(row["value"])

# Streamlitアプリを実行
if __name__ == "__main__":
    app()
