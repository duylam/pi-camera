const EventEmitter = require('events');
const noop = require('lodash/noop');
const d = require('./debug'); 

const grpcModels = require('../schema_node/rtc_signaling_service_pb');

const noopMessage = (function () {
  const msg = new grpcModels.RtcSignalingMessage();
  msg.setNoop(new grpcModels.google.protobuf.Empty());
  return msg;
});

class StreamCall extends EventEmitter {
  constructor({ns, clientId}) {
    super()

    this._call = null;
    this._ns = ns;
    this._clientId = clientId;
    this._callEnded = false;
    this._cleanupEvents = noop;
  }

  get clientId() {
    return this._clientId;
  }

  get attached() {
    return !!this._call;
  }

  attach(call) {
    this.detach();

    const now = Date.now().toString();
    this._debug = d(`${ns}:${now.substr(now.length -6, 6)}`);

    const boundOnCallData = this._onCallData.bind(this);
    const boundOnCallEnd = this._onCallEnd.bind(this);
    this._call = call;
    this._callEnded = false;
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
    this._debug.log('Attached to the call stream');
  }

  sendNoop() {
    if (this._call) {
      this._call.write(noopMessage);
    }
  }

  send(grpcMessage) {
    if (!this._call) {
      const msg = 'Not attached yet, skip';
      this._debug.log(msg);
      throw new Error(msg);
    }

    this._call.write(grpcMessage);
  }

  detach() {
    if (!this._call) {
      return this._debug.log('Warn: not attached, end now.');
    }

    this._call = null;
    this._cleanupEvents();
    this.removeAllListeners();
    this._debug.log('Detached from the call stream');
  }

  get ended() {
    return this.attached && this._callEnded;
  }

  _onCallData(msg) {
    this.emit('message', msg);
  } 

  _onCallEnd(e) {
    if (e) {
      this._debug.error('Error on call stream, detach now.', e);
    }
    else {
      this._debug.log('The call stream ends, detach now.');
    }

    this._callEnded = true;
    this.detach();
  }
}

module.exports = StreamCall

