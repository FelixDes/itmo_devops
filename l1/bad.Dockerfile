FROM python:latest

RUN apt-get update
RUN apt-get install -y vim curl gcc build-essential

ADD . /app
WORKDIR /app

RUN pip install fastapi uvicorn

ENV DATA_DIR=/data
EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port 8000
