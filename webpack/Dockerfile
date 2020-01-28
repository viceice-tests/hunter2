FROM node:12.14.1-alpine3.11

COPY package.json yarn.lock /
RUN yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
