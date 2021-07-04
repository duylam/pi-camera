const Koa = require('koa');
const logger = require('koa-logger');
const $ = require('lodash');
const http = require('http');
const koaBody = require('koa-body');
const cors = require('@koa/cors');
const d = require('./lib/debug'); 
const config = require('./lib/config'); 
const GrpcServer = require('./lib/grpc-server'); 


let piClient = new PiClient();

function main() {
  startRestService();
  startGrpcService();
}

function startRestService() {
  const debug = d('rest');
  const app = new Koa();

  app.use(cors({
    allowMethods: 'POST, PUT',
    maxAge: 3600
  }));
  app.use(koaBody());
  app.use(logger());
  app.use(function(ctx) {
    const path = ctx.request.path;
    let done = $.noop;
    const p = new Promise(function (fulfill) {
      done = fulfill;
    });
    ctx.response.type = 'text/plain; charset=utf-8';
    const callId = ctx.request.query.cid;

    if (path.startsWith('/offer')) {
      const req = new grpcModels.RtcSignalingRequest();
      req.setCallId(callId);
      req.setCreateOffer(new grpcModels.google.protobuf.Empty());
      piClient.send(req, function (e, result) {
        ctx.response.type = 'text/plain';
        if (e) {
          ctx.response.body = e.message;
          ctx.response.status = 500;
        }
        else {
          if (result.error) {
            ctx.response.status = 500;
          }
          else {
            ctx.response.body = result.getCreateOffer();
            debug.log('offer pi response', ctx.response.body);
          }
        }

        done();
      });
    }
    else if (path.startsWith('/ice')) {
      const req = new grpcModels.RtcSignalingRequest();
      req.setCallId(callId);
      req.setIceCandidate(JSON.stringify(ctx.request.body.sdp));
      piClient.send(req);
      ctx.response.status = 200;
      done();
    }
    else if (ctx.request.method === 'POST' && path.startsWith('/answer')) {
      const req = new grpcModels.RtcSignalingRequest();
      req.setCallId(callId);
      req.setAnswerOffer(ctx.request.body.sdp);
      piClient.send(req, function (e, result) {
        ctx.response.type = 'text/plain';
        if (e) {
          ctx.response.body = e.message;
          ctx.response.status = 500;
        }
        else {
          if (result.error) {
            ctx.response.status = 500;
          }
          else {
            ctx.response.status = 200;
          }
        }

        done();
      });
    }
    else if (ctx.request.method === 'PUT' && path.startsWith('/answer')) {
      const req = new grpcModels.RtcSignalingRequest();
      req.setCallId(callId);
      req.setConfirmAnswer(new grpcModels.google.protobuf.Empty());
      piClient.send(req);
      ctx.response.type = 'text/plain';
      ctx.response.status = 200;
      done();
    }
    else {
      ctx.response.type = 'text/plain';
      ctx.response.status = 400;
      ctx.response.body = `Unknown path ${path}`;
      done();
    }

    return p;
  });
  app.on('error', function (e, ctx) {
    debug.error('Koa error event', e, ctx);
  });

  http.createServer(app.callback()).listen(config.RestPort, function () {
    debug.log(`REST listens on ${config.RestPort}`);
  });
}

function startGrpcService() {
  const grpcServer = new GrpcServer();
  grpcServer.start();

  setInterval(function () {
    grpcServer.keepStreamAlive();
  }, config.HeartBeatIntervalMs);
}

function subscribeImplementation(debug) {
  return function (call) {
    debug.log('New Pi client connected');
    call.on('error', function (e) {
      debug.error('GRPC stream of subscribe() error', e);
      piClient.end();
    });
    piClient.start(call);
  }
}

main();

