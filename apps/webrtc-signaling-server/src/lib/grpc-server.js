const EventEmitter = require('events');
const grpc = require('@grpc/grpc-js');
const $ = require('lodash');
const BPromise = require('bluebird');

const d = require('./debug'); 
const config = require('./config'); 
const StreamCall = require('./stream-call');
const grpcServices = require('../schema_node/rtc_signaling_service_grpc_pb');
const grpcModels = require('../schema_node/rtc_signaling_service_pb');

// See values at https://github.com/grpc/grpc-node/blob/9acb1b657530c18e498ef7e6538c1234f33aee4f/packages/grpc-js/src/constants.ts#L18
const GrpcStatusCode = grpc.status;

class GrpcError extends Error {
  constructor(code, message) {
    super(message);

    // See https://github.com/grpc/grpc/blob/master/doc/statuscodes.md
    this.code = code;
  }
}

class GrpcServer {
  constructor() {
    this._debug = d('grpc-server');

    // Events:
    //  - pi-incoming-message: the message sent from Pi box
    //  - web-incoming-message: the message sent from the browser
    this._event = new EventEmitter();
    this._event.on('message', this._onGrpcMessage.bind(this, d(`${this._debug.ns}:onGrpcMessage`)));

    // Only support single Pi box at this time
    this._piClient = new StreamCall({ns: `${this._debug.ns}:pi-client`});
    this._webClients = {};
  }

  start() {
    this._debug.log('Starting service'); 
    const server = new grpc.Server();
    server.addService(grpcServices.RtcSignalingService, {
      subscribeMessage: this._createSubscribeMessageImplementation(),
      sendMessage: this._createSendMessageImplementation(),
      subscribeIncomingMessage: this._createSubscribeIncomingMessageImplementation()
    });
    server.bindAsync(`0.0.0.0:${config.GrpcPort}`, grpc.ServerCredentials.createInsecure(), () => {
      server.start();
      this._debug.log(`Listens on ${config.GrpcPort}`);
    });
  }

  keepStreamsAlive() {
    this._piClient.sendNoop();
    for (const c of $.values(this._webClients)) {
      c.sendNoop();
    }
  }

  _onGrpcMessage(debug, {type, clientId, message}) {
    switch(type) {
      case 'pi-incoming-message': {
        debug.log(`Got new pi-incoming-message`);  
        try {
          let clientId

          if (message.getRequest()) {
            clientId = message.getRequest().getCallHeader().getClientId();
          }
          else {
            clientId = message.getResponse().getCallHeader().getClientId();
          }

          const ns = `[web-${clientId}]`
          this._webClients[clientId].send(message);
          debug.log(`${ns} Sent to web client`);  
        } 
        catch (ignored) {
          debug.error(`Error on processing. Skip the message`, ignored);  
        }
        break;
      }
      case 'web-incoming-message': {
        const ns = `[web-${clientId}]`
        debug.log(`${ns} Got new web-incoming-message`);  
        try {
          this._piClient.send(message);
          debug.log(`${ns} Sent to Pi box`);  
        } 
        catch (ignored) {
          debug.error(`${ns} Error on sending to Pi box.`, ignored);  

          const msgResponseError = new grpcModels.RtcSignalingMessage.Response.Error();
          msgResponseError.setErrorMessage(ignored.message);
          const msgResponse = new grpcModels.RtcSignalingMessage.Response();
          msgResponse.setError(msgResponseError);
          const msg = new grpcModels.RtcSignalingMessage();
          msg.setResponse(msgResponse);

          try {
            this._webClients[clientId].send(msg);
            debug.log(`${ns} Sent back error response now`);  
          }
          catch (ignored) {
            debug.error(`${ns} Error on sending back response, ignore`, ignored);
          }
          this._sendMessageToWebClient(clientId, msg);
        }
        break;
      }
      default: {
        debug.log(`Unsupported type=${type}, ignore!`);
      }
    } 
  }

  _createSubscribeMessageImplementation() {
    const debug = d(`${this._debug.ns}:subscribeMessage`);
    return (call) => {
      debug.log('New Pi box connected');

      this._piClient.attach(call);
      this._piClient.on('message', (msg) => {
        if (!msg.getNoop()) {
          debug.log('Received message from pi', msg.toObject());
          this._event.emit('message', {message: msg, type:'pi-incoming-message'});
        }
      });
    }
  }

  _createSendMessageImplementation() {
    const debug = d(`${this._debug.ns}:sendMessage`);
    return (call, done) => {
      debug.log('Received a call');

      if (!this._piClient.attached) {
        return done(new GrpcError(GrpcStatusCode.ABORTED, 'Pi box went offline'));
      }

      const req = call.request;
      const rtcRequest = req.getRequest();
      if (!rtcRequest) {
        return done(new GrpcError(GrpcStatusCode.INVALID_ARGUMENT, 'Missing field "request"'));
      }

      const callHeader = rtcRequest.getCallHeader();
      if (!callHeader) {
        return done(new GrpcError(GrpcStatusCode.INVALID_ARGUMENT, 'Missing field "request.call_header"'));
      }

      const clientId = callHeader.getClientId();
      if (!clientId) {
        return done(new GrpcError(GrpcStatusCode.INVALID_ARGUMENT, 'Missing field "request.call_header.client_id"'));
      }

      debug.log(`Received message from web-${clientId}`, req.toObject());
      this._event.emit('message', {message: req, clientId, type:'web-incoming-message'});

      done(null, new grpcModels.google.protobuf.Empty());
    }
  }

  _createSubscribeIncomingMessageImplementation() {
    const debug = d(`${this._debug.ns}:subscribeIncomingMessage`);
    return (call) => {
      debug.log('New browser connected');

      const req = call.request;

      const callHeader = req.getCallHeader();
      if (!callHeader) {
        const msg = 'Missing field "call_header", closing'; 
        debug.log(msg);
        return call.destroy(new GrpcError(GrpcStatusCode.INVALID_ARGUMENT, msg));
      }

      const clientId = callHeader.getClientId();
      if (!clientId) {
        const msg = 'Missing field "call_header.client_id", closing';
        debug.log(msg);
        return call.destroy(new GrpcError(GrpcStatusCode.INVALID_ARGUMENT, msg));
      }

      debug.log(`Read client_id=${clientId}`);
      let webClient;
      if ($.has(this._webClients, clientId)) {
        debug.log(`Found existing web client with id ${clientId}, detach existing stream`);
        webClient = this._webClients[clientId];
        webClient.detach();
      } 
      else {
        webClient = new StreamCall({clientId, ns: `${this._debug.ns}:web-client`});
        this._webClients[clientId] = webClient;
        debug.log('Created and added new web client');
      }
        
      webClient.attach(call);
      debug.log(`Attached the browser for client_id=${clientId}`);
      
      webClient.sendNoop();
      debug.log(`Sent noop to inform that the stream ${clientId} is ready on server side`);
    }
  }
}

module.exports = GrpcServer;

