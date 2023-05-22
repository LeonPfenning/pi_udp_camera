import time
import sys
sys.path.insert(0, '..')
from picamera2 import Picamera2
from Core.MessageDescription import MessageDescription
from Core.CameraConfiguration import CameraConfiguration
from Core.Server import Server


class RPICameraServer(MessageDescription, CameraConfiguration):
    def __init__(self, camera_config_file='camera_config_HQ.json'):
        MessageDescription.__init__(self)
        CameraConfiguration.__init__(self)
        self.camera_config_file = camera_config_file
        self.com_obj = Server()

        self.picam2 = None

    def _init_camera_mode(self):
        camera_configuration_modus = self.com_obj.receive_data(self.CAM_MODUS_BYTE_COUNT)
        if camera_configuration_modus is None:
            raise Exception("camera_config_modus is none")
        print('camera modus: ', camera_configuration_modus)
        self.picam2 = self._camera_setup(camera_configuration_modus, False)

    def run(self):
        """This function needs to be run to use the class!"""
        self._init_camera_mode()
        try:
            while True:
                cmd = self.com_obj.receive_data(self.MSG_BYTE_COUNT)
                if cmd == self.GET_IMAGE_MSG:
                    image_stream = self._get_img_stream()
                    self.com_obj.send_data(image_stream)

                elif cmd == self.CHANGE_EXPOSURE_MSG:
                    val = self.com_obj.receive_data(10)
                    self.picam2.set_controls({"ExposureTime": int(val)})

                elif cmd == self.SHUTDOWN_MSG:
                    print("shutdown!")
                    self._close()
                    return

                else:
                    print("unknown command!")
                    self._close()
                    return

        except Exception as e:
            # Exceptions I encountered:
            # [Errno 104] Connection reset by peer
            # received package with zero length
            print("Exception: ", e)
            self._close()
            print("clean up")

        finally:
            self.picam2 = None
            self.com_obj = None

    def _get_img_stream(self):
        # get image from camera
        stream = self.picam2.capture_array("main")
        print(stream.shape)
        return stream.tobytes()

    def _camera_setup(self, received_camera_modus_msg: str = '91', force_sensor_resolution: bool = False):
        picam2 = Picamera2()

        self.open_config_file(self.camera_config_file)
        self.get_camera_config(received_camera_modus_msg)
        if force_sensor_resolution:
            # is quite a bit slower
            config = picam2.create_still_configuration(buffer_count=1,
                                                       main={"size": self.image_size, "format": self.format},
                                                       queue=False,
                                                       raw={"size": (self.raw_img_format[0], self.raw_img_format[1])})
        else:
            config = picam2.create_still_configuration(buffer_count=1,
                                                       main={"size": self.image_size, "format": self.format},
                                                       queue=False)

        picam2.configure(config)
        picam2.align_configuration(config)
        picam2.set_controls({"ExposureTime": int(10000),  # 100,000 --> 100Hz
                             "AnalogueGain": 1.0,
                             "AeEnable": False,
                             "AwbEnable": False,
                             "NoiseReductionMode": False})

        picam2.start()
        picam2.capture_array("main")
        return picam2

    def _close(self):
        self.picam2.stop()
        self.picam2.close()
        self.com_obj.close()
        time.sleep(1)


if __name__ == '__main__':
    pass
