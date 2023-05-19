import json
import os

class CameraConfiguration:
	def __init__(self):
		# Camera modi
		self.CAM_MODUS_BYTE_COUNT = 2
		self.CAM_MODUS_1 = '90'
		self.CAM_MODUS_2 = '91'
		self.CAM_MODUS_3 = '92'
		self.CAM_MODUS_4 = '93'

		self.SELECTED_CAMERA_MODUS = None
		self.ROOT_DIR = None
		self.camera_configuration_file_name = None
		self.data = None
		self.image_size = None
		self.format = None
		self.file_size = None
		self.data_byte_count = None
		self.raw_img_format = None

	def open_config_file(self, camera_configuration_file_name: str):
		self.camera_configuration_file_name = camera_configuration_file_name
		self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
		f = open(self.ROOT_DIR + '/Configuration_Files/' + self.camera_configuration_file_name)
		self.data = json.load(f)

	def get_camera_config(self, camera_modus_identifier: str):
		# implementation like this not necessary, but we might want to set stuff that's not in the config file
		valid_config_modus = False
		if camera_modus_identifier == self.CAM_MODUS_1:
			valid_config_modus = True
		elif camera_modus_identifier == self.CAM_MODUS_2:
			valid_config_modus = True
		elif camera_modus_identifier == self.CAM_MODUS_3:
			valid_config_modus = True
		elif camera_modus_identifier == self.CAM_MODUS_4:
			valid_config_modus = True

		if valid_config_modus:
			self.SELECTED_CAMERA_MODUS = camera_modus_identifier
			self.image_size = self.data[self.SELECTED_CAMERA_MODUS]['image_size']
			self.format = self.data[self.SELECTED_CAMERA_MODUS]['format']
			self.file_size = self.data[self.SELECTED_CAMERA_MODUS]['file_size']
			self.raw_img_format = self.data[self.SELECTED_CAMERA_MODUS]['raw_img_format']
			self.data_byte_count = int(self.file_size[0] * self.file_size[1])
		else:
			self.image_size = self.data['default']['image_size']
			self.format = self.data['default']['format']
			self.file_size = self.data['default']['file_size']
			self.raw_img_format = self.data['default']['raw_img_format']
			self.data_byte_count = int(self.file_size[0] * self.file_size[1])

