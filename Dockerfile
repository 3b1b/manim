FROM python:3.7
RUN apt-get update \
    && apt-get install -qqy --no-install-recommends \
        apt-utils \
        ffmpeg \
        sox \
        libcairo2-dev \
        texlive \
        texlive-latex-extra \
        texlive-fonts-extra \
        texlive-latex-recommended \
        texlive-science \
        texlive-fonts-extra \
        tipa \
    && rm -rf /var/lib/apt/lists/*
COPY . /manim
RUN cd /manim \
    && python setup.py sdist \
    && python -m pip install dist/manimlib*
ENTRYPOINT ["/bin/bash"]
