import cv2
import os
from pathlib import Path

def downsample_images(input_dir, output_dir, scale=2):
    os.makedirs(output_dir, exist_ok=True)
    for file in Path(input_dir).glob("*.png"):
        img = cv2.imread(str(file), cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        low_res = cv2.resize(img, (w // scale, h // scale), interpolation=cv2.INTER_CUBIC)
        low_res = cv2.resize(low_res, (w, h), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(output_dir, file.name), low_res)
