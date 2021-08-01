FROM node:14.17.4-stretch

RUN mkdir /app
WORKDIR /app

ENTRYPOINT ["node"]
CMD ["index.js"]

COPY ./app/ /app/
RUN npm install

