FROM python:3.7
RUN apt-get update \
    && apt-get install -qqy --no-install-recommends \
        apt-utils \
        ffmpeg \
        texlive-latex-base \
        texlive-full \
        texlive-fonts-extra \
        sox \
        libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt && rm requirements.txt
ENTRYPOINT ["/bin/bash"]
