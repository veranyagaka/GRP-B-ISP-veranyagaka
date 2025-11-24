#!/usr/bin/env python3
import sys
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

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
    print("Usage: python3 srcnn.py <path_to_image>")
    sys.exit(1)

img_path = sys.argv[1]

# ------------------------------
# Device setup
# ------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# ------------------------------
# Load model
# ------------------------------
model = SRCNN().to(device)
model.load_state_dict(torch.load("srcnn_xray_improved.pth", map_location=device))
model.eval()

# ------------------------------
# Load and preprocess image
# ------------------------------
hr = Image.open(img_path)     # assume already grayscale

# Upsample to 1024×1024 for SRCNN
target_size = (1024, 1024)
lr_up = hr.resize(target_size, Image.Resampling.BICUBIC)
lr_up.save("lr_image.jpeg")

# Convert to tensor
to_tensor = transforms.ToTensor()
lr_tensor = to_tensor(lr_up).unsqueeze(0).to(device)

# ------------------------------
# Run model
# ------------------------------
with torch.no_grad():
    sr_tensor = model(lr_tensor)

# Convert model output to image
sr_img = sr_tensor.squeeze().cpu().numpy()
sr_img = np.clip(sr_img * 255, 0, 255).astype("uint8")
sr_img_display = Image.fromarray(sr_img)

# ------------------------------
# Save SR output
# ------------------------------
sr_img_display.save("sr_image.jpeg")
print("Super-resolved image saved as sr_image.jpeg")

# ------------------------------
# Compute PSNR and SSIM
# ------------------------------
hr_resized = np.array(hr.resize(target_size, Image.BICUBIC)).astype("uint8")
sr_eval = sr_img

psnr_value = peak_signal_noise_ratio(hr_resized, sr_eval, data_range=255)
ssim_value = structural_similarity(hr_resized, sr_eval, data_range=255)

print("PSNR:", psnr_value)
print("SSIM:", ssim_value)

# ------------------------------
# Export classifier-ready image
# ------------------------------
classifier_size = (224, 224)
sr_img_classifier = sr_img_display.resize(classifier_size, Image.BICUBIC)
sr_np = np.array(sr_img_classifier).astype("float32") / 255.0
sr_tensor_for_classifier = torch.from_numpy(sr_np).unsqueeze(0).unsqueeze(0).to(device)

sr_img_classifier.save("sr_image_classifier.jpeg")
np.save("sr_tensor_for_classifier.npy", sr_tensor_for_classifier.cpu().numpy())

print("Classifier-ready image saved as sr_image_classifier.jpeg")
print("Classifier tensor saved as sr_tensor_for_classifier.npy")
