# Raspberry & Pi Camera as UDP Camera
A server client application to use a raspberry pi and a CSI-camera as ethernet camera. The project is mostly designed for computer vision applications. Single uncompressed ("still") images can be polled by the Client.

A basic interface between the computer and the raspberry pi is provided to initialize/set the camera-configuration (resolution, binning, image format, ...) and control the exposure time. This project allows to use a raspberry pi + camera similar to an industrial ethernet camera.



![](Doc/Overview.png)

## Installation Server
Use ssh or a display/keyboard setup to install the project on the Raspberry Pi (Server)
```
git clone https://github.com/LeonPfenning/pi_udp_camera.git
```

```
sudo apt install -y python3-picamera2=0.3.9-1
```

## Installation Client

```
git clone https://github.com/LeonPfenning/pi_udp_camera.git
```
1. Navigate into "Client_Computer" folder
2. Create venv
3. Install requirements.txt

## Getting Started
### Network
- Connect client and server:
  - Fig1. config.1: indirect connection between client and server with a router inbetween
  - Fig1. config.2: direct connection between client and server via ethernet cable (**PREFERRED**)
- Configure the server to have a static ip (optional but quite helpful)
  - Make sure client and server can ping each other
  
### RPI Camera
- Attach a CSI camera to the RPI 
- Configure RPI to work with camera (more info: https://github.com/raspberrypi/picamera2)
- Make sure camera is working correctly (e.g. run basic example from picamera2)

### Setup _camera_config.json_ File
**A _camera_config.json_ File for the HQ camera and the V2 camera is provided.**

The _cameera_config.json_ file allows specifying custom camera setups that the camera can work in. Those setups can be selected from the client.
The custom camera setups can vary depending on the individual requirements of the user. I personally focus on  full fov modi and some resized resolutions of those.
My camera setups can be found in the example file for the HQ camera. If you use a different camera than the HQ Camera you should configure your own _camera_config.json_ file.
- configure camera_config.json for the used camera
  - the build_camera_config_file.py script can help you to build a custom _camera_config.json_ file
  - if you don't know what parameter your camera supports you might want to have a look into the camera_config_helper.py script
- add the created files to **both** repositories

### Run Code
First run the script on the server (RPI):
```
python3 ServerRun.py
```

Then run an example script on the client (Computer):
```
python3 /examples/Camera_Preview.py
```

___
## What to expect in terms of fps (HQ Camera)
Keep in mind: We acquire and send uncompressed still images. The application is not targeting fast fps image streaming!
Depending on used hardware, network speed and chosen camera settings the resulting framerate might be different.

Network limitations - file transfer (mathematical example):

format  | resolution | formular      | file size (uncompressed) | theoretical fps (1Gbit/s)   | 
------- |------------|---------------|--------------------------|-----------------------------|
bgr888  | 4056x3040  | h * w * 3     | ~37.0 Mbyte              | ~3                          |
yuv420  | 4056x3040  | h * w * (3/2) | ~18.5 Mbyte              | ~7                          |
bgr888  | 2028x1520  | h * w * 3     | ~9.3 Mbyte               | ~14                         |
yuv420  | 2028x1520  | h * w * (3/2) | ~4.6 Mbyte               | ~25                         |
bgr888  | 1014x760   | h * w * 3     | ~2.3 Mbyte               | ~14                         |
yuv420  | 1014x760   | h * w * (3/2) | ~1.2 Mbyte               | ~25                         |
#

Max image acquisition speed of a RPI4 + HQ camera with picamera2.capture_array() (measured):

```
image_size = (2028, 1520)
format = "YUV420"
config = picam2.create_still_configuration(buffer_count=1,
                                           main={"size": image_size, "format": format},
                                           queue=False)
picam2.configure(config)
picam2.set_controls({"ExposureTime": int(300),
                     "AnalogueGain": 1.0,
                     "AeEnable": False,
                     "AwbEnable": False,
                     "NoiseReductionMode": False})
picam2.still_configuration.align()

for i in range(img_count):
     array = picam2.capture_array("main")
     stream = array.tobytes()

```

format  | resolution | images taken | duration | measured fps | 
------- |------------|--------------|----------|--------------|
bgr888  | 4056x3040  | 200          | 60 sec.  | 3            |
yuv420  | 4056x3040  | 600          | 78 sec.  | 8            |
bgr888  | 2028x1520  | 2000         | 162 sec. | 12           |
yuv420  | 2028x1520  | 2000         | 85 sec.  | 23           |
bgr888  | 1014x760   | 600          | 15 sec.  | 40¹          |
yuv420  | 1014x760   | 600          | 15 sec.  | 40¹          |
bgr888  | 507x380    | 600          | 15 sec.  | 40¹          |
yuv420  | 507x380    | 600          | 15 sec.  | 40¹          |
¹ capped by sensor_mode: full FOV max 40fps
#

Actual speed measured with ethernet connection (measured):

format  | resolution  | images taken | duration  | measured fps     |
------- |-------------|--------------|-----------|------------------|
bgr888  | 4056x3040   | --           | --        | not implemented  |
yuv420  | 4056x3040   | 50           | 16 sec.   | 3                |
bgr888  | 2028x1520   | --           | --        | not implemented  |
yuv420  | 2028x1520   | 50           | 5 sec.    | 10               |
bgr888  | 1014x760    | --           | --        | not implemented  |
yuv420  | 1014x760    | 50           | 1.25 sec. | 40               |

___
## Troubleshooting
- server and client should be able to ping each other
- the server software on the rpi has to run
- camera_config.py has to be identical in the server and client project
- to use the rpi in headless mode (without display), the rpi might need to be configured additionally
- if fps are lower than expected check if exposure time is set to high