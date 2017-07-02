FROM python:3.6-alpine

RUN apk add --no-cache \
    lua5.2 \
    postgresql-client \
    postgresql-libs

COPY requirements/frozen.txt /usr/src/app/requirements.txt
WORKDIR /usr

RUN apk add --no-cache -t builddeps \
    gcc \
    linux-headers \
    lua5.2-dev \
    musl-dev \
    postgresql-dev \
 && pip install -r /usr/src/app/requirements.txt --no-deps \
 && apk del --no-cache builddeps

WORKDIR /usr/src/app
COPY . .

RUN addgroup -g 500 -S django \
 && adduser -s /sbin/nologin -G django -S -D -H -u 500 django \
 && install -d -g django -o django /config /static /uploads/events /uploads/puzzles
USER django

VOLUME ["/config", "/static", "/uploads/events", "/uploads/puzzles"]

EXPOSE 3031
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]
