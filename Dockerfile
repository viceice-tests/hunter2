# Construct a common base image for creating python wheels and the final image
FROM python:3.8.1-alpine3.11 AS runtime_base

RUN apk add --no-cache \
    lua5.2 \
    postgresql-client \
    postgresql-libs \
    imlib2

# Setup user
RUN addgroup -g 500 -S hunter2 \
 && adduser -h /opt/hunter2 -s /sbin/nologin -G hunter2 -S -u 500 hunter2
WORKDIR /opt/hunter2/src


# Build image with all the pythong dependancies.
FROM runtime_base AS python_build

RUN apk add --no-cache \
    gcc \
    git \
    libffi-dev \
    linux-headers \
    lua5.2-dev \
    musl-dev \
    postgresql-dev

# Suppress pip version warning, we're keeping the version from the docker base image
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
# Disable caching in pip, this is unecessary complexity in a docker build
ARG PIP_NO_CACHE_DIR=1

ENV PATH "/root/.poetry/bin:${PATH}"
ARG poetry_version=1.0.2
RUN wget "https://raw.githubusercontent.com/python-poetry/poetry/${poetry_version}/get-poetry.py" \
 && python get-poetry.py --version "${poetry_version}" \
 && rm get-poetry.py \
 && poetry config virtualenvs.create false \
 && python -m venv /opt/hunter2/venv

ARG dev_flag=" --no-dev"
COPY poetry.lock pyproject.toml /opt/hunter2/src/
RUN . /opt/hunter2/venv/bin/activate \
 && poetry install${dev_flag} --no-root


# Build all the required Lua components
FROM alpine:3.11 AS lua_build

COPY hunts/runtimes/lua/luarocks/config.lua /etc/luarocks/config-5.2.lua

RUN apk add --no-cache \
    curl \
    gcc \
    imlib2-dev \
    lua5.2-dev \
    luarocks5.2 \
    musl-dev
RUN luarocks-5.2 install lua-cjson 2.1.0-1
RUN luarocks-5.2 install lua-imlib2 dev-2


# Build the production webpack'ed assets
FROM node:12.14.1-alpine3.11 as webpack_build

WORKDIR /opt/hunter2/src

COPY .yarnrc package.json yarn.lock /opt/hunter2/src/
RUN yarn install --frozen-lockfile
COPY . .
RUN "$(yarn bin webpack)" --config webpack.prod.js


# Build the final image
FROM runtime_base

# Copy in the requried components from the previous build stages
COPY --from=lua_build /opt/hunter2 /opt/hunter2
COPY --from=python_build /opt/hunter2/venv /opt/hunter2/venv
COPY --from=webpack_build /opt/hunter2/assets /opt/hunter2/assets
COPY --from=webpack_build /opt/hunter2/src/webpack-stats.json /opt/hunter2/src/webpack-stats.json
COPY . .

RUN install -d -g hunter2 -o hunter2 /config /uploads/events /uploads/puzzles /uploads/solutions
VOLUME ["/config", "/uploads/events", "/uploads/puzzles", "/uploads/solutions"]

USER hunter2

EXPOSE 8000

ENTRYPOINT ["/opt/hunter2/venv/bin/python", "manage.py"]
CMD ["rundaphne", "--bind", "0.0.0.0"]
