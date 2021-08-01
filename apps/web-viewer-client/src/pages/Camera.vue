<template>
  <section class="section">
    <div class="level container">
      <div class="level-left">
        <div class="level-item">
          <button @click="connect" class="button" :class="{'is-loading': rtcConnectState === 'connecting'}">
            <span v-if="rtcConnectState === 'connected'">Re-join</span>
            <span v-else>Join</span>
          </button>
        </div>
        <div class="level-item">
          <font-awesome-icon icon="plug" size="2x" :class="{'has-text-grey-lighter': rtcConnectState !== 'connected'}" />
        </div>
        <div class="level-item">
          <span class="has-text-dark" v-if="rtcConnectState === 'disconnected'">Disconnected</span>
          <span class="has-text-dark" v-if="rtcConnectState === 'connecting'">Connecting</span>
          <span class="has-text-info" v-if="rtcConnectState === 'connected'">Connected</span>
        </div>
        <div class="level-item">
          <span v-if="rtcConnectError">Error on signaling process. Raw message: <span class="has-text-danger">{{ rtcConnectError }}</span></span>
        </div>
      </div>
    </div>
    <div class="container">
      <video style="background-color: #222" width="1200" hieght="900" ref="domVideoElement" playsinline autoplay muted></video>
    </div>
  </section>
</template>

<script>
import noop from 'lodash/noop';
import isEmpty from 'lodash/isEmpty';
import SignalingClient from '../lib/signaling-client';
import * as config from '../lib/config';
import d from '../lib/debug';

const clientId = Date.now();
const debugNs = `CameraPage-${clientId}`;
const peerConnectionConfiguration = {};

if (!isEmpty(config.WEBRTC_ICE_SERVER_URLS)) {
  peerConnectionConfiguration.iceServers = [{
    urls: config.WEBRTC_ICE_SERVER_URLS
  }];
}

export default {
  name: 'CameraPage',
  props: {
    msg: String
  },
  async created() {
    this._debug = d(debugNs);
    this._signalingClient = new SignalingClient(debugNs);
    this._peerConnection = null;

    try {
      await this._signalingClient.connect(clientId);
      const debug = d(`${debugNs}:on-signal-message`);
      this._signalingClient.on('message', this.onSignalingClientMessage.bind(this, debug));
    }
    catch (e) {
      this._debug.error('Fatal error', e);
    }
  },
  methods: {
    onSignalingClientMessage: async function (callDebug, incomingMsg) {
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
            const answerSessionDescription = await this._peerConnection.createAnswer();
            callDebug.log('Sending request.answer_offer');
            await this._signalingClient.sendAnswerOffer(answerSessionDescription.sdp);

            // Temporarily keep in peer connection
            this._peerConnection.__answer = answerSessionDescription;
          }
          else if (response.getAnswerOffer()) {
            callDebug.log('It .response.answer_offer');
            callDebug.log('Calling peer.setLocalDescription()');
            await this._peerConnection.setLocalDescription(this._peerConnection.__answer);
            delete this._peerConnection.__answer;
            callDebug.log('Sending request.confirm_answer');
            await this._signalingClient.sendConfirmAnswer();
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
        this.rtcConnectError = e.message;
        this.disconnect();
      }
    },
    disconnect: function () {
      if (this._peerConnection) {
        try {
          this._peerConnection.onicecandidate = noop;
          this._peerConnection.onconnectionstatechange = noop;
          this._peerConnection.ontrack = noop;
          this._peerConnection.close();
        }
        catch (e) {
          this._debug.error('Closing previous peer connection fails', e);
        }
        
        this.rtcConnectState = 'disconnected';

        // Reset video playing to receive new video stream
        this.$refs.domVideoElement.pause();
        this.$refs.domVideoElement.currentTime = 0;
      }
    },
    connect: async function() {
      const that = this;
      this.disconnect();
      this.rtcConnectError = '';
      this._peerConnection = new RTCPeerConnection(peerConnectionConfiguration);
      this._peerConnection.onicecandidate = async (e) => {
        // See https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnectionIceEvent
        this._debug.log('On peer icecandidate event', e);
        const candidate = e.candidate;
        if (candidate) {
          try {
            this._debug.log('Sending icecandidate', candidate);
            await this._signalingClient.sendIceCandidate(candidate);
          }
          catch (e) {
            this._debug.error('Sending icecandidate fails', e);
          }
        }
      };
      this._peerConnection.onconnectionstatechange = function () {
        that._debug.log(`On peer onconnectionstatechange: ${this.connectionState}`);
        switch(this.connectionState) {
          case 'connected':
            that.rtcConnectState = this.connectionState;
            break;
          case 'disconnected': case 'failed': case 'closed':
            that.rtcConnectState = 'disconnected';
            break;
        }
      };
      this._peerConnection.ontrack = (e) => {
        this._debug.log('On peer track');
        if (this.$refs.domVideoElement.srcObject !== e.streams[0]) {
          this.$refs.domVideoElement.srcObject = e.streams[0]
          this._debug.log('Added track to <video>');
        }
      };
      this._debug.log('Created peer connection and registered events');

      try {
        this._debug.log('Sending request.create_offer');
        this.rtcConnectState = 'connecting';
        await this._signalingClient.sendCreateOffer();
      }
      catch (e) {
        this._debug.error('request.create_offer fails', e);
        this.rtcConnectError = e.message;
        this.disconnect();
      }
    }
  },
  data: function () {
    return {
      rtcConnectState: 'disconnected', // enums: disconnected, connecting, connected
      rtcConnectError: ''
    }
  }
}

</script>
