Launching an Environment
========================

First select which kind of environment you want to run.

For a basic development environment using the django development webserver:
```shell
ln -s docker-compose.dev.yml docker-compose.yml
```
This environment maps the local repo into the container and will dynamically reload code changes.

For a production-like environment using uwsgi and nginx:
```shell
ln -s docker-compose.prod.yml docker-compose.yml
```
This environment uses static code from the docker image.

Either environment can be launched using the following commands:
```shell
echo 'H2_DEBUG=True' > .env
docker-compose up -d
docker-compose run --rm app migrate_schemas
```

To get performance profiling with silk, do:
```shell
echo 'H2_SILK=True' >> .env
docker-compose up -d
```

If you are running a development instance on a laptop then you need to add some hosts file entries:
```
echo 127.0.0.1 hunter2.local dev.hunter2.local > /etc/hosts
docker-compose run --rm app createsuperuser
docker-compose run --rm app createdefaultevent
```
`dev.hunter2.local` is the default event subdomain. If you are working with more events add more names here.

<<<<<<< HEAD
To create the base objects run the following:
```
docker-compose run --rm app python manage.py setupsite
docker-compose run --rm app python manage.py createsuperuser
docker-compose run --rm app python manage.py createevent
```
