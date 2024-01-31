#image指定
FROM ubuntu:22.04

# gcc, Xなどをインストールする
RUN apt-get update \
 && apt-get install -y make gcc python3 python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# WINをインストールする
WORKDIR /usr/local/src/
COPY REAL.tar.gz /usr/local/src/
RUN tar xzfv REAL.tar.gz -C /usr/local/src
WORKDIR /usr/local/src/REAL/
RUN mkdir -p /usr/local/src/real/bin
RUN make all
ENV PATH $PATH:/usr/local/src/real/bin

# # python3をインストールする
WORKDIR /usr/local/src/
RUN pip3 install pandas
RUN pip3 install tqdm

WORKDIR /data/REAL