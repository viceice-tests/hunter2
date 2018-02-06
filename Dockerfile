FROM python:3.6.4

ARG BUILD_DEPS="gcc lua5.2 lua5.2-dev unzip libimlib2-dev libjson-c-dev"
ARG DEBIAN_FRONTEND=noninteractive
ARG LUAROCKS_VERSION=2.4.3
ARG LUAROCKS_INSTALL=luarocks-$LUAROCKS_VERSION
ARG LUAROCKS_TMP_LOC=/tmp/luarocks
ARG PIPENV_PARAMS=

COPY pip.conf /etc/pip.conf
COPY Pipfile Pipfile.lock pipenv.txt /usr/src/app/
COPY hunts/runtimes/lua/luarocks/config.lua /opt/hunter2/luarocks/config-5.2.lua

WORKDIR /usr/src/app

RUN apt-get update \
 && apt-get -y install \
    liblua5.2-0 \
    postgresql-client \
    libimlib2 \
    libjson-c2 \
    ${BUILD_DEPS} \
 && pip install --no-deps -r pipenv.txt \
 && pipenv install --system --deploy ${PIPENV_PARAMS} \
 && curl -OL https://luarocks.org/releases/${LUAROCKS_INSTALL}.tar.gz \
 && tar xzf $LUAROCKS_INSTALL.tar.gz \
 && mv $LUAROCKS_INSTALL $LUAROCKS_TMP_LOC \
 && rm $LUAROCKS_INSTALL.tar.gz \
 && cd ${LUAROCKS_TMP_LOC} \
 && ./configure \
    --lua-suffix=5.2 \
    --lua-version=5.2 \
    --sysconfdir=/opt/hunter2/luarocks \
    --rocks-tree=/opt/hunter2 \
    --force-config \
 && make install \
 && cd - \
 && luarocks install lua-imlib2 0.1-4 \
 && luarocks install lua-cjson 2.1.0-1 \
 && apt-get -y purge ${BUILD_DEPS} \
 && apt-get -y --purge autoremove \
 && rm -rf /var/lib/apt/lists/* ${LUAROCKS_TMP_LOC}

COPY . .

RUN addgroup --gid 500 --system django \
 && adduser --system --home /usr/src/app --shell /sbin/nologin --gid 500 --system --uid 500 django \
 && install -d -g django -o django /config /static /uploads/events /uploads/puzzles
USER django

VOLUME ["/config", "/static", "/uploads/events", "/uploads/puzzles"]

EXPOSE 3031
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]
