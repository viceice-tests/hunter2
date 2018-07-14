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
docker-compose run --rm app createevent
```
`dev.hunter2.local` is the default event subdomain. If you are working with more events add more names here.

To create the base objects run the following:
```
docker-compose run --rm app setupsite
docker-compose run --rm app createsuperuser
docker-compose run --rm app createevent
```

Copyright
=======
Hunter 2 is a platform for running online puzzle hunts. Further information can be found at https://www.hunter2.app/ including details of contributors.

Copyright (C) 2017-2018  The Hunter 2 contributors.

Hunter 2 is free software: you can redistribute it and/or modify it under the terms of the GNU Aferro General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Hunter 2 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Aferro General Public License for more details.

You should have received a copy of the GNU Aferro General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
