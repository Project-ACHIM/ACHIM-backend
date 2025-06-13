FROM python:3.11-slim
 
# Git・SSH・PostgreSQLクライアントをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    postgresql-client \
&& apt-get clean && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app

# requirements.txt をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリコードをコピー（backend配下）
COPY ./backend .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
