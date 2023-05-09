from picamera2 import Picamera2
import time
import io

''' Benchmarking and Test Script for Camera Data acquisition '''
''' - Check acquisition speed '''
''' - Check file size '''

picam2 = Picamera2()
res = (4056, 3040)
res = (2028, 1520)
#res = (1520, 2028)
#res = (1014, 760)
#res = (507, 380)
forma = "YUV420"
#forma = "BGR888"
config = picam2.create_still_configuration(buffer_count=1, main={"size": res,
                                                                 "format": forma},
                                           queue=False)
picam2.configure(config)
picam2.set_controls({"ExposureTime": int(300),  # 1,000,000 --> 1 sec.
                     "AnalogueGain": 1.0,
                     "AeEnable": False,
                     "AwbEnable": False,
                     "NoiseReductionMode": False})
picam2.still_configuration.align()


test_case = 1       # 2, 3
picam2.start()
array = picam2.capture_array("main")

print("start...")
img_count = 200
t = time.time()
for i in range(img_count):
    print(i)
    if test_case == 1:
        array = picam2.capture_array("main")
        stream = array.tobytes()
        print(len(stream))
    elif test_case == 2:
        array =picam2.capture_buffer("main")
        stream = array.tobytes()
        print(len(stream))
    elif test_case == 3:
        stream = io.BytesIO()
        picam2.capture_file(stream, format='jpeg')  # very slow 40 seconds
        print(stream.tell())
    else:
        print("unknown test case")
        break

elapsed = time.time() - t
print(elapsed, "sec.")
print(img_count/elapsed, "HZ")
print(array.shape)

picam2.stop()
picam2.close()
