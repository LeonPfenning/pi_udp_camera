from picamera2 import Picamera2

def configure_camera(camera_obj, img_resolution, format):
	config = camera_obj.create_still_configuration(buffer_count=1,
											   main={"size": img_resolution, "format": format},
											   queue=False)
	camera_obj.configure(config)
	camera_obj.start()
	stream = camera_obj.capture_array("main")

	print("image_Size: ", img_resolution)
	print("file_Size: ", stream.shape)

	camera_obj.stop()
	print()

if __name__ == '__main__':
	picam2 = Picamera2()
	print()

	sensor_modes = picam2.sensor_modes
	print()

	# sensor modes directly supported by camera (no post processing on isp necessary)
	for ele in sensor_modes:
		print(ele)
		img_resolution = ele['size']
		format = "YUV420"
		configure_camera(picam2, img_resolution, format)


	# images are postprocessed / resized by the rpi ISP
	# Any value can be entered bellow but I normally go for the smallest full FOV setting
	full_frame_res = (2028, 1520)					# Enter the initial value here

	res_halfe = (int(full_frame_res[0]/2), int(full_frame_res[1]/2))
	format = "YUV420"
	configure_camera(picam2, res_halfe, format)


	res_quarter = (int(res_halfe[0]/2), int(res_halfe[1]/2))
	format = "YUV420"
	configure_camera(picam2, res_quarter, format)
