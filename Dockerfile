FROM python:3.6.1

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get -y install \
    liblua5.2-0 \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

COPY requirements/frozen.txt /usr/src/app/requirements.txt
WORKDIR /usr

ARG build_deps="gcc lua5.2-dev"
RUN apt-get update \
 && apt-get -y install ${build_deps} \
 && pip install -r /usr/src/app/requirements.txt --no-deps \
 && apt-get -y purge ${build_deps} \
 && apt-get -y --purge autoremove \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . .

RUN addgroup --gid 500 --system django \
 && adduser --system --shell /sbin/nologin --gid 500 --system --uid 500 django \
 && install -d -g django -o django /config /static /uploads/events /uploads/puzzles
USER django

VOLUME ["/config", "/static", "/uploads/events", "/uploads/puzzles"]

EXPOSE 3031
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]
