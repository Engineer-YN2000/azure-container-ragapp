# Python 3.11 の公式イメージをベースにする
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# 作業ディレクトリを設定
WORKDIR /home/site/wwwroot

# 依存関係ファイルをコピー
COPY src/indexer/requirements.txt ./

# 依存関係をインストール
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# アプリケーションの全ファイルをコピー
COPY src/indexer ./

# Azure Functions の起動コマンドはベースイメージで定義済み
