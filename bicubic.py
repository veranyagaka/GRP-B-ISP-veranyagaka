import cv2
import torch
import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
import sys

if len(sys.argv) != 2:
    print("Usage: python3 bicubic_fixed.py <path_to_image>")
    sys.exit(1)

image_path = sys.argv[1]

# --- Load original HR image ---
hr = Image.open(image_path).convert('L')
hr_np = np.array(hr).astype('uint8')

# Step 1: Downsample HR -> LR
scale = 2   # change if needed
h, w = hr_np.shape
lr = cv2.resize(hr_np, (w // scale, h // scale), interpolation=cv2.INTER_CUBIC)

# Step 2: Upscale LR -> SR (bicubic baseline)
bicubic_up = cv2.resize(lr, (w, h), interpolation=cv2.INTER_CUBIC)

# Step 3: Compute metrics against original HR
psnr_value = peak_signal_noise_ratio(hr_np, bicubic_up, data_range=255)
ssim_value = structural_similarity(hr_np, bicubic_up, data_range=255)

print("Correct Bicubic PSNR:", psnr_value)
print("Correct Bicubic SSIM:", ssim_value)
