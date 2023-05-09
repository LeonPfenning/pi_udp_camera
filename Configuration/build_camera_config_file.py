import json
from datetime import datetime

now = datetime.now()
calibration_dump = {
    "description": "RPI HQ CAM",
    "datetime": now.strftime("%d/%m/%Y %H:%M:%S"),
    "90": {
        "res": (4056, 3040),
        "forma": "YUV420",
        "img_shape": (4560, 4096)},
    "91": {
        "res": (2028, 1520),
        "forma": "YUV420",
        "img_shape": (2280, 2048)},
    "92": {
        "res": (1014, 760),
        "forma": "YUV420",
        "img_shape": (1140, 1024)},
    "93": {
        "res": (507, 380),
        "forma": "YUV420",
        "img_shape": (570, 512)},
    "default": {
        "res": (2028, 1520),
        "forma": "YUV420",
        "img_shape": (2280, 2048)},

}
json_object = json.dumps(calibration_dump, sort_keys=True, indent=4)
with open("camera_config.json", "w") as outfile:
    outfile.write(json_object)
