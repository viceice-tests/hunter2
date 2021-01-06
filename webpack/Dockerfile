# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.20.1-alpine3.12@sha256:e63dd88799eeccf4f2869963bf79fb2aa7fa24aacf22ef9d6603c0c3ee7f4a07

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
