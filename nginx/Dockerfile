# syntax=docker/dockerfile:1.1.3-experimental
ARG BUILD_TAG=latest
ARG IMAGE_TAG=registry.gitlab.com/hunter2.app/hunter2/app:${BUILD_TAG}
FROM ${IMAGE_TAG} AS app

USER root
RUN /opt/hunter2/venv/bin/python manage.py collectstatic

FROM openresty/openresty:1.19.3.1-2-alpine@sha256:0446c459cf3924dd46e5d975b2d2d1974d51842701dd546a061ae474f713f602

RUN --mount=type=cache,target=/var/cache/apk apk add -t opm \
    curl \
    perl \
 && opm get knyar/nginx-lua-prometheus=0.20201118 \
 && apk del --no-cache opm

COPY default.conf /etc/nginx/conf.d/default.conf
COPY --from=app /static /static
