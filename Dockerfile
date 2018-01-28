FROM python:2.7.12
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y \
    git

RUN apt-get -t jessie-backports install -y "ffmpeg"


RUN cd /tmp \
    && git clone https://github.com/jakul/aggdraw.git \
    && cd aggdraw \
    && /usr/local/bin/python setup.py install


COPY requirements.txt /tmp
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt

RUN mkdir /app
COPY . /app
WORKDIR /app

ENTRYPOINT ["python", "extract_scene.py"]
