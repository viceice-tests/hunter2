ARG build_tag=latest


FROM registry.gitlab.com/hunter2.app/hunter2/webpack:${build_tag} AS webpack


FROM registry.gitlab.com/hunter2.app/hunter2/app:${build_tag} AS app

COPY --from=webpack /usr/src/app/assets /usr/src/app/assets

USER root
RUN python manage.py collectstatic


FROM nginx:1.14.0-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=app /static /static
