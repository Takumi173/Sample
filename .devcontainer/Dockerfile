## python-3.12:base (vscodeからBuild imageで名前とタグを指定して作成)

# Docker imageの指定
FROM python:3.12-bookworm

# __pycache__を作成しない
ENV PYTHONDONTWRITEBYTECODE=1

# rootユーザで実行
USER root

#COPY requirements.txt /root/

# pipを更新してipkernerlとjupyterのインストール
RUN pip install --upgrade pip

#RUN pip install -r /root/requirements.txt
#RUN pip install altair -U
