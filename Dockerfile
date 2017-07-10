FROM python:3.6.1

ARG DEBIAN_FRONTEND=noninteractive
ARG LUAROCKS_VERSION=2.4.2
ARG LUAROCKS_INSTALL=luarocks-$LUAROCKS_VERSION
ARG LUAROCKS_TMP_LOC=/tmp/luarocks

RUN apt-get update \
 && apt-get -y install \
    liblua5.2-0 \
    postgresql-client \
    libimlib2 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements/frozen.txt /usr/src/app/requirements.txt
WORKDIR /usr

ARG build_deps="gcc lua5.2 lua5.2-dev unzip libimlib2-dev"
RUN apt-get update \
 && apt-get -y install ${build_deps} \
 && pip install -r /usr/src/app/requirements.txt --no-deps \
 && curl -OL https://luarocks.org/releases/${LUAROCKS_INSTALL}.tar.gz \
 && tar xzf $LUAROCKS_INSTALL.tar.gz \
 && mv $LUAROCKS_INSTALL $LUAROCKS_TMP_LOC \
 && rm $LUAROCKS_INSTALL.tar.gz \
 && cd ${LUAROCKS_TMP_LOC} \
 && ./configure \
    --lua-suffix=5.2 \
    --lua-version=5.2 \
    --sysconfdir=/opt/hunter2 \
    --rocks-tree=/opt/hunter2 \
    --force-config \
 && make install \
 && cd - \
 && luarocks install \
    lua-imlib2 \
 && apt-get -y purge ${build_deps} \
 && apt-get -y --purge autoremove \
 && rm -rf /var/lib/apt/lists/* ${LUAROCKS_TMP_LOC} ${LUAROCKS_INSTALL}.tar.gz

WORKDIR /usr/src/app
COPY . .

RUN addgroup --gid 500 --system django \
 && adduser --system --shell /sbin/nologin --gid 500 --system --uid 500 django \
 && install -d -g django -o django /config /static /uploads/events /uploads/puzzles
USER django

VOLUME ["/config", "/static", "/uploads/events", "/uploads/puzzles"]

EXPOSE 3031
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]
