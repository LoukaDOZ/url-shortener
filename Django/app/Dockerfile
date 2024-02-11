FROM debian:11

RUN mkdir /app
COPY ./ /app
WORKDIR /app

RUN apt update && apt install python3-pip -y
RUN pip install -r requirements.txt

RUN python3 manage.py check --deploy

EXPOSE 8080
CMD python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8080