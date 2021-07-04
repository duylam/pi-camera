const EventEmitter = require('events');
const noop = require('lodash/noop');
const d = require('./debug'); 

const grpcModels = require('../schema_node/rtc_signaling_service_pb');

class PiClient extends EventyEmitter {
  constructor({ns}) {
    super()

    this._call = null;
    this._debug = d(`${ns}:${Date.now()}`);
    this._cleanupEvents = noop;

    noopRequest = new grpcModels.RtcSignalingMessage.Request();
    noopRequest.setNoop(new grpcModels.google.protobuf.Empty());
    this._noopRequest = new grpcModels.RtcSignalingMessage();
    this._noopRequest.setRequest(noopRequest);
  }

  start(call) {
    this.end();

    const boundOnCallData = this._onCallData.bind(this);
    const boundOnCallEnd = this._onCallEnd.bind(this);
    this._call = call;
    call
      .on('data', boundOnCallData)
      .on('error', boundOnCallEnd)
      .on('end', boundOnCallEnd); 
    this._cleanupEvents = function () {
      call
        .removeListener('data', boundOnCallData)
        .removeListener('error', boundOnCallEnd)
        .removeListener('end', boundOnCallEnd);
    };
    this._debug.log('Started');
  }

  sendNoop() {
    if (this._call) {
      this._call.write(this._noopRequest);
    }
  }

  send(grpcRequest) {
    if (!this._call) {
      throw new Error('Not start yet');
    }

    this._call.write(grpcRequest);
  }

  end() {
    if (!this._call) {
      return this._debug.log('Warn: not start yet, skip');
    }

    this._call = null;
    this._cleanupEvents();
    this.removeAllListeners();
    this._debug.log('Ended');
  }

  _onCallData(msg) {
    this.emit('message', msg);
  } 

  _onCallEnd(e) {
    if (e) {
      this._debug.error('Stream error', e);
    }
    else {
      this._debug.log('Stream ends');
    }

    this.end();
  }
}

module.exports = PiClient

