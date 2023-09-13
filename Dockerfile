FROM python:3.11.5

WORKDIR /usr/src/bloxlink-image-server

ADD . /usr/src/bloxlink-image-server

RUN pip3 install "poetry==1.6.1"
RUN poetry install

EXPOSE 8001

ENTRYPOINT [ "poetry", "run", "python", "src/main.py" ]