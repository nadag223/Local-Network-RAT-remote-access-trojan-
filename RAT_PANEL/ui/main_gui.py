import customtkinter as ctk
import tkinter.messagebox


class ClientAppUI:
    """
    UI בלבד: בונה את הממשק ויודע לקרוא לפונקציות בלוגיקה (logic).
    אין כאן סוקטים או חוטי ביצוע, רק עיצוב וקריאות ל-logic.
    """
    def __init__(self, logic):
        self.logic = logic

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Remote Viewer - Client")
        self.root.geometry("900x700")

        self._build_ui()

        # סגירת אפליקציה מסודרת
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ========================= Build UI ========================= #
    def _build_ui(self):
        # שורת IP + שמירה + סגירה
        ip_row = ctk.CTkFrame(self.root)
        ip_row.pack(fill="x", pady=(10, 0), padx=10)

        self.ip_entry = ctk.CTkEntry(ip_row, placeholder_text="Server IP", width=280)
        self.ip_entry.pack(side="left", padx=(0, 10))

        remember_ip_btn = ctk.CTkButton(
            ip_row, text="💾 Save IP",
            command=lambda: self.logic.remember_ip(self.ip_entry.get().strip()),
            fg_color="#3B82F6"
        )
        remember_ip_btn.pack(side="left", padx=4)


        close_button = ctk.CTkButton(
            ip_row, text="❌", width=40, height=36,
            command=self._on_close, fg_color="#DC2626", hover_color="#B91C1C"
        )
        close_button.pack(side="right")

        # טאבים
        self.tabview = ctk.CTkTabview(self.root, width=860, height=580)
        self.tabview.pack(pady=10)

        self.screen_tab = self.tabview.add("🖥️ Screen")
        self.shell_tab = self.tabview.add("💻 Shell")
        self.camera_tab = self.tabview.add("📷 Camera")

        # ===== Screen =====
        top_frame = ctk.CTkFrame(self.screen_tab)
        top_frame.pack(fill="x", pady=(10, 8))

        self.btn_connect_screen = ctk.CTkButton(
            top_frame, text="✅ Connect",
            command=self.logic.connect_screen,
            fg_color="#22C55E", hover_color="#16A34A"
        )
        self.btn_connect_screen.pack(side="left", padx=6)

        self.btn_disconnect_screen = ctk.CTkButton(
            top_frame, text="❌ Disconnect",
            command=self.logic.disconnect_screen, state="disabled",
            fg_color="#DC2626", hover_color="#B91C1C"
        )
        self.btn_disconnect_screen.pack(side="left", padx=6)

        self.btn_toggle_stream = ctk.CTkButton(
            top_frame, text="🙈 Hide Stream",
            command=self.logic.toggle_stream, state="disabled",
            fg_color="#6B7280", hover_color="#4B5563"
        )
        self.btn_toggle_stream.pack(side="left", padx=6)

        self.status_screen = ctk.CTkLabel(top_frame, text="🔌 Disconnected", text_color="gray")
        self.status_screen.pack(side="right", padx=6)

        self.image_label = ctk.CTkLabel(self.screen_tab, text="Connect to view the screen")
        self.image_label.pack(pady=6)

        # ===== Shell =====
        sh_control = ctk.CTkFrame(self.shell_tab)
        sh_control.pack(fill="x", pady=(10, 8))

        self.btn_connect_shell = ctk.CTkButton(
            sh_control, text="✅ Connect",
            command=self.logic.connect_shell,
            fg_color="#22C55E", hover_color="#16A34A"
        )
        self.btn_connect_shell.pack(side="left", padx=6)

        self.btn_disconnect_shell = ctk.CTkButton(
            sh_control, text="❌ Disconnect",
            command=self.logic.disconnect_shell, state="disabled",
            fg_color="#DC2626", hover_color="#B91C1C"
        )
        self.btn_disconnect_shell.pack(side="left", padx=6)

        clear_button = ctk.CTkButton(
            sh_control, text="🧹 Clear Output",
            command=self.logic.clear_output, fg_color="#3B82F6"
        )
        clear_button.pack(side="left", padx=6)

        self.status_shell = ctk.CTkLabel(sh_control, text="🔌 Disconnected", text_color="gray")
        self.status_shell.pack(side="right", padx=6)

        self.command_entry = ctk.CTkEntry(self.shell_tab, placeholder_text="Type a command...", width=700)
        self.command_entry.pack(pady=6)
        self.command_entry.bind("<Up>", self.logic.prev_command)
        self.command_entry.bind("<Down>", self.logic.next_command)
        self.command_entry.bind("<Return>", self.logic.run_command_enter)

        self.command_button = ctk.CTkButton(
            self.shell_tab, text="📤 Send Command",
            command=self.logic.send_command, state="disabled",
            fg_color="#2563EB", hover_color="#1D4ED8"
        )
        self.command_button.pack(pady=4)

        self.shell_output = ctk.CTkTextbox(self.shell_tab, width=820, height=360)
        self.shell_output.pack(pady=6)

        # ===== Camera =====
        cam_control = ctk.CTkFrame(self.camera_tab)
        cam_control.pack(fill="x", pady=(10, 8))

        self.btn_connect_camera = ctk.CTkButton(
            cam_control, text="✅ Connect",
            command=self.logic.connect_camera,
            fg_color="#22C55E", hover_color="#16A34A"
        )
        self.btn_connect_camera.pack(side="left", padx=6)

        self.btn_disconnect_camera = ctk.CTkButton(
            cam_control, text="❌ Disconnect",
            command=self.logic.disconnect_camera, state="disabled",
            fg_color="#DC2626", hover_color="#B91C1C"
        )
        self.btn_disconnect_camera.pack(side="left", padx=6)

        self.camera_toggle_button = ctk.CTkButton(
            cam_control, text="🙈 Hide Camera",
            command=self.logic.toggle_camera, state="disabled",
            fg_color="#6B7280", hover_color="#4B5563"
        )
        self.camera_toggle_button.pack(side="left", padx=6)

        self.status_camera = ctk.CTkLabel(cam_control, text="🔌 Disconnected", text_color="gray")
        self.status_camera.pack(side="right", padx=6)

        self.camera_label = ctk.CTkLabel(self.camera_tab, text="Connect to view the camera")
        self.camera_label.pack(pady=6)

    # ========================= UI update APIs (נקראות מה-logic/handlers) ========================= #
    def set_ip_entry(self, value: str):
        self.ip_entry.delete(0, "end")
        self.ip_entry.insert(0, value)

    # --- Screen ---
    def screen_set_status(self, text: str, color: str):
        self.status_screen.configure(text=text, text_color=color)

    def screen_set_buttons(self, connected: bool):
        self.btn_connect_screen.configure(state="disabled" if connected else "normal")
        self.btn_disconnect_screen.configure(state="normal" if connected else "disabled")
        self.btn_toggle_stream.configure(state="normal" if connected else "disabled")

    def screen_set_image(self, ctk_img):
        self.image_label.configure(image=ctk_img, text="")
        self.image_label.image = ctk_img

    def screen_clear_image(self, message="Disconnected"):
        self.image_label.configure(image="", text=message)
        self.image_label.image = None

    def screen_toggle_button_text(self, show: bool):
        self.btn_toggle_stream.configure(text="🙈 Hide Stream" if show else "👁️ Show Stream")

    # --- Shell ---
    def shell_set_status(self, text: str, color: str):
        self.status_shell.configure(text=text, text_color=color)

    def shell_set_buttons(self, connected: bool):
        self.btn_connect_shell.configure(state="disabled" if connected else "normal")
        self.btn_disconnect_shell.configure(state="normal" if connected else "disabled")
        self.command_button.configure(state="normal" if connected else "disabled")

    def shell_append_output(self, text: str):
        self.shell_output.insert("end", text)
        self.shell_output.see("end")

    def shell_clear_output(self):
        self.shell_output.delete("1.0", "end")

    def shell_get_command(self) -> str:
        return self.command_entry.get().strip()

    def shell_clear_command_entry(self):
        self.command_entry.delete(0, "end")

    def shell_set_command_entry(self, value: str):
        self.command_entry.delete(0, "end")
        self.command_entry.insert(0, value)

    # --- Camera ---
    def camera_set_status(self, text: str, color: str):
        self.status_camera.configure(text=text, text_color=color)

    def camera_set_buttons(self, connected: bool):
        self.btn_connect_camera.configure(state="disabled" if connected else "normal")
        self.btn_disconnect_camera.configure(state="normal" if connected else "disabled")
        self.camera_toggle_button.configure(state="normal" if connected else "disabled")

    def camera_set_image(self, ctk_img):
        self.camera_label.configure(image=ctk_img, text="")
        self.camera_label.image = ctk_img

    def camera_clear_image(self, message="Camera hidden"):
        self.camera_label.configure(image="", text=message)
        self.camera_label.image = None

    def camera_toggle_button_text(self, show: bool):
        self.camera_toggle_button.configure(text="🙈 Hide Camera" if show else "👁️ Show Camera")

    # ========================= lifecycle ========================= #
    def run(self):
        self.root.mainloop()

    def _on_close(self):
        try:
            self.logic.close_all()
        except Exception:
            pass
        self.root.destroy()
