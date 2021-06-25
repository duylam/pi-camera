const Koa = require('koa');
const grpc = require('@grpc/grpc-js');
const grpcServices = require('./schema_node/rtc_signaling_service_grpc_pb');
const grpcModels = require('./schema_node/rtc_signaling_service_pb');
const app = new Koa();

app.use(async function(ctx) {
  ctx.body = 'Hello World';
});

app.listen(process.env.PI_MEETING_REST_PORT);

function main() {
  const server = new grpc.Server();
  server.addService(grpcServices.RtcSignalingService, {subscribe: subscribeImplementation});
  server.bindAsync(`0.0.0.0:${process.env.PI_MEETING_GRPC_PORT}`, grpc.ServerCredentials.createInsecure(), () => {
    server.start();
  });
}

function subscribeImplementation(call) {

}

main();

