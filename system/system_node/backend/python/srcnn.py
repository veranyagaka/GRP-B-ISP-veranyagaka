#!/usr/bin/env python3
import sys
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
import os 
import json

# ------------------------------
# Define SRCNN model
# ------------------------------
class SRCNN(nn.Module):
    def __init__(self):
        super(SRCNN, self).__init__()
        self.layer1 = nn.Conv2d(1, 64, kernel_size=9, padding=4)
        self.layer2 = nn.Conv2d(64, 32, kernel_size=5, padding=2)
        self.layer3 = nn.Conv2d(32, 1, kernel_size=5, padding=2)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return x


# ------------------------------
# CLI Argument
# ------------------------------
if len(sys.argv) != 2:
    print(json.dumps({"error": "No image path provided"}))
    sys.exit(1)

img_path = sys.argv[1]

# ------------------------------
# Device setup
# ------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ------------------------------
# Load model
# ------------------------------
model = SRCNN().to(device)
model.load_state_dict(torch.load("srcnn_xray_improved.pth", map_location=device))
model.eval()

# ------------------------------
# Load and preprocess image
# ------------------------------
hr = Image.open(img_path).convert("L")

# Upsample to 1024×1024
target_size = (1024, 1024)
lr_up = hr.resize(target_size, Image.Resampling.BICUBIC)

to_tensor = transforms.ToTensor()
lr_tensor = to_tensor(lr_up).unsqueeze(0).to(device)

# ------------------------------
# Run model
# ------------------------------
with torch.no_grad():
    sr_tensor = model(lr_tensor)

# Convert output to image
sr_img = sr_tensor.squeeze().cpu().numpy()
sr_img = np.clip(sr_img * 255, 0, 255).astype("uint8")
sr_pil = Image.fromarray(sr_img)

# ------------------------------
# Save output image
# ------------------------------
output_dir = os.path.join(os.path.dirname(__file__), "../uploads")
os.makedirs(output_dir, exist_ok=True)

output_filename = "enhanced_" + os.path.basename(img_path)
output_path = os.path.join(output_dir, output_filename)

sr_pil.save(output_path)

# ------------------------------
# Compute PSNR + SSIM
# ------------------------------
hr_resized = np.array(hr.resize(target_size, Image.BICUBIC)).astype("uint8")

psnr_value = peak_signal_noise_ratio(hr_resized, sr_img, data_range=255)
ssim_value = structural_similarity(hr_resized, sr_img, data_range=255)

caption = f"PSNR {psnr_value:.2f}, SSIM {ssim_value:.4f}"

# ------------------------------
# Return JSON (MATCHES SCRIPT 2)
# ------------------------------
print(json.dumps({
    "message": "Image enhanced successfully",
    "metrics": caption,
    "output_path": f"uploads/{output_filename}"
}))
