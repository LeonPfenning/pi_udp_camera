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
    def __init__(self, IP='141.100.109.17', Port=8123, camera_modus='91'):
        self.IP = IP
        self.Port = Port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, Port))
        self.rdFile = self.client_socket.makefile('rb')
        print("communication with rpi initialized...")
        self.save_idx = 0

        self.client_socket.sendall(camera_modus.encode())
        time.sleep(0.5)
        self.init_camera_modi(camera_modus)
        self.init_calibrated_camera()

    def init_camera_modi(self, msg):
        f = open("../Configuration/camera_config.json")
        data = json.load(f)
        if msg == data['90']:
            self.res = data['90']['res']
            self.forma = data['90']['forma']
            self.img_shape = data['90']['img_shape']
        elif msg == data['91']:
            self.res = data['91']['res']
            self.forma = data['91']['forma']
            self.img_shape = data['91']['img_shape']
        elif msg == data['92']:
            self.res = data['92'].res
            self.forma = data['92']['forma']
            self.img_shape = data['92']['img_shape']
        elif msg == data['93']:
            self.res = data['93']['res']
            self.forma = data['93']['forma']
            self.img_shape = data['93']['img_shape']
        else:
            self.res = data['default']['res']
            self.forma = data['default']['forma']
            self.img_shape = data['default']['img_shape']

    def get_img_stream(self):
        # request image
        msg = "1"
        self.client_socket.sendall(msg.encode())

        # get byte count of data to read
        data = self.rdFile.read(struct.calcsize('<L'))
        image_len = struct.unpack('<L', data)[0]
        if not image_len:
            return None

        # get data
        image_stream = self.rdFile.read(image_len)
        return image_stream

    def change_exposure(self):
        msg = "2"
        self.client_socket.sendall(msg.encode())
        print("send shutter Speed:")
        msg = input()
        self.client_socket.sendall(msg.encode())

    def set_exposure(self, exp):
        msg = "2"
        self.client_socket.sendall(msg.encode())
        time.sleep(0.1)
        exp = str(exp)
        self.client_socket.sendall(exp.encode())
        time.sleep(0.5)

    def preview_img_yuv(self, checkerboard_detection=False):
        image_stream = self.get_img_stream()
        test = np.frombuffer(image_stream, 'uint8')
        test = test.reshape(self.img_shape)           # (1140, 1024)   # (2280, 2048)
        img = cv2.cvtColor(test, cv2.COLOR_YUV420p2RGB)
        self.im = img.copy()
        if checkerboard_detection:
            img, rmat, self.tvecs = self.pose_estimation(img)
        im_resized = cv2.resize(img, (1014, 760))           # (760, 1014)    # (1520, 2028)
        cv2.imshow('Video', im_resized)
        cv2.setMouseCallback('Video', self.click_event)
        cv2.waitKey(1)

    def click_event(self, event, x, y, flags, params):
        # checking for left mouse clicks
        if event == cv2.EVENT_LBUTTONDOWN:
            pass
        # checking for right mouse clicks
        if event == cv2.EVENT_RBUTTONDOWN:
            self.save_img()

    def save_img(self):
        if self.tvecs[0] is not None:
            im = Image.fromarray(self.im[:, :, ::-1])   # bgr <--> rgb
            save_str = 'Img_data/img' + str(self.saveidx) + '.png'
            self.save_idx += 1
            im.save(save_str, compress_level=0)
            print("Img saved")

    def reconnect(self):
        try:
            self.close()
        except:
            pass
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.IP, self.Port))
        self.rdFile = self.client_socket.makefile('rb')

    def close(self):
        print("closed all")
        self.rdFile.close()
        self.client_socket.close()

    def shutdown(self):
        msg = "0"
        try:
            self.client_socket.sendall(msg.encode())
            self.close()
        except:
            pass
        time.sleep(0.25)

    def speed_test(self, count=50):
        dt = []
        t = time.perf_counter()
        for i in range(cnt):
            print(i)
            self.get_img_stream()
            dt.append((time.perf_counter() - t))
        elapsed = time.perf_counter() - t
        dt = np.array(dt)
        dt = np.diff(dt, axis=0)
        print("elapsed time: ", elapsed)
        print("frequency: ", count/elapsed)
        print("min dt: ", np.min(dt))
        print("max dt: ", np.max(dt))
        print("meadian dt: ", np.median(dt))
        # elapsed = 41 seconds for 200 img --> 4.9 Images/sec.

    def init_calibrated_camera(self):
        self.mtx = np.array([[5242, 0.0, 973],
                             [0.0, 5245, 808.5],
                             [0.0, 0.0, 1.0]])
        self.dist = np.array([0, 0, 0, 0, 0])
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(cameraMatrix=self.mtx, distCoeffs=self.dist,
                                                           R=None, newCameraMatrix=self.mtx,
                                                           size=self.res, m1type=5)

    def draw(self, img, corners, imgpts):
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

    def pose_estimation(self, img):
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
            img = self.draw(img, corners, imgpts)
        return img, rmat, tvecs


if __name__ == '__main__':
    IP = '169.254.148.62'
    myCam = pi_udp_camera_pc(IP, camera_modus='91')
    myCam.speed_test(cnt=50)

    myCam.set_exposure(50000)        # 50000 => 20Hz
    cnt = 0
    t = time.perf_counter()
    while True:
        try:
            # myCam.change_exposure()
            # myCam.set_exposure(20000)
            myCam.preview_img_yuv(checkerboard_detection=True)
            cnt += 1
            elapsed = time.perf_counter() - t

            if elapsed > 1:
                print(cnt/elapsed)
                t = time.perf_counter()
                cnt = 0
        except:
            print("called shutdown")
            myCam.shutdown()
            raise
        finally:
            pass
