FROM python:3.7
RUN apt-get update \
    && apt-get install -qqy --no-install-recommends \
        apt-utils \
        ffmpeg \
        texlive-full \
        sox \
        libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*
COPY . /manim
RUN cd /manim \
    && python setup.py sdist \
    && python -m pip install dist/manimlib*
ENTRYPOINT ["/bin/bash"]
