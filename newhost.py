import cv2
import socket
import pickle
import struct
import threading
import ssl

# Function to handle each client connection
def handle_client(client_socket, addr):
    print('Connection from:', addr)

    # Read video file
    video_file = 'video.mp4'
    cap = cv2.VideoCapture(video_file)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))
            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a)) + a
            client_socket.sendall(message)

            # Display the transmitted video frame on the server side
            cv2.imshow(f"Transmitted Video - {addr}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(e)
    finally:
        cap.release()
        cv2.destroyWindow(f"Transmitted Video - {addr}")
        client_socket.close()
        print('Connection closed:', addr)

# Server socket setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '10.1.1.99'
port = 9999
socket_address = (host_ip, port)

# SSL context and wrapping
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('server.crt', 'server.key')
server_socket = ssl_context.wrap_socket(server_socket, server_side=True)

# Socket binding
server_socket.bind(socket_address)

# Socket listening
server_socket.listen(5)
print(f"Listening at {socket_address}")

# Accept multiple connections using threading
while True:
    client_socket, addr = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
