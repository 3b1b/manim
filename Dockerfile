FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -qqy
RUN apt-get install -qqy --no-install-recommends apt-utils

WORKDIR /root
RUN apt-get install -qqy build-essential libsqlite3-dev sqlite3 bzip2 \
                         libbz2-dev zlib1g-dev libssl-dev openssl libgdbm-dev \
                         libgdbm-compat-dev liblzma-dev libreadline-dev \
                         libncursesw5-dev libffi-dev uuid-dev
RUN apt-get install -qqy wget
RUN wget -q https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
RUN tar -xf Python-3.7.0.tgz
WORKDIR Python-3.7.0
RUN ./configure > /dev/null && make -s && make -s install
RUN python3 -m pip install --upgrade pip
RUN apt-get install -qqy libcairo2-dev libjpeg-dev libgif-dev
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
RUN rm requirements.txt
WORKDIR /root
RUN rm -rf Python-3.7.0*

RUN apt-get install -qqy ffmpeg

ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -qqy apt-transport-https
RUN apt-get install -qqy texlive-latex-base 
RUN apt-get install -qqy texlive-full
RUN apt-get install -qqy texlive-fonts-extra
RUN apt-get install -qqy sox
RUN apt-get install -qqy git

ENV DEBIAN_FRONTEND teletype
ENTRYPOINT ["/bin/bash"]
