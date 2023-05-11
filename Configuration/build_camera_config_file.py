import json
from datetime import datetime

now = datetime.now()
calibration_dump = {
    "camera": "RPI HQ CAM",
    "description": {
        "image_size": "Resolution of the Image",
        "format": "see. picamera2-manual page. 64 Appendix A: Pixel and image formats(e.g. YUV420, RGB888)",
        "file_size": "shape of the file that is send"},
    "datetime": now.strftime("%d/%m/%Y %H:%M:%S"),
    "90": {
        "image_size": (4056, 3040),
        "format": "YUV420",
        "file_size": (4560, 4096)},
    "91": {
        "image_size": (2028, 1520),
        "format": "YUV420",
        "file_size": (2280, 2048)},
    "92": {
        "image_size": (1014, 760),
        "format": "YUV420",
        "file_size": (1140, 1024)},
    "93": {
        "image_size": (507, 380),
        "format": "YUV420",
        "file_size": (570, 512)},
    "default": {
        "image_size": (2028, 1520),
        "format": "YUV420",
        "file_size": (2280, 2048)},
}

json_object = json.dumps(calibration_dump, sort_keys=True, indent=4)
with open("camera_config_HQ.json", "w") as outfile:
    outfile.write(json_object)
