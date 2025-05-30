FROM python:3.11-slim
 
# Git と OpenSSH クライアントをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    openssh-client \
&& apt-get clean && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app
 
# requirements.txt をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# アプリコードをコピー（backend配下）
COPY ./backend .
 
# ホットリロード対応（開発用）
ENV PYTHONUNBUFFERED=1
 
# サーバー起動（app.main:app に合わせる）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]