import streamlit as st
from embedding_handler import EmbeddingHandler  # 埋め込み処理クラス
from database import DatabaseHandler           # データベース操作クラス
from config import DB_CONFIG                   # データベース構成
from urllib.parse import urlparse
from gemin import chat_gem
from Web_download import fetch_text_from_url
from pathlib import Path

# データベースとEmbeddingHandlerの初期化
db_handler = DatabaseHandler(DB_CONFIG)
embedding_handler = EmbeddingHandler()


def gemini(url):
    webres = fetch_text_from_url(url)

    prompt = f"""
instruction : 以下のテキストをツールや具体的な手法や手順を主にして要約を出力してください。
text : {webres}
"""
    summary = chat_gem(prompt)
    return {
        "summary": summary,
        "content": webres
    }

# タブ設定
st.set_page_config(layout="wide", page_title="Webページデータベース検索・管理")

# サイドバー
st.sidebar.title("データ管理アプリ")
menu = st.sidebar.radio("メニューを選択", ["検索", "データ追加", "データ確認と編集"])

# 検索タブ
if menu == "検索":
    st.header("ベクトル検索")
    query = st.text_input("検索キーワードを入力してください:")
    top_k = st.number_input("検索結果の上位件数", min_value=1, max_value=50, value=5)
    
    if st.button("検索"):
        if query:
            # クエリをベクトルに変換
            query_vector = embedding_handler.get_embedding(query)
            # データベース検索
            results = db_handler.search_vectors(query_vector, top_k)
            
            if results:
                st.success("検索結果:")
                for idx, result in enumerate(results):
                    st.write(f"**{idx + 1}. URL: {result['url']}**")
                    st.write(f"要約: {result['summary']}")  # 保存された要約を表示
                    # 元のデータを新規タブで開くリンク
                    original_data_url = result['url'].replace("https://", "").replace("http://", "").replace("/", "_") + ".html"
                    data_url = ".webcontent/" + original_data_url
                    st.write(f"保存先： {data_url}")
            else:
                st.warning("該当するデータが見つかりませんでした。")
        else:
            st.error("検索キーワードを入力してください。")

# データ追加タブ
elif menu == "データ追加":
    st.header("Webページデータ追加")
    url = st.text_input("URLを入力してください:")
    if st.button("データを追加"):
        if url:
            data = gemini(url)
            summary = data.get("summary")
            content = data.get("content")

            if summary and content:
                embedding = embedding_handler.get_embedding(summary)
                db_handler.insert_data(url, summary, content, embedding)
                st.success("データを追加しました。")
            else:
                st.error("データの取得に失敗しました。")
        else:
            st.error("URLを入力してください。")

# データ確認と編集タブ
elif menu == "データ確認と編集":
    st.header("データ確認と編集")
    page = st.number_input("確認するページ番号", min_value=1, step=1, value=1)
    data_list = db_handler.get_data_list(page, limit=10)

    if data_list:
        for idx, data in enumerate(data_list):
            st.write(f"**{idx + 1}. {data['url']}**")
            st.write(f"要約: {data['summary']}")

            edit_button = st.button(f"編集する {data['id']}")
            delete_button = st.button(f"削除する {data['id']}")

            if edit_button:
                new_summary = st.text_area("新しい要約を入力:", data['summary'])
                if st.button("保存する"):
                    db_handler.update_data(data['id'], new_summary)
                    st.success("データを更新しました。")
            if delete_button:
                db_handler.delete_data(data['id'])
                st.warning("データを削除しました。")
    else:
        st.info("データが見つかりませんでした。")
