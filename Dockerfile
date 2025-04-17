FROM ubuntu:20.04

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-ipafont \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを作成
WORKDIR /app

# エントリポイントを設定
ENTRYPOINT ["libreoffice", "--headless", "--convert-to", "pdf"]