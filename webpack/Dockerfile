# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.19.0-alpine3.12@sha256:efbd966c348dcc9c03a46a24a5380e764bbde3412a100e42ff6b604a0a3015a0

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
