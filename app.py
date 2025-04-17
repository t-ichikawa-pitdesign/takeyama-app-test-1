import streamlit as st
import pandas as pd
import os
import socket
from datetime import datetime
from PIL import Image
import pytesseract
import re

# 保存先パス
TEMP_IMAGE_DIR = "./tmp"
CSV_LOG_PATH = "./upload_log.csv"

# USE_OCR = os.environ.get("STREAMLIT_CLOUD", "false").lower() != "true"
USE_OCR = False

# セッション初期化
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "editing" not in st.session_state:
    st.session_state.editing = False
if "plate_info" not in st.session_state:
    st.session_state.plate_info = {}

# OCRでナンバー抽出
def extract_plate_info(uploaded_file):
    image = Image.open(uploaded_file).convert("L")
    text = pytesseract.image_to_string(image, lang="jpn")

    match = re.search(r"(?P<region>[\u4E00-\u9FFF]+)[\s　]*(?P<class>\d{3})[\s　]*(?P<kana>[ぁ-んア-ン])[\s　\-]*(?P<number>\d{2,4})", text)
    if match:
        return {
            "地域": match.group("region"),
            "クラス": match.group("class"),
            "かな": match.group("kana"),
            "車番": match.group("number")
        }
    return {
        "地域": "不明",
        "クラス": "",
        "かな": "",
        "車番": ""
    }

def dummy_ssh_upload(local_image_path, remote_path="/dummy/path"):
    st.info(f"[SSH送信スキップ] 本来は {local_image_path} を {remote_path} にアップロードします。")

def save_temp_image(uploaded_file):
    os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)
    save_path = os.path.join(TEMP_IMAGE_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

def update_csv_log(image_filename, plate_info):
    data = {
        "filename": image_filename,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **plate_info
    }
    if os.path.exists(CSV_LOG_PATH):
        df = pd.read_csv(CSV_LOG_PATH)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])
    df.to_csv(CSV_LOG_PATH, index=False)

# UI
st.set_page_config(page_title="カーレジスター", layout="centered")
st.title("竹山")

# ステップ1：アップロード
if not st.session_state.uploaded_file:
    uploaded_file = st.file_uploader("ナンバープレートを撮影してください。", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        if USE_OCR:
            st.session_state.plate_info = extract_plate_info(uploaded_file)
        else:
            st.session_state.plate_info = {
                "地域": "依知川",
                "クラス": "111",
                "かな": "い",
                "車番": "2525"
            }
        st.rerun()

# ステップ2：確認 or 修正
elif not st.session_state.confirmed:

    st.image(st.session_state.uploaded_file, caption="アップロードされた画像", use_container_width=True)

    if not st.session_state.editing:
        st.markdown("### このナンバーで間違いありませんか？")
        plate = st.session_state.plate_info
        st.markdown(f"""
        - 地域：{plate['地域']}
        - クラス：{plate['クラス']}
        - かな：{plate['かな']}
        - 車番：{plate['車番']}
        """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("登録する"):
                st.session_state.confirmed = True
                st.rerun()
        with col2:
            if st.button("修正する"):
                st.session_state.editing = True
                st.rerun()

    else:
        st.markdown("### ナンバー情報を修正してください")
        plate = st.session_state.plate_info
        plate["地域"] = st.text_input("地域", plate["地域"])
        plate["クラス"] = st.text_input("クラス", plate["クラス"])
        plate["かな"] = st.text_input("かな", plate["かな"])
        plate["車番"] = st.text_input("車番", plate["車番"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("登録する（修正完了）"):
                st.session_state.confirmed = True
                st.session_state.editing = False
                st.rerun()
        with col2:
            if st.button("アップロードからやり直す"):
                for key in ["uploaded_file", "confirmed", "editing", "plate_info"]:
                    st.session_state.pop(key, None)
                st.rerun()

# ステップ3：登録完了
else:
    with st.spinner("登録中..."):
        temp_path = save_temp_image(st.session_state.uploaded_file)
        dummy_ssh_upload(temp_path)
        update_csv_log(st.session_state.uploaded_file.name, st.session_state.plate_info)

    st.success("お車を登録しました！ ✅")
    plate = st.session_state.plate_info
    st.markdown("### 以下の内容で登録しました：")
    st.markdown(f"""
    - 地域：{plate['地域']}
    - クラス：{plate['クラス']}
    - かな：{plate['かな']}
    - 車番：{plate['車番']}
    """)
    st.image(st.session_state.uploaded_file, caption="登録された画像", use_container_width=True)

    if st.button("トップに戻る"):
        for key in ["uploaded_file", "confirmed", "editing", "plate_info"]:
            st.session_state.pop(key, None)
        st.rerun()
