# Raspberry & Pi Camera as ethernet camera
A server client application to use a raspberry pi and a CSI-camera as ethernet camera. The project is mostly designed for computer vision applications. Single uncompressed ("still") images can be polled by the Client.



![](Doc/Overview.png)

## Installation Server
Use ssh or a display/keyboard setup to install the project on the Raspberry Pi (Server)
```
git clone https://github.com/LeonPfenning/raspberry-pi-as-ethernet-camera.git
```

```
sudo apt install -y python3-picamera2=0.3.9-1
```

## Installation Client

```
git clone https://github.com/LeonPfenning/raspberry-pi-as-ethernet-camera.git
```
1. Navigate into "Client_Computer" folder
2. Create venv
3. Install requirements.txt

## Getting Started
### Network
- Connect client and server:
  - Fig1. config.1: indirect connection between client and server with a router inbetween
  - Fig1. config.2: direct connection between client and server via ethernet cable (**PREFERRED** faster and more robust)
- Configure the server to have a static ip (optional but quite helpful)
  - Make sure client and server can ping each other
  
### RPI Camera
- Attach a CSI camera to the RPI 
- Configure RPI to work with camera (more info: https://github.com/raspberrypi/picamera2)
- Make sure camera is working correctly (e.g. run basic example from picamera2)

### Setup _camera_config.json_ File
**A _camera_config.json_ File for the HQ camera and the V2 camera are provided.**

The _camera_config.json_ file allows specifying custom camera setups that the camera can be operated in.  The camera setup basically consists of the image resolutions the user needs for his application.
The individual camera setups can then be selected remotely by the Client (Computer).
I personally focus on full fov modi and some resized resolutions of those.
My camera setups can be found in the example file for the HQ camera. If you use a different camera, or you have different requirements than I do you should configure your own _camera_config.json_ file.
- configure _camera_config.json_ for a camera
  - check what camera setups are available for your camera: run _camera_config_helper.py_ script on rpi (server)
  - modify the _build_camera_config_file.py_ script with your desired setups
- add the created files to **both** repositories!

### Run Code
First run the script on the server (RPI):
```
python3 ServerRun.py
```

Run an example script on the client (Computer):
```
python3 /examples/Camera_Preview.py
```

___
## What to expect
For a small overview what fps can be expected and where the limitation come from, have a look into the following document:
[FPS_Docs.md](Doc%2FFPS_Docs.md)

Keep in mind we are capturing and transferring uncompressed still images!

___
## Troubleshooting
- server and client should be able to ping each other
- the server software on the rpi has to run
- camera_config.py has to be identical in the server and client project
- to use the rpi in headless mode (without display), the rpi might need to be configured additionally
- if fps are lower than expected check if exposure time is set to high
