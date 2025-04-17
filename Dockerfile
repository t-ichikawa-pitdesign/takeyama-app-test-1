FROM python:3.11-slim

# 必要パッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ作成
WORKDIR /app

# ファイルコピー
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ポート開放
EXPOSE 8501

# Streamlit 実行
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
