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
const GrpcStatusCodes = grpc.status;

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
    this._event.on('message', this._onGrpcMessage.bind(this, debug(`${this._debug.ns}:onGrpcMessage`)));

    // Only support single Pi box at this time
    this._piClient = new PiClient({ns: `${this._debug.ns}:pi-client`});
    this._webClients = {};
  }

  start() {
    const server = new grpc.Server();
    server.addService(grpcServices.RtcSignalingService, {
      subscribeMessage: this._createSubscribeMessageImplementation(),
      sendMessage: this._createSendMessageImplementation(),
      subscribeIncomingMessage: this._createSubscribeIncomingMessageImplementation()
    });
    server.bindAsync(`0.0.0.0:${config.GrpcPort}`, grpc.ServerCredentials.createInsecure(), () => {
      server.start();
      this._debug.log(`Signaling GRPC service listens on ${config.GrpcPort}`);
    });
  }

  keepStreamAlive() {
    this._piClient && this._piClient.sendNoop();
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

          const ns = `[${clientId}]`
          debug.log(`${ns} Sending message to web client`);  
          this._sendMessageToWebClient(clientId, message);
        } 
        catch (ignored) {
          debug.error(`Error on processing. Skip the message`, ignored);  
        }
      }
      case 'web-incoming-message': {
        const ns = `[${clientId}]`
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

          debug.log(`${ns} Sending back error response now`);  
          this._sendMessageToWebClient(clientId, msg);
        }
      }
    } 
  }

  _sendMessageToWebClient(clientId, msg) {
    try {
      this._webClietns[clientId].send(msg);
    }
    catch (ignored) { }
  }

  _createSubscribeMessageImplementation() {
    const debug = d(`${this._debug.ns}:subscribeMessage`);
    return (call) => {
      debug.log('New Pi box connected');

      this._piClient.attach(call);
      this._piClient.on('message', (msg) => {
        this._event.emit('message', {message: msg, type:'pi-incoming-message'});
      });
    }
  }

  _createSendMessageImplementation() {
    const debug = d(`${this._debug.ns}:sendMessage`);
    return async (req, done) => {
      debug.log('Received a call');

      if (!this._piClient.attached) {
        return done(new GrpcError(GrpcStatusCode.ABORTED, 'Pi box went offline'));
      }

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
        debug.log('Missing field "call_header", closing');
        return call.end();
      }

      const clientId = callHeader.getClientId();
      if (!clientId) {
        debug.log('Missing field "call_header.client_id", closing');
        return call.end();
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
      debug.log('Attached the browser');
    }
  }
}

module.exports = GrpcServer;


message CallHeader {
  string client_id = 1;
}

message SubscribeIncomingMessageRequest {
  CallHeader call_header = 1;
}

message RtcSignalingMessage {
  message Request {
    CallHeader call_header = 1;

    oneof type {
      google.protobuf.Empty create_offer = 10; 
      string answer_offer = 11; 
      google.protobuf.Empty confirm_answer = 12; // no response
      string ice_candidate = 13; // no response
    }
  }

  message Response {
    CallHeader call_header = 1;
    bool error = 2;
  
    oneof type {
      string create_offer = 10; 
      google.protobuf.Empty answer_offer = 11; 
    }
  }

  oneof type {
    Request request = 1;
    Response response = 2;
    google.protobuf.Empty noop = 3; // for heartbeat to keep connection alive, no response
  }
}

