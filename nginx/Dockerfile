ARG app_tag=latest
FROM registry.gitlab.com/hunter2.app/hunter2/app:${app_tag} AS app

RUN python manage.py collectstatic

FROM alpine:3.8

RUN apk add --no-cache \
    nginx \
    nginx-mod-http-lua

ADD https://raw.githubusercontent.com/knyar/nginx-lua-prometheus/6982f250cf6e73c7f398869e3769d76bf56e2ee2/prometheus.lua /usr/lib/lua/5.1/

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=app /static /static

CMD ["nginx", "-g", "daemon off;"]
