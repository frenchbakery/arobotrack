import io
import socket
import struct
import time
import picamera

# Connect a client socket to my laptop's IP address and port 8000
client_socket = socket.socket()
client_socket.connect(('192.168.4.106', 8000))

# Make a file-like object out of the connection
connection = client_socket.makefile('rwb')


try:
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        time.sleep(2) # Let camera warm up
        start = time.time()
        stream = io.BytesIO()

        for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            # Send the image length and data over the network
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            stream.seek(0)
            stream.truncate()

            time.sleep(0.01)


finally:
    connection.close()
    client_socket.close()

    time.sleep(1)

    exit(1)