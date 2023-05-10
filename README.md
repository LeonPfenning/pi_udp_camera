# Raspberry Pi Camera as UDP Camera
A server client application to use a raspberry pi with an attached CSI-camera as udp camera. A basic interface between the computer and the raspberry pi is provided to setup the camera-mode (resolution, binning, image format, ...) and control the exposure time. This Project allows to use the raspberry pi + camera to be used in headless mode by controlling it from an external device (computer).

The Application is used to acquire mostly uncompressed images, depending on network speed and chosen image resolution the framerate might be rather low.

![](Doc/Overview.png)

### Steps to start
- clone repo to raspberry pi and install requirements
- clone repo to computer and install requirements
- configure camera_config.json for the used camera (basic Hq camera provided)
- identify rpi ip address
- run camera_rpi.py on Server (RPI)
- run camera_pc.py on Client (Computer)

### Troubleshooting
- server and client should be able to ping eachother
- camera_config.py has to be identical in the server and client project
- the rpi has to be configured to work in headless mode (without monitor)