<template>
  <div>
    Env: {{ env1 }}<br />
    <button v-on:click="start">Start/Restart</button><br />
    <video width="300" hieght="100" ref="domVideoElement" playsinline autoplay></video>
    Remote video width: {{ remoteVideoWidth }}px<br/>
    Remote video height: {{ remoteVideoHeight }}px<br/>
  </div>
</template>

<script>
import $ from 'lodash';
import BPromise from 'bluebird';

import * as config from '../lib/config';
import d from '../lib/debug';
import grpcService from '../schema_node/rtc_signaling_service_grpc_web_pb';
import grpcModel from '../schema_node/rtc_signaling_service_pb';

const GOOGLE_EMPTY =  new grpcModel.google.protobuf.Empty();
const callHeader = new grpcModel.CallHeader();
callHeader.setClientId(Date.now().toString());

export default {
  name: 'HelloWorld',
  props: {
    msg: String
  },
  async mounted() {
    const that = this;
    this.$refs.domVideoElement.addEventListener('loadedmetadata', function() {
      that.remoteVideoWidth = this.videoWidth;
      that.remoteVideocHeight = this.videoHeight;
    });

    this._grpcClient = new grpcService.RtcSignalingClient(config.GRPC_API_BASE_URL);
    this._debug = d('web');
  },
  methods: {
    start: async function() {
      const configuration = {};
      if (!$.isEmpty(config.WEBRTC_ICE_SERVER_URLS)) {
        configuration.iceServers = [{
          urls: config.WEBRTC_ICE_SERVER_URLS
        }];
      }

      if (this._peerConnection) {
        try {
          this._peerConnection.close();
        }
        catch (e) {
          this._debug.error('Closing previous peer connection fails', e);
        }
      }

      if (this._signalStream) {
        try {
          this._signalStream.destroy();
        }
        catch (e) {
          this._debug.error('Closing previouse call subscribeIncomingMessage() fails', e);
        }
      }

      this._peerConnection = new RTCPeerConnection(configuration);
      this._peerConnection.onicecandidate = (e) => {
        // See https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnectionIceEvent
        this._debug.log('On peer icecandidate event', e);
        if (e.candidate) {
          const iceJson = e.candidate.toJSON();
          this._debug.log('Sending .request.ice_candidate', iceJson);
          this._grpcClient.sendMessage(getIceCandidateRequestMessage(JSON.stringify(iceJson)), {}, (e) => {
            if (e) this._debug.error(e);
          });
        }
      };
      this._peerConnection.oniceconnectionstatechange = () => {
        this._debug.log('On peer iceconnectionstatechange');
        this._debug.log(`connection.iceConnectionState=${this._peerConnection.iceConnectionState}`);
      };
      this._peerConnection.ontrack = (e) => {
        this._debug.log('On peer track');
        if (this.$refs.domVideoElement.srcObject !== e.streams[0]) {
          this.$refs.domVideoElement.srcObject = e.streams[0]
          this._debug.log('Added track to <video>');
        }
      };
      this._debug.log('Created peer connection and registered events');

      const callDebug = d(`${this._debug.ns}:subscribeIncomingMessage`);
      let answerSessionDescription;
      try {
        callDebug.log('Opening stream');
        const subscribeIncomingMessageRequest = new grpcModel.SubscribeIncomingMessageRequest();
        subscribeIncomingMessageRequest.setCallHeader(callHeader);
        const call = this._grpcClient.subscribeIncomingMessage(subscribeIncomingMessageRequest);
        let onSuccess;
        call.on('end', function () {
          callDebug.log('Call ends');
        });
        call.on('error', function (e) {
          callDebug.error('Call error', e);
          onSuccess(e);
        });

        const waitSuccess = BPromise.fromCallback((cb) => onSuccess = cb);
        const onDataHandler = () => onSuccess();
        call.on('data', onDataHandler);        
        callDebug.log('Waiting success confirmation from server');
        await waitSuccess;
        callDebug.log('Server confirms success');
        call.removeListener('data', onDataHandler);        
        this._signalStream = call;

        call.on('data', async (incomingMsg) => {
          if (incomingMsg.getNoop()) return;

          callDebug.log('Received incoming message');

          try {
            if (incomingMsg.getResponse()) {
              callDebug.log('It .response');
              const response = incomingMsg.getResponse();

              if (response.getError()) throw Error(response.getError().getErrorMessage());

              if (response.getCreateOffer()) {
                callDebug.log('It .response.create_offer');
                callDebug.log('Calling peer.setRemoteDescription()');
                await this._peerConnection.setRemoteDescription({
                  type: 'offer',
                  sdp: response.getCreateOffer()
                });

                callDebug.log('Calling peer.createAnswer()');
                answerSessionDescription = await this._peerConnection.createAnswer();
                callDebug.log('Sending request.answer_offer');
                await BPromise.fromCallback((cb) => this._grpcClient.sendMessage(getAnswerOfferRequestMessage(answerSessionDescription.sdp), {}, cb));
              }
              else if (response.getAnswerOffer()) {
                callDebug.log('It .response.answer_offer');
                callDebug.log('Calling peer.setLocalDescription()');
                await this._peerConnection.setLocalDescription(answerSessionDescription);
                callDebug.log('Sending request.confirm_answer');
                await BPromise.fromCallback((cb) => this._grpcClient.sendMessage(getConfirmAnwerRequestMessage(), {}, cb));
                callDebug.log('Completed peer handshaking!');
              }
              else {
                callDebug.log('Unhandled message');
              }
            }
            else if (incomingMsg.getRequest()) {
              callDebug.log('It .request');
              const request = incomingMsg.getRequest();

              if (request.getIceCandidate()) {
                callDebug.log('It .request.ice_candidate');
                callDebug.log('peer.addIceCandidate()');
                await this._peerConnection.addIceCandidate(JSON.parse(request.getIceCandidate()));
              }
            }
          }
          catch (e) {
            callDebug.error('Error on handling incoming message', e);
          }
        });

        this._debug.log('Sending request.create_offer');
        await BPromise.fromCallback((cb) => this._grpcClient.sendMessage(getCreateOfferRequestMessage(), {}, cb));
      }
      catch (e) {
        callDebug.error('Fatal error', e);
      }
    }
  },
  data: function () {
    return {
      env1: config.WEBRTC_ICE_SERVER_URLS,
      remoteVideoWidth: 0,
      remoteVideoHeight: 0
    }
  }
}

function getCreateOfferRequestMessage() {
  const request = new grpcModel.RtcSignalingMessage.Request();
  request.setCallHeader(callHeader);
  request.setCreateOffer(GOOGLE_EMPTY);
  const message = new grpcModel.RtcSignalingMessage();
  message.setRequest(request);
  return message;
}

function getIceCandidateRequestMessage(val) {
  const request = new grpcModel.RtcSignalingMessage.Request();
  request.setCallHeader(callHeader);
  request.setIceCandidate(val);
  const message = new grpcModel.RtcSignalingMessage();
  message.setRequest(request);
  return message;
}

function getAnswerOfferRequestMessage(val) {
  const request = new grpcModel.RtcSignalingMessage.Request();
  request.setCallHeader(callHeader);
  request.setAnswerOffer(val);
  const message = new grpcModel.RtcSignalingMessage();
  message.setRequest(request);
  return message;
}

function getConfirmAnwerRequestMessage() {
  const request = new grpcModel.RtcSignalingMessage.Request();
  request.setCallHeader(callHeader);
  request.setConfirmAnswer(GOOGLE_EMPTY);
  const message = new grpcModel.RtcSignalingMessage();
  message.setRequest(request);
  return message;
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
