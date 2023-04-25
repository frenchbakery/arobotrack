import io
import socket
import struct
import cv2
import numpy as np
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)
connection = server_socket.accept()[0].makefile('rwb')


try:
    while True:
        # Read the length of the image as a 32-bit unsigned int
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        # Construct a stream to hold the image data and read the image data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream and convert the image data to a NumPy array
        image_stream.seek(0)
        image_array = np.frombuffer(image_stream.getvalue(), dtype=np.uint8)
        # Decode the image and display it
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        cv2.imshow('Image', image)

finally:
    connection.close()
    server_socket.close()