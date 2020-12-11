# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.20.0-alpine3.12@sha256:14acf99d0233dc5a8cec28c036a9634febf9993240a44a9bfbb45305afa37807

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
