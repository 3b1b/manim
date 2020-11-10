FROM python:3.7-slim

RUN apt-get update -q \
    && apt-get install --no-install-recommends -y \
        ffmpeg \
        gcc \
        git \
        libcairo2-dev \
        libffi-dev \
        pkg-config \
        wget

# setup a minimal texlive installation
COPY ./texlive-profile.txt /tmp/
ENV PATH=/usr/local/texlive/bin/x86_64-linux:$PATH
RUN wget -O /tmp/install-tl-unx.tar.gz http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz && \
    mkdir /tmp/install-tl && \
    tar -xzf /tmp/install-tl-unx.tar.gz -C /tmp/install-tl --strip-components=1 && \
    /tmp/install-tl/install-tl --profile=/tmp/texlive-profile.txt \
    && tlmgr install \
        amsmath babel-english cm-super doublestroke dvisvgm fundus-calligra \
        jknapltx latex-bin microtype ms physics preview ragged2e relsize rsfs \
        setspace standalone tipa wasy wasysym xcolor xkeyval

# clone and build manim
RUN git clone --depth 1 --branch v0.1.0 https://github.com/ManimCommunity/manim.git /opt/manim
WORKDIR /opt/manim
RUN pip install --no-cache .

# ensure ffi bindings are generated correctly
WORKDIR /usr/local/lib/python3.7/site-packages
RUN python cairocffi/ffi_build.py \
    && python pangocffi/ffi_build.py \
    && python pangocairocffi/ffi_build.py

# create working directory for user to mount local directory into
WORKDIR /manim
RUN chmod 666 /manim

CMD [ "/bin/bash" ]
