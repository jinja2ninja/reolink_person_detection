FROM ubuntu:20.04
RUN mkdir /app
WORKDIR /app
RUN apt update && apt install curl \
    vim \
    git \
    gnupg2 \
    libpq-dev -y
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
  tee /etc/apt/sources.list.d/coral-edgetpu.list && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg |  apt-key add - && \
  apt-get update  && apt-get install python3-pycoral -y
RUN apt install python3-pip -y
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt
COPY app/ /app/
ENTRYPOINT [ "python3", "/app/detect.py"]