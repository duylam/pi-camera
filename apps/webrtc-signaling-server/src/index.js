const $ = require('lodash');
const http = require('http');
const d = require('./lib/debug'); 
const config = require('./lib/config'); 
const GrpcServer = require('./lib/grpc-server'); 

function main() {
  const debug = d('app');
  const grpcServer = new GrpcServer();

  debug.log('Starting GRPC server');
  grpcServer.start();

  setInterval(function () {
    grpcServer.keepStreamsAlive();
  }, config.HeartBeatIntervalMs);
  debug.log(`Scheduled heartbeat at ${config.HeartBeatIntervalMs}ms interval`);
}

main();

