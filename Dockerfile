FROM python:3.6.4-alpine3.7

ARG PIPENV_PARAMS=
COPY pip.conf /etc/pip.conf
COPY Pipfile Pipfile.lock pipenv.txt /usr/src/app/
COPY hunts/runtimes/lua/luarocks/config.lua /etc/luarocks/config-5.2.lua

WORKDIR /usr/src/app

RUN apk add --no-cache \
    lua5.2 \
    postgresql-client \
    postgresql-libs \
    imlib2 \
 && apk add --no-cache -t builddeps \
    curl \
    gcc \
    git \
    imlib2-dev \
    linux-headers \
    lua5.2-dev \
    luarocks5.2 \
    musl-dev \
    postgresql-dev \
 && pip install --no-deps -r pipenv.txt \
 && pipenv install --system --deploy \
 && luarocks-5.2 install lua-cjson \
 && luarocks-5.2 install lua-imlib2 \
 && apk del builddeps

COPY . .

RUN addgroup -g 500 -S django \
 && adduser -h /usr/src/app -s /sbin/nologin -G django -S -u 500 django \
 && install -d -g django -o django /config /static /uploads/events /uploads/puzzles
USER django

VOLUME ["/config", "/static", "/uploads/events", "/uploads/puzzles"]

EXPOSE 3031
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]
