# syntax=docker/dockerfile:1.1.3-experimental
FROM node:12.20.1-alpine3.12@sha256:42998ae4420998ff3255fc2d6884e882bd32f06d45b057f4b042e33bf48a1240

COPY package.json yarn.lock /
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
