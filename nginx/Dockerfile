# syntax=docker/dockerfile:1.1.3-experimental
ARG BUILD_TAG=latest
ARG IMAGE_TAG=registry.gitlab.com/hunter2.app/hunter2/app:${BUILD_TAG}
FROM ${IMAGE_TAG} AS app

USER root
RUN /opt/hunter2/venv/bin/python manage.py collectstatic

FROM alpine:3.12@sha256:25f5332d060da2c7ea2c8a85d2eac623bd0b5f97d508b165f846c7d172897438

RUN --mount=type=cache,target=/var/cache/apk apk add \
    nginx \
    nginx-mod-http-lua

ADD https://raw.githubusercontent.com/knyar/nginx-lua-prometheus/379c0a4d4d6f3c5b0eb93691fc7e14fff498e1ca/prometheus.lua /usr/lib/lua/5.1/

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=app /static /static

CMD ["nginx", "-g", "daemon off;"]
