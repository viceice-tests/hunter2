FROM python:3.6

RUN apt-get update && apt-get install -y \
liblua5.2-dev \
postgresql-client \
wget \
&& rm -rf /var/lib/apt/lists/*

# TODO: Remove when dockerize is no longer required
ENV DOCKERIZE_VERSION v0.3.0
RUN wget -q https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
&& tar -C /usr/local/bin -xzf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
&& rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

COPY requirements.txt /usr/src/app/
WORKDIR /usr
RUN pip install -r /usr/src/app/requirements.txt
WORKDIR /usr/src/app
COPY . .

RUN groupadd -g 500 -r django && useradd -g django -r -u 500 django
RUN install -d -g django -o django /config
RUN install -d -g django -o django /storage/media
USER django

VOLUME /config
VOLUME /storage

EXPOSE 8000
#TODO: Remove dockerize and make django database timeout tolerant
ENTRYPOINT ["dockerize", "-wait", "tcp://db:5432", "python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
