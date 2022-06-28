ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION}-slim as base

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git



RUN mkdir /var/appbuilder
WORKDIR /var/appbuilder

RUN git clone -b 'v4.1.2' https://github.com/dpgaspar/Flask-AppBuilder.git .
RUN pip install -e .

COPY . /var/appbuilder/

EXPOSE 5000

CMD [ "python", "run.py" ]