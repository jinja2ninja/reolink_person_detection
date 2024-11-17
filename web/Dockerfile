FROM ubuntu
COPY requirements.txt /tmp/requirements.txt
RUN apt update && apt install python3-pip -y && python3 -m pip install -r /tmp/requirements.txt --break-system-packages
RUN apt install -y vim
RUN mkdir -p /web/app
COPY ./ /web/app
RUN mv /web/app/run.sh /web/run.sh && chmod +x /web/run.sh
WORKDIR /web
ENTRYPOINT ["bash", "/web/run.sh"]