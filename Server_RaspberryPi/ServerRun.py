from Server_RaspberryPi.RPICameraServer import RPICameraServer
import time

def server_forever(config_file='camera_config_HQ.json'):
	while True:
		try:
			Obj = RPICameraServer(camera_config_file=config_file)
			Obj.run()
		except Exception as e:
			print("exception: ", e)
			time.sleep(5)

if __name__ == '__main__':
	config_file_HQ = 'camera_config_HQ.json'
	config_file_V2 = 'camera_config_V2.json'
	server_forever(config_file_V2)
