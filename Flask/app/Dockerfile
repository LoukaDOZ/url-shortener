FROM debian:11

RUN mkdir /app
COPY ./ /app
WORKDIR /app

RUN apt update && apt install python3-pip -y
RUN pip install -r requirements.txt

EXPOSE 8080
CMD flask --env-file .flaskenv run