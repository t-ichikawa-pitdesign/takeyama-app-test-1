import streamlit as st
import pandas as pd
import os
import tempfile
from datetime import datetime

# 一時的に保存するローカルディレクトリ
TEMP_IMAGE_DIR = "./tmp"
CSV_LOG_PATH = "./upload_log.csv"

# ダミーSSH送信処理
def dummy_ssh_upload(local_image_path, remote_path="/dummy/path"):
    # ここで実際のSSHアップロード処理を置き換える
    st.info(f"[SSH送信スキップ] 本来は {local_image_path} を {remote_path} にアップロードします。")

# ローカルに画像を保存
def save_temp_image(uploaded_file):
    os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)
    save_path = os.path.join(TEMP_IMAGE_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

# CSVを更新（ローカル）
def update_csv_log(image_filename):
    data = {
        "filename": image_filename,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(CSV_LOG_PATH):
        df = pd.read_csv(CSV_LOG_PATH)
        df = df.append(data, ignore_index=True)
    else:
        df = pd.DataFrame([data])
    df.to_csv(CSV_LOG_PATH, index=False)

# Streamlit UI
st.title("画像アップロード & CSV更新テスト（SSHはダミー）")

uploaded_file = st.file_uploader("画像ファイルを選択してください", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with st.spinner("処理中..."):
        # ① ローカルに一時保存
        temp_path = save_temp_image(uploaded_file)

        # ② SSH送信（ダミー関数）
        dummy_ssh_upload(temp_path)

        # ③ CSVログ更新
        update_csv_log(uploaded_file.name)

    st.success("アップロードとCSV更新が完了しました ✅")
