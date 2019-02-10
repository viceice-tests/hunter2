FROM node:11-alpine

COPY package.json /
RUN npm install

WORKDIR /usr/src/app

EXPOSE 4000
ENTRYPOINT ["npm", "run-script"]
CMD ["start"]
