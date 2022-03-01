FROM python:3.9.10-buster

ENV TESTHOME=/home/app
RUN set -eux; \
    apt update; \
    apt install -y sqlite3;

##################################################################

COPY ./ $TESTHOME/app

WORKDIR $TESTHOME/app

RUN pip install -U poetry;

ENV PATH="${PATH}:/root/.poetry/bin"

RUN poetry config virtualenvs.create false;

RUN set -eux; \
    poetry install;


RUN set -eux; \
    python3 manage.py makemigrations; \
    python3 manage.py migrate;

# Port set as variable and never declared because of Heroku's dinamic port assignment.
EXPOSE $PORT
CMD python3 manage.py runserver 0.0.0.0:$PORT