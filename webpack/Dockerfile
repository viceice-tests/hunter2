ARG webpack_tag=latest
FROM registry.gitlab.com/rconan/docker-webpack:${webpack_tag}

WORKDIR /usr/src/app
COPY . .
RUN npm install \
 && /node_modules/.bin/webpack --config webpack/config.js \
 && rm -rf node_modules
