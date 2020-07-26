Launching an Environment
========================

Development Environment
-----------------------

Hunter 2 requires the following minimum versions to build:
| -------------- | ------ |
| docker-engine  | 18.09  |
| docker-compose | 1.25.1 |

We need to export some variables to enable the build features we are using:
```shell
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1
```

Link the development compose file:
```shell
ln -s docker-compose.dev.yml docker-compose.yml
```
This environment maps the local repo into the container and will dynamically reload code changes.

Build the container images:
```shell
docker-compose build
```

You will need to configure some hosts file entries for the wildcard DNS:
```shell
echo 127.0.0.1 hunter2.local www.hunter2.local dev.hunter2.local >> /etc/hosts
```
`dev.hunter2.local` is the default event subdomain. If you are working with more events add more names here.

Launch the containers and configure the database tables:
```shell
docker-compose up -d
```

There is also a `Makefile` with some targets for developer convenience. See `make help` for details.

To create the database tables and base objects run the following:
```shell
docker-compose run --rm app migrate_schemas
docker-compose run --rm app setupsite
docker-compose run --rm app createsuperuser
docker-compose run --rm app createevent
```

Load an event page (such as [http://dev.hunter2.local:8080/hunt/](http://dev.hunter2.local:8080/hunt/)) and log in.
This implicitly creates a profile for you, and then you can strugle make an admin team.

### Profiling ###
To enable performance profiling with silk, do:
```shell
echo 'H2_SILK=True' >> .env
docker-compose up -d
docker-compose run --rm app migrate_schemas
```

Production Environment
----------------------

Link the production compose file:
```shell
ln -s docker-compose.prod.yml docker-compose.yml
```

Launch the containers and configure the database tables:
```shell
docker-compose up -d
docker-compose run --rm app migrate_schemas
```

To create the base objects run the following:
```shell
docker-compose run --rm app setupsite
docker-compose run --rm app createsuperuser
docker-compose run --rm app createevent
```

Development Process
-------------------

To manipulate the Python dependencies you need to run `poetry`. The easiest way to do this is from the latest python build container as follows:
```shell
docker-compose -f docker-compose.tools.yml run --rm poetry ...
```

There are several commands like this specified in the `docker-compose.tools.yml`, with the notable exception of `yarn` for which you should use the `webpack`
container in `docker-compose.dev.yml`. To simplify this process you can use the `h2tools.sh` alias file on a `sh` compatible shell:
```shell
. h2tools.sh
```

This will add all the tools with `h2-` prefix to your current shell. (`h2-poetry`, `h2-yarn` etc...)


Copyright
=======
Hunter 2 is a platform for running online puzzle hunts. Further information can be found at https://www.hunter2.app/ including details of contributors.

Copyright (C) 2017-2019  The Hunter 2 contributors.

Hunter 2 is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Hunter 2 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Aferro General Public License for more details.

You should have received a copy of the GNU Aferro General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
