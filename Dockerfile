FROM python:3.7.4-stretch

ADD . /interactive-viewer
WORKDIR /interactive-viewer
RUN apt update \
    && apt install -y \
    openexr libopenexr-dev zlib1g-dev \
    && apt clean
RUN pip install --upgrade pip 
RUN python3 -m pip install --user -r tools/requirements.txt
