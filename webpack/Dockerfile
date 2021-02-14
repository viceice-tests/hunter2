# syntax=docker/dockerfile:1.1.3-experimental
FROM node:14.15.5-alpine3.13@sha256:0c7162a9ee87193fb9b6b9940bcf7f9491d0a87477e5130d66fcb1eb442f36ae

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
