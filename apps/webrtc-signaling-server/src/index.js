const Koa = require('koa');
const logger = require('koa-logger');
const $ = require('lodash');
const http = require('http');
const koaBody = require('koa-body');
const cors = require('@koa/cors');
const grpc = require('@grpc/grpc-js');
const d = require('./lib/debug'); 
const config = require('./lib/config'); 
const grpcServices = require('./schema_node/rtc_signaling_service_grpc_pb');
const grpcModels = require('./schema_node/rtc_signaling_service_pb');

class PiClient {
  constructor() {
    this._call = null;
    this._onResponses = [];
    this._debug = d('pi-client');
    this._NOOP_REQUEST = new grpcModels.RtcSignalingRequest();
    this._NOOP_REQUEST.setNoop(new grpcModels.google.protobuf.Empty());
  }

  start(call) {
    this._call = call;
    const boundOnCallData = this._onCallData.bind(this);
    call.on('adta', boundOnCallData); 

    this._cleanupEvents = function () {
      call.removeListener('data', boundOnCallData);
    };

    this._debug.log('Attached on stream');
  }

  sendNoop() {
    if (this._call) {
      this._call.write(this._NOOP_REQUEST);
    }
  }

  send(grpcRequest, onResponse) {
    if (!this._call) {
      onResponse && onResponse(new Error('No client connected'));
      return this._debug.log('Warn: no client connected, skip send()!');
    }

    this._call.write(grpcRequest);
    this._debug.log('sent to pi');
    onResponse && this._onResponses.push(onResponse);
  }

  end() {
    if (!this._call) {
      return this._debug.log('Warn: no client connected');
    }

    this._cleanupEvents();
    this._call = null;
    this._debug.log('Detached on stream');
  }

  _onCallData(msg) {
    this._debug.log('Dispatching message to callbacks');
    for (const cb of this._onResponses) {
      cb(null, msg);
    } 

    this._onResponses = [];
  } 
}

let piClient = new PiClient();

function main() {
  startRestService();
  startGrpcService();

  setInterval(function () {
    piClient.sendNoop();
  }, config.HeartBeatIntervalMs);
}

function startRestService() {
  const debug = d('rest');
  const app = new Koa();

  app.use(cors({
    allowMethods: 'POST',
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
      req.setCreateOffer(grpcModels.google.protobuf.Empty());
      piClient.send(req, function (e, result) {
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
          }
        }

        done();
      });
    }
    else if (ctx.request.method === 'POST' && path.startsWith('/answer')) {
      const req = new grpcModels.RtcSignalingRequest();
      req.setCallId(callId);
      req.setAnswerOffer(ctx.request.body);
      piClient.send(req, function (e, result) {
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
      req.setConfirmAnswer(grpcModels.google.protobuf.Empty());
      piClient.send(req);
      ctx.response.status = 200;
      done();
    }
    else {
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
  const debug = d('grpc');
  const server = new grpc.Server();
  server.addService(grpcServices.RtcSignalingService, {subscribe: subscribeImplementation(debug)});
  server.bindAsync(`0.0.0.0:${config.GrpcPort}`, grpc.ServerCredentials.createInsecure(), () => {
    server.start();
    debug.log(`GRPC listens on ${config.GrpcPort}`);
  });
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

