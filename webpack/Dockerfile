# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.19.1-alpine3.12@sha256:f657294c21fd6efe3c2c77ed451f9de89a522c4dbb052e63b34d4788a56fa9f7

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
