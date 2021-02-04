# syntax=docker/dockerfile:1.1.3-experimental
FROM node:14.15.5-alpine3.13@sha256:17dc61b31b2a12a1390b5a4e2e69b0d0886a0d77647f88c5a33787ac457fa83e

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
