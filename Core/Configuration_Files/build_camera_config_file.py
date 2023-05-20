import json
from datetime import datetime

now = datetime.now()
calibration_dump = {
    "camera": "RPI HQ CAM",
    "description": {
        "image_size": "Resolution of the Image, after postprocessing by the isp",
        "format": "see picamera2-manual page. 64 Appendix A: Pixel and image formats(e.g. YUV420, RGB888)",
        "file_size": "shape of the file that is send",
        "raw_img_format": "initial resolution of the sensor with this resolution the img will be acquired"},
    "datetime": now.strftime("%d/%m/%Y %H:%M:%S"),
    "90": {
        "file_Size": (4560, 4096),
        "format": "YUV420",
        "image_Size": (4056, 3040),
        "raw_img_format": (4056, 3040)},

    "91": {
        "file_Size": (2280, 2048),
        "format": "YUV420",
        "image_Size": (2028, 1520),
        "raw_img_format": (2028, 1520)},

    "92": {
        "file_Size": (1140, 1024),
        "format": "YUV420",
        "image_Size": (1014, 760),
        "raw_img_format": (2028, 1520)},
    "93": {
        "file_Size": (570, 512),
        "format": "YUV420",
        "image_Size": (507, 380),
        "raw_img_format": (2028, 1520)},

    "default": {
        "file_Size": (2280, 2048),
        "format": "YUV420",
        "image_Size": (2028, 1520),
        "raw_img_format": (2028, 1520)},
}

if __name__ == '__main__':
    json_object = json.dumps(calibration_dump, sort_keys=True, indent=4)
    with open("camera_config_HQ.json", "w") as outfile:
        outfile.write(json_object)
    print("configuration file created!")
