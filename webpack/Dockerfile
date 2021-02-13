# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.20.2-alpine3.12@sha256:361042d98d4a17bae412f140c9bd9e9bf2512206141fdae6a1384298b887c5d6

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
