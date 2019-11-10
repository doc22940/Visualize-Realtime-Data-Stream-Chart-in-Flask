import time
import json

import cv2
import pickle
import struct
from threading import Thread, Event
from data_stream import *

from flask_handler import *
import socket

"""
ImageServer is a multithreaded socket server
receiving n amount of connections and proxy the messages
to flask
"""

class ImageServer(Thread):
    def __init__(self):
        super(ImageServer, self).__init__()

    def handle_connection(self, conn):
        with conn:
            while True:
                data = b""
                payload_size = struct.calcsize(">L")
                try:
                    # Recieve image package size
                    while len(data) < payload_size:
                        data += conn.recv(4096)

                        packed_msg_size = data[:payload_size]
                        data = data[payload_size:]
                        msg_size = struct.unpack(">L", packed_msg_size)[0]

                    # Recieve image
                    while len(data) < msg_size:
                        data += conn.recv(4096)
                    frame_data = data[:msg_size]
                    data = data[msg_size:]

                    data=pickle.loads(frame_data, fix_imports=True, encoding="bytes")

                    data = json.loads(data)
                    send_request(id = data["id"], data=data["value"], type =safe(data, "type"), active_points =safe(data, "active_points"),
                     _label=safe(data, "label"), _legend=safe(data, "legend"), _width = safe(data, "width"), _height = safe(data, "height"),
                      _name = safe(data, "name"), fill = safe(data, "fill"), backgroundColor = safe(data, "backgroundColor"), borderColor = safe(data, "borderColor"))
                except Exception as e:
                    pass
                    # Got corrupt image data1
                    #print(" WARNING: an error occured in image_server: ", e)


    def run(self):
        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        PORT = 12345        # Port to listen on (non-privileged ports are > 1023)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                print('Connected by', addr)
                Thread(target=self.handle_connection, args=(conn,)).start()

def safe(json, value):
    try:
        return json[value]
    except Exception:
        return