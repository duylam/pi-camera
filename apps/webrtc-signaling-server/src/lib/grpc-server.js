const EventEmitter = require('events');
const grpc = require('@grpc/grpc-js');
const $ = require('lodash');
const BPromise = require('bluebird');

const d = require('./debug'); 
const config = require('./config'); 
const PiClient = require('./pi-client');
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
    //  - pi-client-message: the message sent from Pi box
    this._event = new EventEmitter();
    this._event.setMaxListeners(d.MaxEventListener);

    // Only support single Pi box at this time
    this._piClient = null;
  }

  start() {
    const server = new grpc.Server();
    server.addService(grpcServices.RtcSignalingService, {
      subscribeOtherPeer: this._createSubscribeOtherPeerImplementation(),
      sendRtcMessage: this._createSendRtcMessageImplementation(),
      webSubscribeOtherPeer: this._createWebSubscribeOtherPeerImplementatio()
    });
    server.bindAsync(`0.0.0.0:${config.GrpcPort}`, grpc.ServerCredentials.createInsecure(), () => {
      server.start();
      this._debug.log(`GRPC listens on ${config.GrpcPort}`);
    });
  }

  sendHeartbeat() {
    this._piClient && this._piClient.sendNoop();
  }

  _createSubscribeOtherPeerImplementation() {
    const debug = d(`${this._debug.ns}:pi-client`);
    return (call) => {
      debug.log('New Pi box connected');
      if (this._piClient) {
        debug.log('Found existing PiClient object, destroying it');
        this._piClient.end();
      }

      debug.log('Creating new PiClient object');
      this._piClient = new PiClient({ns: debug.ns});
      piClient.start(call);
      pi.on('message', () => {
        this._event.emit('pi-client-message', msg);
      });
    }
  }

  _createSendRtcMessageImplementation() {
    const ns = `${this._debug.ns}:send-rtc-message`;
    return async (req, done) => {
      const debug = d(`${ns}:${Date.now()}`);
      debug.log('Sending request to PiClient');
      try {
        this._piClient.send(req);
      }
      catch (ignored)  {
        debug.error(ignored);
        return done(new GrpcError(GrpcStatusCodes.NOT_FOUND, ignored.message));
      }

      let response = new grpcModels.RtcSignalingMessage();
      const endWaiting = $.noop;
      const waitPiClientMessage = BPromise.fromCallback((cb) => endWaiting = cb);
      const onPiClientMessage = (msg) => {

      };

      try {
        const rtcRequest = request.getRequest();
        if (rtcRequest) {
          if (rtcRequest.getCreateOffer() || rtcRequest.getAnswerOffer()) {
            const clientId = rtcRequest.getClientId();
            if (!clientId) {
              debug.error('Expecting request.client_id field but unavailable. Finishing the call with empty response');
            }
            else {
              this._event.on('pi-client-message', onPiClientMessage);
              response = await waitPiClientMessage.timeout(1000);
            }
          }
        }
      }
      catch (ignored) {

      }
      finally {
        this._event.removeListener('pi-client-message', onPiClientMessage);
        done(null, response);
      }
    }
  }

  _createWebSubscribeOtherPeerImplementatio() {

  }
}

module.exports = GrpcServer;

service RtcSignaling {
  // For the Pi client to communicate signaling messages with other peers
  rpc SubscribeOtherPeer(stream RtcSignalingMessage) returns (stream RtcSignalingMessage) {}

  // For the browser to send signaling message
  rpc SendRtcMessage(RtcSignalingMessage) returns (RtcSignalingMessage) {}

  // For the browser to receive push notification of signaling messages
  rpc WebSubscribeOtherPeer(WebSubscribeOtherPeerRequest) returns (stream RtcSignalingMessage) {}
}

message WebSubscribeOtherPeerRequest {
  string client_id = 1;

message RtcSignalingMessage {
  message Request {
    string client_id = 1;

    oneof type {
      google.protobuf.Empty create_offer = 10; 
      string answer_offer = 11; 
      google.protobuf.Empty confirm_answer = 12; 
      google.protobuf.Empty noop = 13;
      string ice_candidate = 14;
    }
  }

  message Response {
    bool error = 1;
  
    oneof type {
      string create_offer = 10; 
      google.protobuf.Empty answer_offer = 11; 
    }
  }

  oneof type {
    Request request = 1;
    Response response = 2;
  }
}


