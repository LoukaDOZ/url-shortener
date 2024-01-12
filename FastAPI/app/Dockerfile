FROM debian:11

RUN apt update && apt install python3-pip -y
RUN pip install fastapi
RUN pip install jinja2
RUN pip install psycopg2-binary
RUN pip install passlib
RUN pip install python-multipart
RUN pip install "uvicorn[standard]"

RUN mkdir /app
COPY ./ /app
WORKDIR /app

EXPOSE 8080
CMD uvicorn main:app --host 0.0.0.0 --port 8080