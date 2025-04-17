import streamlit as st
import pandas as pd
import os
import tempfile
from datetime import datetime

# 一時保存先
TEMP_IMAGE_DIR = "./tmp"
CSV_LOG_PATH = "./upload_log.csv"

def dummy_ssh_upload(local_image_path, remote_path="/dummy/path"):
    st.info(f"[SSH送信スキップ] 本来は {local_image_path} を {remote_path} にアップロードします。")

def save_temp_image(uploaded_file):
    os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)
    save_path = os.path.join(TEMP_IMAGE_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

def update_csv_log(image_filename):
    data = {
        "filename": image_filename,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(CSV_LOG_PATH):
        df = pd.read_csv(CSV_LOG_PATH)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])
    df.to_csv(CSV_LOG_PATH, index=False)

st.set_page_config(page_title="カーレジスター", layout="centered")
st.title("竹山")

# カメラ起動をサポートするHTML input（streamlit標準ではできないため裏技）
uploaded_file = st.file_uploader("ナンバープレートを撮影してください。", type=["jpg", "jpeg", "png"])

# カメラ起動に対応したraw HTMLも追加（スマホ対応用）
st.markdown(
    """
    <input type="file" accept="image/*" capture="environment"
           onchange="document.getElementById('fileUploader').dispatchEvent(new Event('change'))"
           style="margin-bottom: 20px;" />
    """,
    unsafe_allow_html=True
)

if uploaded_file:
    with st.spinner("処理中..."):
        temp_path = save_temp_image(uploaded_file)
        dummy_ssh_upload(temp_path)
        update_csv_log(uploaded_file.name)

    # 成功メッセージと仮のナンバー情報
    st.success("お車を登録しました！ ✅")
    st.markdown("### 以下の内容で登録しました：")
    st.markdown("""
    - 地域：依知川
    - クラス：111
    - かな：い
    - 車番：2525
    """)

    # トップに戻るボタン（ページ再読み込み）
    if st.button("トップに戻る"):
        st.experimental_rerun()
