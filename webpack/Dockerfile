# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.20.0-alpine3.12@sha256:a3cc3a7f3dbf8c7d30c89e1fa76fad14137b411671c146f990a0d3cc1c294acb

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
