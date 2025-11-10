import socket
import struct


PORT_CAMERA = 9996
TIMEOUT_SEC = 10


class CameraSocket:
    def __init__(self, ip: str, port: int = PORT_CAMERA):
        self.ip = ip
        self.port = port
        self.sock: socket.socket | None = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT_SEC)
        self.sock.connect((self.ip, self.port))
        self.sock.settimeout(None)

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None

    def _recv_exact(self, size: int) -> bytes | None:
        data = b""
        while len(data) < size:
            part = self.sock.recv(size - len(data))
            if not part:
                return None
            data += part
        return data

    def receive_frame(self) -> bytes | None:
        """
        פרוטוקול: 4 בתים big-endian לגודל ואז payload של תמונה (bytes)
        """
        size_data = self._recv_exact(4)
        if not size_data:
            return None
        size = struct.unpack("!I", size_data)[0]
        return self._recv_exact(size)
