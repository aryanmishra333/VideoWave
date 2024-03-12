import cv2
import socket
import pickle
import struct
import ssl

# Client socket setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '192.168.157.30'
port = 9999
socket_address = (host_ip, port)

# SSL setup


try:
    # Create SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='server.crt')
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.check_hostname = True
    ssl_context.verify_callback = True
    client_socket = ssl_context.wrap_socket(client_socket, server_hostname='auth')

    # Connect to the server
    client_socket.connect(socket_address)

    data = b""
    payload_size = struct.calcsize("Q")

    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4 * 1024)
            if not packet:
                break
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(4 * 1024)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("Received", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except ssl.SSLError as e:
    print("SSL error occurred:", e)
    print("Certificate verification failed. Ensure that the server presents a valid certificate signed by a trusted Certificate Authority.")
except Exception as e:
    print("An error occurred:", e)
finally:
    client_socket.close()
    cv2.destroyAllWindows()
