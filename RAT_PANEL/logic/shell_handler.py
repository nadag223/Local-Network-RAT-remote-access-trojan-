from RAT_PANEL.network.shell_socket import ShellSocket


class ShellHandler:
    def __init__(self, logic):
        self.logic = logic
        self.ui = logic.ui
        self.socket = None
        self.running = False

    def connect(self, ip: str):
        self.socket = ShellSocket(ip)
        self.socket.connect()
        self.running = True

    def send_and_receive(self, cmd: str) -> str:
        if not self.running:
            raise RuntimeError("Shell is not connected")
        self.socket.send_line(cmd)
        data = self.socket.recv_until_delimiter(b"<END>")
        text = data.decode(errors="ignore")
        return text

    def stop(self):
        self.running = False
        if self.socket:
            try:
                self.socket.disconnect()
            except Exception:
                pass
            self.socket = None
