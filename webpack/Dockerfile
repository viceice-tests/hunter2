FROM node:12.15.0-alpine3.11

COPY package.json yarn.lock /
RUN yarn install --frozen-lockfile

EXPOSE 4000
ENTRYPOINT ["yarn"]
CMD ["start"]
