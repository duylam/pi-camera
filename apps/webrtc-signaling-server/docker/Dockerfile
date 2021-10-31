FROM node:14.17.4-stretch

RUN mkdir /app
WORKDIR /app

ENTRYPOINT ["node", "index.js"]

COPY ./app/ /app/
RUN npm install --production

