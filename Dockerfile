FROM ubuntu:latest

RUN apt-get update -y

RUN apt-get install python3-pip python-dev build-essential -y

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD [ "run.py" ]

EXPOSE 5000