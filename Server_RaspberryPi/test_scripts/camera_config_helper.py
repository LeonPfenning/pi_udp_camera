from picamera2 import Picamera2


def configure_camera(camera_obj, img_resolution, format, raw_img_resolution):
	config = camera_obj.create_still_configuration(buffer_count=1,
											   	   main={"size": img_resolution, "format": format},
											       queue=False,
												   raw={"size": raw_img_resolution})

	camera_obj.configure(config)
	camera_obj.start()
	stream = camera_obj.capture_array("main")
	print('"file_size": ', stream.shape, ',')
	print('"format": "' + format + '",')
	print('"image_size": ', img_resolution, ',')
	print('"raw_img_format": ', raw_img_resolution, '},')
	camera_obj.stop()


if __name__ == '__main__':
	picam2 = Picamera2()
	sensor_modes = picam2.sensor_modes

	smalles_full_fov_resolution = (5000, 5000)		# just some dummpy values
	print("\n\nCamera Configurations:")
	print("native camera configs. no postprocessing on isp necessary:")
	for idx, ele in enumerate(sensor_modes):
		print('\n')
		print("camera configuration: ", idx)
		print(ele)
		fov = ele['crop_limits']
		if (fov[0] != 0) or (fov[1] != 0):
			print("Skipped not full fov!")
			continue
		img_resolution = ele['size']
		format = "YUV420"
		configure_camera(picam2, img_resolution, format, img_resolution)
		if (img_resolution[0] < smalles_full_fov_resolution[0]) or (img_resolution[1] < smalles_full_fov_resolution[1]):
			smalles_full_fov_resolution = img_resolution

	# images are postprocessed / resized by the rpi ISP
	# Any value could be entered bellow.
	# I normally go for the smallest full FOV resolution.
	print("\n\ncamera configs. that requires postprocessing on isp:")
	print('\n')
	print("camera configuration: ", idx+1)
	res_halfe = (int(smalles_full_fov_resolution[0] / 2), int(smalles_full_fov_resolution[1] / 2))
	format = "YUV420"
	configure_camera(picam2, res_halfe, format, smalles_full_fov_resolution)

	print('\n')
	print("camera configuration: ", idx+2)
	res_quarter = (int(res_halfe[0] / 2), int(res_halfe[1] / 2))
	format = "YUV420"
	configure_camera(picam2, res_quarter, format, smalles_full_fov_resolution)
