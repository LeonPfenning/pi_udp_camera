# Raspberry Pi Camera as UDP Camera
A server client application to use a raspberry pi with an attached CSI-camera as udp camera. A basic interface between the computer and the raspberry pi is provided to setup the camera-mode (resolution, binning, image format, ...) and control the exposure time. This Project allows to use the raspberry pi + camera to be used in headless mode by controlling it from an external device (computer).

The Application is used to acquire mostly uncompressed images, depending on network speed and chosen image resolution the framerate might be rather low.

![](Doc/Overview.png)

### Steps to start
- clone repo to raspberry pi and install requirements in folder "RaspberryPi"
- clone repo to computer and install requirements in folder "Computer"
- configure camera_config.json for the used camera (basic Hq camera provided)
- identify rpi ip address
- run camera_rpi.py on Server (RPI)
- run camera_pc.py on Client (Computer)

### What to expect in terms of fps (HQ Camera)
Keep in mind: We only acquire uncompressed still images

Network limitations (theoretical):

  .     | resolution | formular      | file size (uncompressed) | theoretical fps (1Gbit/s) | 
------- |------------|---------------|--------------------------|---------------------------------------|
rgb888  | 4056x3040  | h * w * 3     | ~37 Mbyte                | 3                                     |
yuv420  | 4056x3040  | h * w * (3/2) | ~18 Mbyte                | 7                                     |
rgb888  | 2028x1520  | h * w * 3     | ~9 Mbyte                 | 14                                    |
yuv420  | 2028x1520  | h * w * (3/2) | ~5 Mbyte                 | 25                                    |

#

Max image acquisition speed on RPI4 with picamera2.capture_array() (measured):

  .     | resolution | images taken | duration | measured fps | 
------- |------------|--------------|----------|--------------|
rgb888  | 4056x3040  | 200          | 60 sec.  | 3            |
yuv420  | 4056x3040  | 200          | 21 sec.  | 9            |
rgb888  | 2028x1520  | 200          | 16 sec.  | 12           |
yuv420  | 2028x1520  | 200          | 10 sec.  | 20           |
rgb888  | 1014x760   | 200          | 5 sec.   | 40¹           |
yuv420  | 1014x760   | 200          | 5 sec.   | 40¹           |
rgb888  | 2028x1520  | 200          | 5 sec.   | 40¹           |
yuv420  | 2028x1520  | 200          | 5 sec.   | 40¹           |
¹ capped by sensor_mode: full fov max 40fps
#
Actual speed measured (direct ethernet connection) (measured):

  .     | resolution  | images taken | duration  | measured fps     | 
------- |-------------|--------------|-----------|------------------|
rgb888  | 4056x3040   | --           | --        | not implemented  |
yuv420  | 4056x3040   | 50           | 16 sec.   | 3                |
rgb888  | 2028x1520   | --           | --        | not implemented  |
yuv420  | 2028x1520   | 50           | 5 sec.    | 10               |
rgb888  | 1014x760    | --           | --        | not implemented  |
yuv420  | 1014x760    | 50           | 1.25 sec. | 40               |


### Troubleshooting
- server and client should be able to ping eachother
- camera_config.py has to be identical in the server and client project
- the rpi has to be configured to work in headless mode (without monitor)
- if fps are lower as expected check if exposure time is set to high