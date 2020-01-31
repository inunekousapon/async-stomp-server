FROM python:3.7.6-slim-buster

ENV LANG ja_JP.UTF-8
ENV LC_CTYPE ja_JP.UTF-8

# gitの導入でLOCALEを聞かれるので、それを回避する
ENV DEBIAN_FRONTEND=noninteractive

# aptの先を日本にする
RUN sed -i.bak -e "s%http://archive.ubuntu.com/ubuntu/%http://ftp.iij.ad.jp/pub/linux/ubuntu/archive/%g" /etc/apt/sources.list

# セットアップのための標準ライブラリを導入
RUN set -x \
    && apt-get -qq -y update \
    && apt-get -qq -y upgrade \
    && apt-get install -y --no-install-recommends curl ca-certificates apt-transport-https gnupg ssh g++ git \
    && curl -O -fsSL https://packages.microsoft.com/keys/microsoft.asc \ 
    && apt-key add microsoft.asc \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y --no-install-recommends unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./app /app/

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]