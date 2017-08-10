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
docker-compose run --rm app python manage.py migrate
```

To get performance profiling with silk, do:
```shell
echo 'H2_SILK=True' >> .env
docker-compose up -d
```

If you want minimal data, you can run:
```
docker-compose run --rm app python manage.py createsuperuser
$ docker-compose run --rm app python manage.py createdefaultevent
```

If you want all the data that's used in the CI tests:
```
docker-compose run --rm app python manage.py loaddata hunts/fixtures/hunts_test.yaml
```


We also need to setup the `Site` object:
```
$ docker-compose run --rm app python manage.py setupsite
```
It's important to set the domain to match the name or IP and port you're using to access the site (eg. 127.0.0.1:8080 for a local docker development instance)
