FROM python:3.6

RUN apt-get update && apt-get install -y \
liblua5.2-dev \
postgresql-client \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /usr/src/app/
WORKDIR /usr
RUN pip install -r /usr/src/app/requirements.txt
WORKDIR /usr/src/app
COPY . .

RUN groupadd -g 500 -r django && useradd -g django -r -u 500 django
RUN install -d -g django -o django /config /storage/media
USER django

VOLUME ["/config", "/storage"]

EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
