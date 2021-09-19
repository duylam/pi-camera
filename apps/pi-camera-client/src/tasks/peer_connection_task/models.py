from lib import RtcConnection

class CreateRtcConnectionRequest:
    def __init__(self, client_id: str):
        self._client_id = client_id

    @property
    def client_id(self) -> str:
        return self._client_id

class CreateRtcConnectionResponse:
    def __init__(self, client_id: str, pc: RtcConnection = None, sdp_offer: str = None, error_msg: str = None):
        self._pc = pc
        self._client_id = client_id
        self._sdp_offer = sdp_offer
        self._error_msg = error_msg

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def pc(self) -> RtcConnection:
        return self._pc

    @property
    def sdp_offer(self) -> str:
        return self._sdp_offer

    @property
    def error_msg(self) -> str:
        return self._error_msg

