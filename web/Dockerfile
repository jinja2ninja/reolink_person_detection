FROM ubuntu
COPY requirements.txt /tmp/requirements.txt
RUN apt update && apt install python3-pip -y && python3 -m pip install -r /tmp/requirements.txt --break-system-packages
RUN apt install -y vim
RUN mkdir -p /web/app
COPY ./ /web/app
WORKDIR /web/app
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["python3", "/web/app/main.py"]