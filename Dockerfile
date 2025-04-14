FROM alpine

RUN apk --update --no-cache add \
    python3 python3-dev build-base libressl-dev libffi-dev py3-pip libxml2-dev libxslt-dev py3-setuptools py3-wheel

WORKDIR /app

ADD . /app

RUN pip3 install --trusted-host pypi.python.org --break-system-packages -r requirements.txt

CMD ["python3", "myinstantsbot.py"]
