import socket
import struct
from PIL import Image
import cv2
import numpy as np
import time
import json

# interesting speed comaprison:
# https://stackoverflow.com/questions/49784551/python-frame-data-optimization-before-sending-through-socket
# black and white image: https://buildmedia.readthedocs.org/media/pdf/picamera/latest/picamera.pdf
# page 29 Search: "Y plane"

class pi_udp_camera_pc:
    def __init__(self, IP='141.100.109.17', Port=8123, camera_config_file='camera_config_HQ.json',
                 camera_modus='91', calibrated_camera=False):
        # Costants
        self.CAM_MODUS_1 = '90'
        self.CAM_MODUS_2 = '91'
        self.CAM_MODUS_3 = '92'
        self.CAM_MODUS_4 = '93'

        self.SHUTDOWN_MSG = '0'
        self.GET_IMAGE_MSG = '1'
        self.CHANGE_EXPOSURE_MSG = '2'

        # Init
        self.IP = IP
        self.Port = Port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, Port))
        self.rdFile = self.client_socket.makefile('rb')
        print("communication with rpi initialized...")
        self.save_idx = 0

        self.__init_camera_modi(camera_config_file, camera_modus)
        self.calibrated_camera = calibrated_camera
        if calibrated_camera:
            self.__init_calibrated_camera()

    def __init_camera_modi(self, camera_config_file, camera_modus):
        # let camera know what modus to run in
        self.client_socket.send(camera_modus.encode())
        time.sleep(0.5)

        # locally initialize the camera modus
        f = open('../Configuration/' + camera_config_file)
        data = json.load(f)
        if camera_modus == '90':
            self.image_size = data['90']['image_size']
            self.format = data['90']['format']
            self.file_size = data['90']['file_size']
        elif camera_modus == '91':
            self.image_size = data['91']['image_size']
            self.format = data['91']['format']
            self.file_size = data['91']['file_size']
        elif camera_modus == '92':
            self.image_size = data['92']['image_size']
            self.format = data['92']['format']
            self.file_size = data['92']['file_size']
        elif camera_modus == '93':
            self.image_size = data['93']['image_size']
            self.format = data['93']['format']
            self.file_size = data['93']['file_size']
        else:
            self.image_size = data['default']['image_size']
            self.format = data['default']['format']
            self.file_size = data['default']['file_size']

    def _get_img_stream(self):
        # send request to get image ("1") to server.
        # Server will answer with the byte count of the image encoded in to 4 byte
        # After we know how many bytes the image has, we read data till we received the entire image
        msg = self.GET_IMAGE_MSG
        self.client_socket.send(msg.encode())
        # get byte count of data to read
        data = self.rdFile.read(struct.calcsize('<L'))
        image_len = struct.unpack('<L', data)[0]
        if not image_len:
            return None
        # get data
        image_stream = self.rdFile.read(image_len)
        return image_stream

    def get_image(self):
        image_stream = self._get_img_stream()
        numpy_img_bytes = np.frombuffer(image_stream, 'uint8')
        if self.format == 'YUV420':
            numpy_img_bytes = numpy_img_bytes.reshape(self.file_size)           # (1140, 1024)   # (2280, 2048)
            img = cv2.cvtColor(numpy_img_bytes, cv2.COLOR_YUV420p2RGB)
            img = img[0:self.image_size[1], 0:self.image_size[0], :]      # remove pixel without information (see: picamera2 yuv)
        else:
            raise NotImplemented("only yuv implemented yet")
        return img

    def change_exposure(self):
        print("enter shutter Speed:")
        msg = input()
        self.set_exposure(msg)

    def set_exposure(self, exp):
        msg = self.CHANGE_EXPOSURE_MSG
        self.client_socket.send(msg.encode())
        time.sleep(0.1)
        exp = str(exp)
        self.client_socket.send(exp.encode())
        time.sleep(0.5)

    def preview_img(self, checkerboard_detection=False):
        img = self.get_image()
        self.im = img.copy()                            # deep copy of the file for saving
        if checkerboard_detection and self.calibrated_camera:
            img, self.rmat, self.tvecs = self._pose_estimation(img)
        im_resized = cv2.resize(img, (1014, 760))           # (760, 1014)    # (1520, 2028)
        cv2.imshow('Video', im_resized)
        cv2.setMouseCallback('Video', self.__click_event)
        cv2.waitKey(1)

    def __click_event(self, event, x, y, flags, params):
        # checking for left mouse clicks
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.tvecs is not None:
                print("Transformation:")
                H = np.eye(4)
                H[0:3,0:3] = self.rmat
                H[0:3, 3] = self.tvecs.squeeze()
                with np.printoptions(precision=3, suppress=True):
                    print(H)    # pretty-print
            else:
                print("no transformation available")
        # checking for right mouse clicks
        if event == cv2.EVENT_RBUTTONDOWN:
            self._save_img()

    def _save_img(self):
        if self.tvecs is not None:
            im = Image.fromarray(self.im[:, :, ::-1])   # bgr <--> rgb
            save_str = 'Img_data/img' + str(self.save_idx) + '.png'
            self.save_idx += 1
            im.save(save_str, compress_level=0)
            print("Img saved")
        else:
            print("checkerboard not detected don't save img")

    def __close_communication(self):
        print("closed all")
        self.rdFile.close()
        self.client_socket.close()

    def shutdown(self):
        msg = self.SHUTDOWN_MSG
        try:
            self.client_socket.send(msg.encode())
            self.__close_communication()
        except:
            pass
        time.sleep(0.25)

    def speed_test(self, count=50):
        dt = []
        t = time.perf_counter()
        for i in range(count):
            print(i)
            self._get_img_stream()
            dt.append((time.perf_counter() - t))
        elapsed = time.perf_counter() - t
        dt = np.array(dt)
        dt = np.diff(dt, axis=0)
        print("elapsed time: ", elapsed)
        print("frequency: ", count/elapsed)
        print("min dt: ", np.min(dt))
        print("max dt: ", np.max(dt))
        print("meadian dt: ", np.median(dt))
        # e.g. Img resolution (2028,1520) 50 img in 4.46 sec. --> 11.2fps


    def __init_calibrated_camera(self):
        self.mtx = np.array([[5242, 0.0, 973],
                             [0.0, 5245, 808.5],
                             [0.0, 0.0, 1.0]])
        self.dist = np.array([0, 0, 0, 0, 0])
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(cameraMatrix=self.mtx, distCoeffs=self.dist,
                                                           R=None, newCameraMatrix=self.mtx,
                                                           size=self.image_size, m1type=5)

    def __draw(self, img, corners, imgpts):
        corner = tuple(corners[0].ravel())
        corner = (int(corner[0]), int(corner[1]))
        x_axis = tuple(imgpts[0].ravel())
        x_axis = (int(x_axis[0]), int(x_axis[1]))
        y_axis = tuple(imgpts[1].ravel())
        y_axis = (int(y_axis[0]), int(y_axis[1]))
        z_axis = tuple(imgpts[2].ravel())
        z_axis = (int(z_axis[0]), int(z_axis[1]))
        img = cv2.line(img, corner, z_axis, (255, 0, 0), 5)
        img = cv2.line(img, corner, y_axis, (0, 255, 0), 5)
        img = cv2.line(img, corner, x_axis, (0, 0, 255), 5)
        return img

    def _pose_estimation(self, img):
        board = (7, 4)  # board shape
        square_size = 15
        objp = np.zeros((board[1] * board[0], 3), np.float32)
        objp[:, :2] = np.mgrid[0:board[0], 0:board[1]].T.reshape(-1, 2) * square_size
        axis = np.float32([[2 * square_size, 0, 0], [0, 2 * square_size, 0], [0, 0, 2 * square_size]]).reshape(-1, 3)

        img = cv2.remap(img, self.mapx, self.mapy, cv2.INTER_LINEAR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, board, None, flags=cv2.CALIB_CB_FAST_CHECK)
        rmat = None
        tvecs = None
        if ret:
            cv2.drawChessboardCorners(img, board, corners, ret)
            (success, rvecs, tvecs, reprojectionError) = cv2.solvePnPGeneric(objectPoints=objp, imagePoints=corners,
                                                                             cameraMatrix=self.mtx, distCoeffs=None,
                                                                             flags=cv2.SOLVEPNP_ITERATIVE)
            rvecs = rvecs[0]
            tvecs = tvecs[0]
            rmat = cv2.Rodrigues(rvecs)[0]
            imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, self.mtx, None)
            img = self.__draw(img, corners, imgpts)
        return img, rmat, tvecs


if __name__ == '__main__':
    IP = '169.254.148.62'
    Port = 8123
    myCam = pi_udp_camera_pc(IP=IP, Port=Port, camera_config_file='camera_config_HQ.json',
                             camera_modus='92', calibrated_camera=True)

    myCam.speed_test(count=500)
    myCam.set_exposure(20000)        # 50000 => 20Hz
    cnt = 0
    t = time.perf_counter()
    while True:
        try:
            # myCam.change_exposure()
            # myCam.set_exposure(20000)
            # myCam.get_image()
            myCam.preview_img(checkerboard_detection=False)

            cnt += 1
            elapsed = time.perf_counter() - t

            if elapsed > 1:
                print(cnt/elapsed)
                t = time.perf_counter()
                cnt = 0

            if cnt == 100:
                break
        except:
            print("called shutdown")
            myCam.shutdown()
            raise
        finally:
            pass
