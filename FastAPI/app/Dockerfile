FROM debian:11

RUN mkdir /app
WORKDIR /app

RUN apt update && apt install python3-pip -y

COPY ./ /app
RUN pip install -r requirements.txt

EXPOSE 8080
CMD uvicorn main:app --host 0.0.0.0 --port 8080