import socket
import struct
import time
import json
from picamera2 import Picamera2


class pi_udp_camera_rpi:
    def __init__(self, camera_config_file='camera_config_HQ.json'):
        self.GET_IMAGE_MSG = '1'
        self.CHANGE_EXPOSURE_MSG = '2'
        self.camera_config_file = camera_config_file
        self.open_server_connection()
        self.camera_main_loop()

    def open_server_connection(self):
        HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
        PORT = 8123  # Port to listen on (non-privileged ports are > 1023)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        print('Listening...')
        self.conn, self.addr = self.server_socket.accept()
        print(f"Connected by {self.addr}")

    def camera_main_loop(self):
        while True:
            camera_modus = self.receive_cmd()
            print('camera modus: ', camera_modus)
            self.picam2 = self.camera_setup(camera_modus)
            try:
                while True:
                    cmd = self.receive_cmd()
                    if cmd == self.GET_IMAGE_MSG:
                        stream = self.get_img_stream()
                        self.send_data(stream)
                    elif cmd == self.CHANGE_EXPOSURE_MSG:
                        data = self.conn.recv(1024)
                        if not data:
                            print("recieved package with zero length")
                            break
                        val = data.decode()
                        self.picam2.set_controls({"ExposureTime": int(val)})
                    else:
                        print("unknown command - maybe connection was shut down")
                        raise Exception("computer shutdown")
            except:
                self.conn.shutdown()
                self.picam2.stop()
                self.picam2.close()
                self.server_socket.close()
                print("clean up")
            finally:
                self.picam2.close()
                self.conn.close()
                self.server_socket.close()

    def get_img_stream(self):
        stream = self.picam2.capture_array("main")
        print(stream.shape)
        return stream.tobytes()

    def send_data(self, byte_stream):
        mk_file = self.conn.makefile('wb')
        # send length of data encoded in 4byte (so client knows what to listen for)
        mk_file.write(struct.pack('<L', len(byte_stream)))
        mk_file.write(byte_stream)
        mk_file.close()

    def camera_setup(self, camera_modus='91'):
        picam2 = Picamera2()
        f = open('../Configuration/' + self.camera_config_file)
        data = json.load(f)
        if camera_modus == '90':
            image_size = data['90']['image_size']
            format = data['90']['format']
        elif camera_modus == '91':
            image_size = data['91']['image_size']
            format = data['91']['format']
        elif camera_modus == '92':
            image_size = data['92']['image_size']
            format = data['92']['format']
        elif camera_modus == '93':
            image_size = data['93']['image_size']
            format = data['93']['format']
        else:
            image_size = data['default']['image_size']
            format = data['default']['format']

        config = picam2.create_still_configuration(buffer_count=1,
                                                   main={"size": image_size, "format": format},
                                                   queue=False)
        picam2.configure(config)
        print(picam2.align_configuration(config))
        picam2.set_controls({"ExposureTime": int(300),  # 1,000,000 --> 1 sec.
                             "AnalogueGain": 1.0,
                             "AeEnable": False,
                             "AwbEnable": False,
                             "NoiseReductionMode": False})

        picam2.start()
        picam2.capture_array("main")
        return picam2

    def receive_cmd(self):
        data = self.conn.recv(128)
        if not data:
            print("recieved package with zero length")
            return None
        cmd = data.decode()
        return cmd


if __name__ == '__main__':
    while True:
        try:
            Obj = pi_udp_camera_rpi()
        except:
            print("exception")
            time.sleep(5)
