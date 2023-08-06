___
## What to expect in terms of fps (HQ Camera)
Keep in mind: We acquire and send uncompressed still images. The application is not targeting fast fps image streaming!
Depending on used hardware, network speed and chosen camera settings the resulting framerate might be different.

Network limitations - file transfer (mathematical example):

|format  | resolution | formular      | file size (uncompressed) | theoretical fps (1Gbit/s)   | 
|------- |------------|---------------|--------------------------|-----------------------------|
|bgr888  | 4056x3040  | h * w * 3     | ~37.0 Mbyte              | ~3                          |
|yuv420  | 4056x3040  | h * w * (3/2) | ~18.5 Mbyte              | ~7                          |
|bgr888  | 2028x1520  | h * w * 3     | ~9.3 Mbyte               | ~14                         |
|yuv420  | 2028x1520  | h * w * (3/2) | ~4.6 Mbyte               | ~25                         |
|bgr888  | 1014x760   | h * w * 3     | ~2.3 Mbyte               | ~14                         |
|yuv420  | 1014x760   | h * w * (3/2) | ~1.2 Mbyte               | ~25                         |
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

|format  | resolution | images taken | duration | measured fps | 
|------- |------------|--------------|----------|--------------|
|bgr888  | 4056x3040  | 200          | 60 sec.  | 3            |
|yuv420  | 4056x3040  | 600          | 78 sec.  | 8            |
|bgr888  | 2028x1520  | 2000         | 162 sec. | 12           |
|yuv420  | 2028x1520  | 2000         | 85 sec.  | 23           |
|bgr888  | 1014x760   | 600          | 15 sec.  | 40¹          |
|yuv420  | 1014x760   | 600          | 15 sec.  | 40¹          |
|bgr888  | 507x380    | 600          | 15 sec.  | 40¹          |
|yuv420  | 507x380    | 600          | 15 sec.  | 40¹          |
¹ capped by sensor_mode: full FOV max 40fps
#

Actual speed measured with ethernet connection (measured):

|format  | resolution  | images taken | duration  | measured fps     |
|------- |-------------|--------------|-----------|------------------|
|bgr888  | 4056x3040   | --           | --        | not implemented  |
|yuv420  | 4056x3040   | 50           | 16 sec.   | 3                |
|bgr888  | 2028x1520   | --           | --        | not implemented  |
|yuv420  | 2028x1520   | 50           | 5 sec.    | 10               |
|bgr888  | 1014x760    | --           | --        | not implemented  |
|yuv420  | 1014x760    | 50           | 1.25 sec. | 40               |
