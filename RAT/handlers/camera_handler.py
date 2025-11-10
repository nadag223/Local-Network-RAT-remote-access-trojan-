import struct
import cv2

import time

def camera_handler(client_socket, address):
    print(f"[CAMERA] לקוח התחבר מ-{address}")

    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("לא ניתן לפתוח מצלמה")

        while True:
            ret, frame = cap.read()
            if not ret:
                raise Exception("קריאה ממצלמה נכשלה")

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