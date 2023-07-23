from ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3.10-venv

COPY ./requirements.txt /requirements.txt

RUN python3 -m venv /server/venv && \
    . /server/venv/bin/activate && \
    python3 -m pip install -r /requirements.txt

COPY ./main.py /server/main.py
COPY ./start.sh /server/start.sh

RUN chmod +x /server/start.sh

VOLUME "/server/data"
ENTRYPOINT ["sh"]
WORKDIR "/server"
CMD ["/server/start.sh"]
