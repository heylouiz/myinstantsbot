FROM alpine

RUN apk --update --no-cache add \
    python3 python3-dev build-base libressl-dev libffi-dev

WORKDIR /app

ADD . /app

RUN pip3 install -U pip
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

CMD ["python3", "myinstantsbot.py"]

