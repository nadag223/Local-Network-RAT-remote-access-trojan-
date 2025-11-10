import socket


PORT_SHELL = 9998
TIMEOUT_SEC = 10


class ShellSocket:
    def __init__(self, ip: str, port: int = PORT_SHELL):
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

    def send_line(self, line: str):
        if not self.sock:
            raise RuntimeError("Shell socket not connected")
        self.sock.sendall(line.encode("utf-8") + b"\n")

    def recv_until_delimiter(self, delimiter: bytes) -> bytes:
        """
        קורא עד שנמצא delimiter (לדוגמה: b"<END>") או שהתנתק.
        """
        if not self.sock:
            raise RuntimeError("Shell socket not connected")
        buf = b""
        while True:
            part = self.sock.recv(2048)
            if not part:
                raise ConnectionError("Disconnected from server")
            buf += part
            if delimiter in buf:
                buf = buf.replace(delimiter, b"")
                return buf
