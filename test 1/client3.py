import socket
import struct
import threading
import tkinter.messagebox
import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import io

PORT_SCREEN = 9999
PORT_SHELL = 9998
PORT_CAMERA = 9996


class ScreenClientApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Remote Viewer - Client")
        self.root.geometry("900x700")

        self.connected_ip = None

        # Screen
        self.screen_socket = None
        self.screen_running = False
        self.screen_thread = None
        self.stream_visible = True

        # Shell
        self.shell_socket = None
        self.shell_running = False
        self.history = []
        self.history_index = -1

        # Camera
        self.camera_socket = None
        self.camera_running = False
        self.camera_thread = None
        self.show_camera = True

        self.build_ui()

    # ========================= UI ========================= #
    def build_ui(self):
        ip_row = ctk.CTkFrame(self.root)
        ip_row.pack(fill="x", pady=(10, 0), padx=10)

        self.ip_entry = ctk.CTkEntry(ip_row, placeholder_text="Server IP", width=280)
        self.ip_entry.pack(side="left", padx=(0, 10))

        self.remember_ip_btn = ctk.CTkButton(ip_row, text="💾 Save IP", command=self.remember_ip, fg_color="#3B82F6")
        self.remember_ip_btn.pack(side="left", padx=4)

        self.close_button = ctk.CTkButton(ip_row, text="❌", width=40, height=36,
                                          command=self.close_app, fg_color="#DC2626", hover_color="#B91C1C")
        self.close_button.pack(side="right")

        self.tabview = ctk.CTkTabview(self.root, width=860, height=580)
        self.tabview.pack(pady=10)

        self.screen_tab = self.tabview.add("🖥️ Screen")
        self.shell_tab = self.tabview.add("💻 Shell")
        self.camera_tab = self.tabview.add("📷 Camera")

        # ===== Screen =====
        top_frame = ctk.CTkFrame(self.screen_tab)
        top_frame.pack(fill="x", pady=(10, 8))

        self.btn_connect_screen = ctk.CTkButton(top_frame, text="✅ Connect", command=self.connect_screen,
                                                fg_color="#22C55E", hover_color="#16A34A")
        self.btn_connect_screen.pack(side="left", padx=6)

        self.btn_disconnect_screen = ctk.CTkButton(top_frame, text="❌ Disconnect",
                                                   command=self.disconnect_screen, state="disabled",
                                                   fg_color="#DC2626", hover_color="#B91C1C")
        self.btn_disconnect_screen.pack(side="left", padx=6)

        self.btn_toggle_stream = ctk.CTkButton(top_frame, text="🙈 Hide Stream",
                                               command=self.toggle_stream, state="disabled", fg_color="#6B7280",
                                               hover_color="#4B5563")
        self.btn_toggle_stream.pack(side="left", padx=6)

        self.status_screen = ctk.CTkLabel(top_frame, text="🔌 Disconnected", text_color="gray")
        self.status_screen.pack(side="right", padx=6)

        self.image_label = ctk.CTkLabel(self.screen_tab, text="Connect to view the screen")
        self.image_label.pack(pady=6)

        # ===== Shell =====
        sh_control = ctk.CTkFrame(self.shell_tab)
        sh_control.pack(fill="x", pady=(10, 8))

        self.btn_connect_shell = ctk.CTkButton(sh_control, text="✅ Connect", command=self.connect_shell,
                                               fg_color="#22C55E", hover_color="#16A34A")
        self.btn_connect_shell.pack(side="left", padx=6)

        self.btn_disconnect_shell = ctk.CTkButton(sh_control, text="❌ Disconnect",
                                                  command=self.disconnect_shell, state="disabled",
                                                  fg_color="#DC2626", hover_color="#B91C1C")
        self.btn_disconnect_shell.pack(side="left", padx=6)

        self.clear_button = ctk.CTkButton(sh_control, text="🧹 Clear Output", command=self.clear_output,
                                          fg_color="#3B82F6")
        self.clear_button.pack(side="left", padx=6)

        self.status_shell = ctk.CTkLabel(sh_control, text="🔌 Disconnected", text_color="gray")
        self.status_shell.pack(side="right", padx=6)

        self.command_entry = ctk.CTkEntry(self.shell_tab, placeholder_text="Type a command...", width=700)
        self.command_entry.pack(pady=6)
        self.command_entry.bind("<Up>", self.prev_command)
        self.command_entry.bind("<Down>", self.next_command)
        self.command_entry.bind("<Return>", self.run_command_enter)

        self.command_button = ctk.CTkButton(self.shell_tab, text="📤 Send Command", command=self.send_command,
                                            state="disabled", fg_color="#2563EB", hover_color="#1D4ED8")
        self.command_button.pack(pady=4)

        self.shell_output = ctk.CTkTextbox(self.shell_tab, width=820, height=360)
        self.shell_output.pack(pady=6)

        # ===== Camera =====
        cam_control = ctk.CTkFrame(self.camera_tab)
        cam_control.pack(fill="x", pady=(10, 8))

        self.btn_connect_camera = ctk.CTkButton(cam_control, text="✅ Connect", command=self.connect_camera,
                                                fg_color="#22C55E", hover_color="#16A34A")
        self.btn_connect_camera.pack(side="left", padx=6)

        self.btn_disconnect_camera = ctk.CTkButton(cam_control, text="❌ Disconnect",
                                                   command=self.disconnect_camera, state="disabled",
                                                   fg_color="#DC2626", hover_color="#B91C1C")
        self.btn_disconnect_camera.pack(side="left", padx=6)

        self.camera_toggle_button = ctk.CTkButton(cam_control, text="🙈 Hide Camera",
                                                  command=self.toggle_camera, state="disabled", fg_color="#6B7280",
                                                  hover_color="#4B5563")
        self.camera_toggle_button.pack(side="left", padx=6)

        self.status_camera = ctk.CTkLabel(cam_control, text="🔌 Disconnected", text_color="gray")
        self.status_camera.pack(side="right", padx=6)

        self.camera_label = ctk.CTkLabel(self.camera_tab, text="Connect to view the camera")
        self.camera_label.pack(pady=6)

    # ========================= IP helper ========================= #
    def remember_ip(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            tkinter.messagebox.showerror("Error", "Enter IP address")
            return
        self.connected_ip = ip
        tkinter.messagebox.showinfo("IP Saved", f"Server IP set to {ip}")

    def require_ip(self):
        if not self.connected_ip:
            ip = self.ip_entry.get().strip()
            if not ip:
                tkinter.messagebox.showerror("Error", "Enter IP address")
                return None
            self.connected_ip = ip
        return self.connected_ip

    # ========================= Screen ========================= #
    def connect_screen(self):
        if self.screen_running:
            return
        ip = self.require_ip()
        if not ip:
            return
        try:
            self.screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.screen_socket.connect((ip, PORT_SCREEN))
            self.screen_running = True
            self.status_screen.configure(text=f"🟢 Connected to Screen ({ip})", text_color="green")
            self.btn_connect_screen.configure(state="disabled")
            self.btn_disconnect_screen.configure(state="normal")
            self.btn_toggle_stream.configure(state="normal")

            self.screen_thread = threading.Thread(target=self.receive_frames, daemon=True)
            self.screen_thread.start()
        except Exception as e:
            self.status_screen.configure(text=f"❌ Screen connection error: {e}", text_color="red")
            self.disconnect_screen()

    def receive_frames(self):
        try:
            while self.screen_running:
                size_data = self.recv_exact(self.screen_socket, 4)
                if not size_data:
                    break
                size = struct.unpack("!I", size_data)[0]
                frame_data = self.recv_exact(self.screen_socket, size)
                if not frame_data:
                    break
                if self.stream_visible:
                    self.root.after(0, self._update_screen_image_from_bytes, frame_data)
        except Exception as e:
            print(f"[SCREEN STREAM ERROR] {e}")
        finally:
            self.root.after(0, self.disconnect_screen)

    def _update_screen_image_from_bytes(self, data):
        try:
            img = Image.open(io.BytesIO(data))
            ctk_img = CTkImage(light_image=img, dark_image=img, size=(800, 450))
            self.image_label.configure(image=ctk_img, text="")
            self.image_label.image = ctk_img
        except Exception:
            pass

    def toggle_stream(self):
        self.stream_visible = not self.stream_visible
        self.btn_toggle_stream.configure(text="🙈 Hide Stream" if self.stream_visible else "👁️ Show Stream")
        if not self.stream_visible:
            self.image_label.configure(image="", text="Stream hidden")
            self.image_label.image = None

    def disconnect_screen(self):
        if not self.screen_running and not self.screen_socket:
            return
        self.screen_running = False
        if self.screen_socket:
            try:
                self.screen_socket.close()
            except:
                pass
            self.screen_socket = None

        self.status_screen.configure(text="🔌 Disconnected", text_color="gray")
        self.btn_connect_screen.configure(state="normal")
        self.btn_disconnect_screen.configure(state="disabled")
        self.btn_toggle_stream.configure(state="disabled")
        self.image_label.configure(image="", text="Disconnected")
        self.image_label.image = None

    # ========================= Shell ========================= #
    def connect_shell(self):
        if self.shell_running:
            return
        ip = self.require_ip()
        if not ip:
            return
        try:
            self.shell_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.shell_socket.connect((ip, PORT_SHELL))
            self.shell_running = True
            self.status_shell.configure(text=f"🟢 Connected to Shell ({ip})", text_color="green")
            self.btn_connect_shell.configure(state="disabled")
            self.btn_disconnect_shell.configure(state="normal")
            self.command_button.configure(state="normal")
        except Exception as e:
            self.status_shell.configure(text=f"❌ Shell connection error: {e}", text_color="red")
            self.disconnect_shell()

    def send_command(self):
        if not self.shell_running or not self.shell_socket:
            return
        cmd = self.command_entry.get().strip()
        if not cmd:
            return
        try:
            self.history.append(cmd)
            self.history_index = len(self.history)
            self.command_entry.delete(0, "end")
            self.shell_socket.sendall(cmd.encode("utf-8") + b"\n")

            response = b""
            while True:
                part = self.shell_socket.recv(2048)
                if not part:
                    raise Exception("Disconnected from server")
                response += part
                if b"<END>" in response:
                    break

            text = response.replace(b"<END>", b"").decode(errors="ignore")
            self.shell_output.insert("end", f"$ {cmd}\n{text}\n")
            self.shell_output.see("end")
        except Exception as e:
            self.shell_output.insert("end", f"[Send Error] {e}\n")
            self.shell_output.see("end")
            self.disconnect_shell()

    def clear_output(self):
        self.shell_output.delete("1.0", "end")

    def prev_command(self, event):
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.history[self.history_index])

    def next_command(self, event):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.history[self.history_index])
        else:
            self.command_entry.delete(0, "end")
            self.history_index = len(self.history)

    def disconnect_shell(self):
        if not self.shell_running and not self.shell_socket:
            return
        self.shell_running = False
        if self.shell_socket:
            try:
                self.shell_socket.close()
            except:
                pass
            self.shell_socket = None

        self.status_shell.configure(text="🔌 Disconnected", text_color="gray")
        self.btn_connect_shell.configure(state="normal")
        self.btn_disconnect_shell.configure(state="disabled")
        self.command_button.configure(state="disabled")

    # ========================= Camera ========================= #
    def connect_camera(self):
        if self.camera_running:
            return
        ip = self.require_ip()
        if not ip:
            return
        try:
            self.camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.camera_socket.connect((ip, PORT_CAMERA))
            self.camera_running = True

            self.status_camera.configure(text=f"🟢 Connected to Camera ({ip})", text_color="green")
            self.btn_connect_camera.configure(state="disabled")
            self.btn_disconnect_camera.configure(state="normal")
            self.camera_toggle_button.configure(state="normal")

            self.camera_thread = threading.Thread(target=self.receive_camera, daemon=True)
            self.camera_thread.start()
        except Exception as e:
            self.status_camera.configure(text=f"❌ Camera connection error: {e}", text_color="red")
            self.disconnect_camera()

    def receive_camera(self):
        try:
            while self.camera_running:
                size_data = self.recv_exact(self.camera_socket, 4)
                if not size_data:
                    break
                size = struct.unpack("!I", size_data)[0]
                img_data = self.recv_exact(self.camera_socket, size)
                if not img_data:
                    break
                if self.show_camera:
                    self.root.after(0, self._update_camera_image_from_bytes, img_data)
                else:
                    self.root.after(0, self._hide_camera_image)
        except Exception as e:
            print(f"[CAMERA STREAM ERROR] {e}")
        finally:
            self.root.after(0, self.disconnect_camera)

    def _update_camera_image_from_bytes(self, data):
        try:
            img = Image.open(io.BytesIO(data))
            ctk_img = CTkImage(light_image=img, dark_image=img, size=(800, 450))
            self.camera_label.configure(image=ctk_img, text="")
            self.camera_label.image = ctk_img
        except Exception:
            pass

    def _hide_camera_image(self):
        self.camera_label.configure(image="", text="Camera hidden")
        self.camera_label.image = None

    def toggle_camera(self):
        self.show_camera = not self.show_camera
        self.camera_toggle_button.configure(text="🙈 Hide Camera" if self.show_camera else "👁️ Show Camera")
        if not self.show_camera:
            self._hide_camera_image()

    def disconnect_camera(self):
        if not self.camera_running and not self.camera_socket:
            return
        self.camera_running = False
        if self.camera_socket:
            try:
                self.camera_socket.close()
            except:
                pass
            self.camera_socket = None

        self.status_camera.configure(text="🔌 Disconnected", text_color="gray")
        self.btn_connect_camera.configure(state="normal")
        self.btn_disconnect_camera.configure(state="disabled")
        self.camera_toggle_button.configure(state="disabled")
        self._hide_camera_image()

    # ========================= Helpers ========================= #
    def recv_exact(self, sock, size):
        data = b""
        try:
            while len(data) < size:
                part = sock.recv(size - len(data))
                if not part:
                    return None
                data += part
        except Exception:
            return None
        return data

    def run_command_enter(self, event):
        self.send_command()

    # ========================= App lifecycle ========================= #
    def run(self):
        self.root.mainloop()

    def close_app(self):
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
        self.root.destroy()

if __name__ == "__main__":
    app = ScreenClientApp()
    app.run()
