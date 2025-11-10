import struct
import cv2
import numpy as np
import mss
import time

def screen_handler(client_socket, address):
    print(f"[SCREEN] לקוח התחבר מ-{address}")
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # מסך ראשי

            while True:
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
