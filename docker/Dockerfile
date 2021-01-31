FROM python:3.8-slim

RUN apt-get update -qq \
    && apt-get install --no-install-recommends -y \
        ffmpeg \
        gcc \
        libcairo2-dev \
        libffi-dev \
        pkg-config \
        wget

# setup a minimal texlive installation
COPY docker/texlive-profile.txt /tmp/
ENV PATH=/usr/local/texlive/bin/x86_64-linux:$PATH
RUN wget -O /tmp/install-tl-unx.tar.gz http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz && \
    mkdir /tmp/install-tl && \
    tar -xzf /tmp/install-tl-unx.tar.gz -C /tmp/install-tl --strip-components=1 && \
    /tmp/install-tl/install-tl --profile=/tmp/texlive-profile.txt \
    && tlmgr install \
        amsmath babel-english cm-super doublestroke dvisvgm everysel fundus-calligra \
        jknapltx latex-bin microtype ms physics preview ragged2e relsize rsfs \
        setspace standalone tipa wasy wasysym xcolor xkeyval

# clone and build manim
COPY . /opt/manim
WORKDIR /opt/manim
RUN pip install --no-cache .[jupyterlab,webgl_renderer]
# required due to current incompatibility from latest jedi version
RUN pip install jedi==0.17.2

ARG NB_USER=manimuser
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /manim

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# create working directory for user to mount local directory into
WORKDIR ${HOME}
USER root
RUN chown -R ${NB_USER}:${NB_USER} ${HOME}
RUN chmod 777 ${HOME}
USER ${NB_USER}

CMD [ "/bin/bash" ]
