<template>
  <section class="section">
    <div class="level container">
      <div class="level-left">
        <div class="level-item">
          <button @click="start" class="button">Join</button>
        </div>
        <div class="level-item">
          <font-awesome-icon icon="plug" size="2x" /><br />
          <font-awesome-icon icon="plug" size="2x" class="has-text-grey-lighter" /><br />
        </div>
        <div class="level-item">
          <span class="has-text-dark">status</span>
        </div>
      </div>
    </div>
    <div class="container">
      <video style="background-color: #222" width="1200" hieght="900" ref="domVideoElement" playsinline autoplay muted></video>
    </div>
  </section>
</template>

<script>
import $ from 'lodash';
import SignalingClient from '../lib/signaling-client';
import * as config from '../lib/config';
import d from '../lib/debug';

const clientId = Date.now();
const debugNs = `CameraPage-${clientId}`;
const peerConnectionConfiguration = {};

if (!$.isEmpty(config.WEBRTC_ICE_SERVER_URLS)) {
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
  async mounted() {
    const that = this;
    this.$refs.domVideoElement.addEventListener('loadedmetadata', function() {
      that.remoteVideoWidth = this.videoWidth;
      that.remoteVideocHeight = this.videoHeight;
    });
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
      }
    },
    start: async function() {
      if (this._peerConnection) {
        try {
          this._peerConnection.close();
        }
        catch (e) {
          this._debug.error('Closing previous peer connection fails', e);
        }
      }

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

      try {
        this._debug.log('Sending request.create_offer');
        await this._signalingClient.sendCreateOffer();
      }
      catch (e) {
        this._debug.error('request.create_offer fails', e);
      }
    }
  },
  data: function () {
    return {
      remoteVideoWidth: 0,
      remoteVideoHeight: 0
    }
  }
}

</script>

