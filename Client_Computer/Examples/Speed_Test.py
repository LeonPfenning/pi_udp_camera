from Client_Computer.RPICameraClient import RPICameraClient
import time
import numpy as np

def speed_test(myCam, count=50):
	dt = []
	t = time.perf_counter()
	for i in range(count):
		print(i)
		myCam._get_img_stream()
		# myCam.get_image()
		dt.append((time.perf_counter() - t))
	elapsed = time.perf_counter() - t
	dt = np.array(dt)
	dt = np.diff(dt, axis=0)
	print("elapsed time: ", elapsed)
	print("frequency: ", count / elapsed)
	print("min dt: ", np.min(dt))
	print("max dt: ", np.max(dt))
	print("meadian dt: ", np.median(dt))

if __name__ == '__main__':
	IP = '169.254.148.62'
	Port = 8123
	myCam = RPICameraClient(ip=IP, port=Port, camera_config_file='camera_config_HQ.json',
							camera_modus='92', calibrated_camera=True)

	speed_test(myCam, 400)

	myCam.close()

