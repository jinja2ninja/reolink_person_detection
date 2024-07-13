FROM ubuntu
COPY requirements.txt /tmp/requirements.txt
RUN apt update && apt install python3-pip  python3-venv vim -y
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install -r /tmp/requirements.txt
RUN mkdir -p /web/app
COPY ./ /web/app
WORKDIR /web/app
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["python3", "/web/app/main.py"]