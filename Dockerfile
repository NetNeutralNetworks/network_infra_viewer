ARG PYTHON_VERSION=3.10.6

FROM python:${PYTHON_VERSION}-slim as base

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    apt install -y python3-dev cmake make gcc g++ libssl-dev

RUN mkdir /var/appbuilder
WORKDIR /var/appbuilder

RUN pip install --upgrade pip

COPY ./requirements.txt /var/appbuilder/requirements.txt

RUN pip install -r requirements.txt

COPY . /var/appbuilder/

#EXPOSE 5000

CMD [ "python", "run.py" ]
