import EventEmitter from 'events';
import BPromise from 'bluebird';
import * as config from './config';
import d from './debug';
import noop from 'lodash/noop';
import grpcService from '../schema_node/rtc_signaling_service_grpc_web_pb';
import grpcModel from '../schema_node/rtc_signaling_service_pb';

const GOOGLE_EMPTY = new grpcModel.google.protobuf.Empty();

export default class SignalingClient extends EventEmitter {
  constructor(parentDebugNs) {
    super();

    this._parentDebugNs = parentDebugNs;
    this._grpcClient = new grpcService.RtcSignalingClient(config.GRPC_API_BASE_URL);
    this._callHeader = new grpcModel.CallHeader();
    this._debug = null;
    this._clientId = null;
    this._signalStream = null;
    this._boundOnSignalStreamMessage = (msg) => {
      if (msg.getNoop()) return;
      this.emit('message', msg);
    };
  }

  async connect(clientId) {
    this._debug = d(`${this._parentDebugNs}:signaling-client`);
    this._clientId = clientId.toString();
    this._callHeader.setClientId(this._clientId);

    const streamCall = await this._openStream(); 
    if (this._signalStream) {
      this._signalStream.removeListener('data', this._boundOnSignalStreamMessage);
    }

    this._signalStream = streamCall;
    this._signalStream.on('data', this._boundOnSignalStreamMessage);
  }

  async sendCreateOffer() {
    let cb = noop;
    const p = BPromise.fromCallback((_cb) => cb = _cb);
    this._grpcClient.sendMessage(this._getCreateOfferRequestMessage(), {}, cb);
    return p;
  }

  async sendConfirmAnswer() {
    let cb = noop;
    const p = BPromise.fromCallback((_cb) => cb = _cb);
    this._grpcClient.sendMessage(this._getConfirmAnwerRequestMessage(), {}, cb);
    return p;
  }

  async sendAnswerOffer(sdp) {
    let cb = noop;
    const p = BPromise.fromCallback((_cb) => cb = _cb);
    this._grpcClient.sendMessage(this._getAnswerOfferRequestMessage(sdp), {}, cb);
    return p;
  }

  async sendIceCandidate(iceCandidateObject) {
    const iceJson = iceCandidateObject.toJSON();
    let cb = noop;
    const p = BPromise.fromCallback((_cb) => cb = _cb);
    this._grpcClient.sendMessage(this._getIceCandidateRequestMessage(JSON.stringify(iceJson)), {}, cb);
    return p;
  }

  _getConfirmAnwerRequestMessage() {
    const request = new grpcModel.RtcSignalingMessage.Request();
    request.setCallHeader(this._callHeader);
    request.setConfirmAnswer(GOOGLE_EMPTY);
    const message = new grpcModel.RtcSignalingMessage();
    message.setRequest(request);
    return message;
  }
  _getAnswerOfferRequestMessage(val) {
    const request = new grpcModel.RtcSignalingMessage.Request();
    request.setCallHeader(this._callHeader);
    request.setAnswerOffer(val);
    const message = new grpcModel.RtcSignalingMessage();
    message.setRequest(request);
    return message;
  }

  _getCreateOfferRequestMessage() {
    const request = new grpcModel.RtcSignalingMessage.Request();
    request.setCallHeader(this._callHeader);
    request.setCreateOffer(GOOGLE_EMPTY);
    const message = new grpcModel.RtcSignalingMessage();
    message.setRequest(request);
    return message;
  }

  _getIceCandidateRequestMessage(val) {
    const request = new grpcModel.RtcSignalingMessage.Request();
    request.setCallHeader(this._callHeader);
    request.setIceCandidate(val);
    const message = new grpcModel.RtcSignalingMessage();
    message.setRequest(request);
    return message;
  }

  async _openStream() {
    let onFirstResponse = noop;
    const that = this;
    const waitForResponse = BPromise.fromCallback((cb) => onFirstResponse = cb);

    const subscribeIncomingMessageRequest = new grpcModel.SubscribeIncomingMessageRequest();
    subscribeIncomingMessageRequest.setCallHeader(this._callHeader);
    this._debug.log('Calling subscribeIncomingMessage()');
    const call = this._grpcClient.subscribeIncomingMessage(subscribeIncomingMessageRequest);
    const onSuccess = () => onFirstResponse();
    call.on('error', onError).on('data', onSuccess);        
    this._debug.log('Waiting stream confirmation');
    await waitForResponse;
    this._debug.log('Server confirms success');
    call.removeListener('data', onSuccess).removeListener('error', onError);        

    return call;

    function onError(e) {
      that._debug.error('Stream error', e);
      onFirstResponse(e);
    }
  }
}

