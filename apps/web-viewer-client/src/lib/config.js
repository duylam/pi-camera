// A comma-delimited array of urls for ICE servers (TURN or STUN)
// See https://developer.mozilla.org/en-US/docs/Web/API/RTCIceServer
export const WEBRTC_ICE_SERVER_URLS =
  (process.env.VUE_APP_WEBRTC_ICE_SERVER_URLS || 'stun:stun.stunprotocol.org:3478').split(',').filter(u => !!u);
export const GRPC_API_BASE_URL = process.env.VUE_APP_GRPC_API_BASE_URL || 'http://localhost:4001';

