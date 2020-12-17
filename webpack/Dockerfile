# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.20.0-alpine3.12@sha256:fa3b6a9051003554574f7e5bdab6495f431436b4b384a9ddcf4d33107bb99992

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
