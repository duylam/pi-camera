FROM node:14.17.4-stretch

RUN mkdir /app
WORKDIR /app

ENTRYPOINT ["node"]
CMD ["index.js"]

ENV PI_MEETING_GRPC_PORT ""
ENV PI_MEETING_HEARTBEAT_INTERVAL_MS ""
ENV PI_MEETING_MAX_EVENT_LISTENER ""

COPY ./app/ /app/
RUN npm install --production

