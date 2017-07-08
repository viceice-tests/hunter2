FROM python:3.6.1

RUN apt-get update

RUN apt-get -y install \
    lua5.2 \
    postgresql-client 

COPY requirements/frozen.txt /usr/src/app/requirements.txt
WORKDIR /usr

RUN apt-get -y install \
    gcc \
    lua5.2-dev \
    musl-dev \
    postgresql-server-dev-9.4 \
 && pip install -r /usr/src/app/requirements.txt --no-deps 

WORKDIR /usr/src/app
COPY . .

RUN addgroup --gid 500 --system django \
 && adduser --system --shell /sbin/nologin --gid 500 --system --uid 500 django \
 && install -d -g django -o django /config /static /uploads/events /uploads/puzzles
USER django

VOLUME ["/config", "/static", "/uploads/events", "/uploads/puzzles"]

EXPOSE 3031
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]
