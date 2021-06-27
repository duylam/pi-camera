<template>
  <div>
    Env: {{ env1 }}<br />
    <button v-on:click="start">Start/Restart</button><br />
    <video ref="domVideoElement" playsinline autoplay></video>
    Remote video width: {{ remoteVideoWidth }}px<br/>
    Remote video height: {{ remoteVideoHeight }}px<br/>
    <p>
      Logs<br />
      <textarea ref="logTextArea"></textarea>
    </p>
  </div>
</template>

<script>
import * as config from '../lib/config';
import $ from 'lodash';

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
  },
  methods: {
    log: function(msg) {
      this.$refs.logTextArea.value = this.$refs.logTextArea.value + msg + '\n';
    },
    start: async function() {
      const that = this;
      const configuration = {};
      if (!$.isEmpty(config.WEBRTC_ICE_SERVER_URLS)) {
        configuration.iceServers = [{
          urls: config.WEBRTC_ICE_SERVER_URLS
        }];
      }

      if (this.peerConnection) {
        this.peerConnection.close();
      }

      this.peerConnection = new RTCPeerConnection(configuration);
      this.log('Created peer cnnection object');

      this.peerConnection.addEventListener('icecandidate', function(e) {
        that.log('On icecandidate event: addIceCandidate success');
        that.log(`On icecandidate event: ${e.candidate ? e.candidate.candidate : '(null)'}`);
      });
      this.log('Registered "icecandidate" event on peer cnnection');

      this.peerConnection.addEventListener('iceconnectionstatechange', function(e) {
        that.log(`On iceconnectionstatechange event: ICE state: ${that.peerConnection.iceConnectionState}`);
        that.log(`On iceconnectionstatechange event: ICE state change event: ${e}`);
      });
      this.log('Registered "iceconnectionstatechange" event on peer cnnection');

      this.peerConnection.addEventListener('track', function(e) {
        if (that.$refs.domVideoElement.srcObject !== e.streams[0]) {
          that.$refs.domVideoElement.srcObject = e.streams[0]
          that.log('PeerCon received remote stream');
        }
      });
      this.log('Registered "track" event on peer cnnection');

      try {
        const reqOption = {params: {cid: Date.now()}};
        const response = await this.$http.post('offer', reqOption);
        await this.peerConnection.setRemoteDescription(response.body);

        const localOffer = await this.peerConnection.createOffer({offerToReceiveAudio: false, voiceActivityDetection: false});
        await this.peerConnection.setLocalDescription(localOffer);
        await this.$http.post('answer', this.peerConnection.localDescription.sdp, reqOption);
        await this.$http.put('answer', reqOption);
      }
      catch (e) {
          this.log('Error on sending offer');
          this.log(e.message);
      }

      // Set remote offer to peer: role for signaling
      // https://github.com/webrtc/samples/blob/gh-pages/src/content/peerconnection/pc1/index.html
      // https://github.com/node-webrtc/node-webrtc-examples/blob/master/examples/viewer/client.js
    }
  },
  data: function () {
    return {
      env1: config.WEBRTC_ICE_SERVER_URLS,
      remoteVideoWidth: 0,
      remoteVideoHeight: 0,
      peerConnection: null
    }
  }
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
