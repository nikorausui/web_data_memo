import os
import requests
from bs4 import BeautifulSoup

def fetch_text_from_url(url, save_directory="./webcontent"):
    """
    指定されたURLからウェブページをダウンロードし、テキストとして返す関数。

    Parameters:
        url (str): ダウンロードするウェブページのURL。

    Returns:
        str: 抽出されたテキスト（失敗時はエラーメッセージ）。
    """
    try:
        # URLからウェブページを取得
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあれば例外をスロー

        # BeautifulSoupを使ってHTMLを解析
        soup = BeautifulSoup(response.text, 'html.parser')

        # ページ内のテキストを抽出
        text = soup.get_text().strip()

        # 保存ディレクトリが存在しない場合は作成
        os.makedirs(save_directory, exist_ok=True)

        # 保存するファイル名（URLに基づいて固有名を生成）
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".html"
        file_path = os.path.join(save_directory, filename)

        # HTMLファイルを保存
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)

        print(f"HTMLが正常に保存されました: {file_path}")

        # 抽出したテキストを返す
        return text

    except requests.exceptions.RequestException as e:
        # HTTPリクエストエラーの処理
        error_msg = f"HTTPエラーが発生しました: {e}"
        print(error_msg)
        return error_msg

    except Exception as e:
        # その他のエラーの処理
        error_msg = f"不明なエラーが発生しました: {e}"
        print(error_msg)
        return error_msg

