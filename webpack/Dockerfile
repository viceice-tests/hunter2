FROM node:12.13.0-alpine3.10

COPY package.json yarn.lock /
RUN yarn install --frozen-lockfile

WORKDIR /usr/src/app

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
