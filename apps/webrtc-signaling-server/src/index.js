const Koa = require('koa');
const logger = require('koa-logger');
const $ = require('lodash');
const http = require('http');
const koaBody = require('koa-body');
const cors = require('@koa/cors');
const d = require('./lib/debug'); 
const config = require('./lib/config'); 
const GrpcServer = require('./lib/grpc-server'); 

function main() {
  const debug = d('app');
  const grpcServer = new GrpcServer();

  debug.log('Starting GRPC server');
  grpcServer.start();

  setInterval(function () {
    grpcServer.keepStreamAlive();
  }, config.HeartBeatIntervalMs);
  debug.log(`Scheduled hearthbeat at ${config.HeartBeatIntervalMs}ms interval`);
}

main();

