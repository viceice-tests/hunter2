# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.18.1-alpine3.11

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
