FROM python:3.6.4-alpine3.7

RUN apk add --no-cache \
    lua5.2 \
    postgresql-client \
    postgresql-libs \
    imlib2

ARG REQUIREMENTS_VERSION=production
COPY requirements/${REQUIREMENTS_VERSION}.frozen.txt /usr/src/app/requirements.txt
COPY hunts/runtimes/lua/luarocks/config.lua /etc/luarocks/config-5.2.lua

RUN apk add --no-cache -t builddeps \
    curl \
    gcc \
    git \
    imlib2-dev \
    linux-headers \
    lua5.2-dev \
    luarocks5.2 \
    musl-dev \
    postgresql-dev \
 && pip install -r /usr/src/app/requirements.txt --no-deps --no-binary lupa \
 && luarocks-5.2 install lua-cjson \
 && luarocks-5.2 install lua-imlib2 \
 && apk del builddeps

WORKDIR /usr/src/app
COPY . .

RUN addgroup -g 500 -S django \
 && adduser -h /usr/src/app -s /sbin/nologin -G django -S -u 500 django \
 && install -d -g django -o django /config /static /uploads/events /uploads/puzzles
USER django

VOLUME ["/config", "/static", "/uploads/events", "/uploads/puzzles"]

EXPOSE 3031
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]
