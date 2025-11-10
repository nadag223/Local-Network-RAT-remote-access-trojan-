import socket
import struct


PORT_SCREEN = 9999
TIMEOUT_SEC = 10


class ScreenSocket:
    def __init__(self, ip: str, port: int = PORT_SCREEN):
        self.ip = ip
        self.port = port
        self.sock: socket.socket | None = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT_SEC)
        self.sock.connect((self.ip, self.port))
        # אחרי חיבור מוצלח אפשר להסיר timeout כדי לא להיתקע בחצי פריים
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
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def receive_frame(self) -> bytes | None:
        """
        פרוטוקול: תחילה 4 בתים big-endian של גודל, ואז payload של התמונה (bytes)
        """
        size_data = self._recv_exact(4)
        if not size_data:
            return None
        size = struct.unpack("!I", size_data)[0]
        return self._recv_exact(size)
