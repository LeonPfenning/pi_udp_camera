import sys
sys.path.insert(0, '..')
import cv2
import numpy as np
import time
from Core.MessageDescription import MessageDescription
from Core.CameraConfiguration import CameraConfiguration
from Core.Client import Client

# interesting speed comparison:
# https://stackoverflow.com/questions/49784551/python-frame-data-optimization-before-sending-through-socket
# black and white image: https://buildmedia.readthedocs.org/media/pdf/picamera/latest/picamera.pdf
# page 29 Search: "Y plane"

class RPICameraClient(MessageDescription, CameraConfiguration):
    def __init__(self, ip: str = '141.100.109.17', port: int = 8123, camera_config_file: str = 'camera_config_HQ.json',
                 camera_modus: str = '91', calibrated_camera: bool = False):
        # Init
        MessageDescription.__init__(self)
        CameraConfiguration.__init__(self)
        self.com_obj = Client(ip=ip, port=port)
        self.com_obj.connect()
        self.save_idx = 0

        self.__init_camera_modi(camera_config_file, camera_modus)
        self.calibrated_camera = calibrated_camera
        if calibrated_camera:
            self.__init_calibrated_camera()
        self.tvecs = None
        self.rmat = None


    def __init_camera_modi(self, camera_config_file: str, camera_configuration_modus: str):
        # let camera know what modus to run in
        self.com_obj.send_msg(camera_configuration_modus)
        time.sleep(0.5)

        # locally initialize the camera modus
        self.open_config_file(camera_config_file)
        self.get_camera_config(camera_configuration_modus)

    def _get_img_stream(self) -> bytes:
        # send request to server to get image.
        self.com_obj.send_msg(self.GET_IMAGE_MSG)
        # get byte count of data to read
        image_stream = self.com_obj.get_data(self.data_byte_count)
        return image_stream

    def get_image(self) -> np.ndarray:
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

    def set_exposure(self, exp: str):
        # msg = self.CHANGE_EXPOSURE_MSG
        self.com_obj.send_msg(self.CHANGE_EXPOSURE_MSG)
        time.sleep(0.1)
        exp = str(exp)

        self.com_obj.send_msg(exp)
        time.sleep(0.5)

    def preview_img(self, img_save_path=None, checkerboard_detection: bool = False):
        img = self.get_image()
        self.im = img.copy()                            # deep copy of the file for saving
        if checkerboard_detection and self.calibrated_camera:
            img, self.rmat, self.tvecs = self._pose_estimation(img)
        im_resized = cv2.resize(img, (1014, 760))           # (760, 1014)    # (1520, 2028)
        cv2.imshow('Video', im_resized)
        cv2.setMouseCallback('Video', self.__click_event, param=img_save_path)
        cv2.waitKey(1)

    def __click_event(self, event, x, y, flags, params=None):
        # checking for left mouse clicks
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.tvecs is not None:
                print("Transformation:")
                H = np.eye(4)
                H[0:3, 0:3] = self.rmat
                H[0:3, 3] = self.tvecs.squeeze()
                with np.printoptions(precision=3, suppress=True):
                    print(H)    # pretty-print
            else:
                print("no transformation available")
        # checking for right mouse clicks
        if event == cv2.EVENT_RBUTTONDOWN:
            img_path = params
            self.save_img(img=self.im, path=img_path)

    def save_img(self, img, path=None):
        if path:
            save_str = path
        else:
            save_str = 'Img_data/'
        save_str = save_str + 'img' + f"{self.save_idx:03}" + '.png'
        self.save_idx += 1
        print(save_str)
        cv2.imwrite(save_str, img, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        print("Img saved")

    def close(self):
        self.com_obj.send_msg(self.SHUTDOWN_MSG)
        self.com_obj.close()

    def __init_calibrated_camera(self):
        self.mtx = np.array([[5242, 0.0, 973],
                             [0.0, 5245, 808.5],
                             [0.0, 0.0, 1.0]])
        self.dist = np.array([0, 0, 0, 0, 0])

        self.mtx = np.array([[1305.54755504,    0.,          823.79146023],
                             [   0.,         1309.51471307,  640.22136024],
                             [   0.,            0.,            1.,        ]])
        self.dist = np.array([ 0.17180091, -0.32950401,  0.,          0.,         0.,        ])
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
    pass
