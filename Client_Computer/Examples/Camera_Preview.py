from Client_Computer.RPICameraClient import RPICameraClient
import time

IP = '169.254.148.62'
# IP = '192.168.1.13'
Port = 8123
myCam = RPICameraClient(ip=IP, port=Port, camera_config_file='camera_config_HQ.json',
						 camera_modus='92', calibrated_camera=False)

myCam.set_exposure(25000)        # 50000 => 20Hz
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

	except:
		print("called close")
		myCam.close()
		raise
	finally:
		pass