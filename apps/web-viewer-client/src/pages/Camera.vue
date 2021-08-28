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
      <video style="background-color: #222" width="900" height="700" ref="domVideoElement" playsinline autoplay muted></video>
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
            await this._peerConnection.setLocalDescription(answerSessionDescription);
          }
          else if (response.getAnswerOffer()) {
            callDebug.log('It .response.answer_offer');
            callDebug.log('Sending request.confirm_answer');
            await this._signalingClient.sendConfirmAnswer();
            callDebug.log('Completed peer handshaking!');
          }
          else {
            callDebug.log('Unhandled message');
          }
        }
        else if (incomingMsg.getRequest()) {
          callDebug.log('It .request but not handling now');
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
          this._peerConnection.onicecandidateerror = noop;
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
      this._debug.log('Created peer connection');

      // See https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/icecandidate_event#indicating_the_end_of_a_generation_of_candidates
      this._peerConnection.onicecandidate = async (e) => {
        // See https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnectionIceEvent
        this._debug.log('On peer "icecandidate" event', e);
        const candidate = e.candidate;
        if (!candidate) {
          // The aiortc library in pi-client hasn't supported ICE negotiation process, so the pi-client
          // can't send back ICE candidate for establishing connection. Per the trick at
          // https://stackoverflow.com/a/38533347, we will send full candidate for web-viewer at 
          // end of ICE negotiation process so that pi-client has all candidates to reach to this web-viewer
          this._debug.log('ICE negotiation completes. Sending request.answer_offer');
          await this._signalingClient.sendAnswerOffer(this._peerConnection.localDescription.sdp);
        }
      };
      this._peerConnection.onconnectionstatechange = function () {
        that._debug.log(`On peer "onconnectionstatechange" event: ${this.connectionState}`);
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
        this._debug.log('On peer "track" event');
        if (this.$refs.domVideoElement.srcObject !== e.streams[0]) {
          this.$refs.domVideoElement.srcObject = e.streams[0]
          this._debug.log('Added track to <video>');
        }
      };
      this._peerConnection.onicecandidateerror = (e) => {
        this._debug.error('On peer "onicecandidateerror" event');
        if (e.errorCode >= 300 && e.errorCode <= 699) {
          // STUN errors are in the range 300-699. See RFC 5389, section 15.6
          // for a list of codes. TURN adds a few more error codes; see
          // RFC 5766, section 15 for details.
          this._debug.error('TURN and STUN protocol error', e);
        } else if (e.errorCode >= 700 && e.errorCode <= 799) {
          // Server could not be reached; a specific error number is
          // provided but these are not yet specified.
          this._debug.error('TURN and STUN server error', e);
        }
        else {
          this._debug.error('Unknown error code', e);
        }
      };
      this._debug.log('Registered events on peer connection');

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

