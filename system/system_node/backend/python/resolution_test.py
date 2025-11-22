import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image, ImageFilter
import numpy as np
import math
import os
import sys
import json
from skimage.metrics import structural_similarity as ssim

# -----------------------------
# 1️⃣ Improved SRCNN Model (Strong SR)
# -----------------------------
class SRCNN(nn.Module):
    def __init__(self):
        super(SRCNN, self).__init__()
        self.layer1 = nn.Conv2d(1, 64, kernel_size=9, padding=4)
        self.layer2 = nn.Conv2d(64, 32, kernel_size=1)   # MUST BE 1×1 (your checkpoint)
        self.layer3 = nn.Conv2d(32, 1, kernel_size=5, padding=2)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return x

# Load Model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SRCNN().to(device)

model_path = os.path.join(os.path.dirname(__file__), "srcnn_xray.pth")
if not os.path.exists(model_path):
    print(json.dumps({"error": "SRCNN weights not found"}))
    sys.exit(1)

model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

# -----------------------------
# 3️⃣ Preprocessing & Metrics
# -----------------------------
to_tensor = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

to_pil = transforms.ToPILImage()

def mse_metric(y_true, y_pred):
    return torch.mean((y_true - y_pred) ** 2).item()

def psnr_metric(y_true, y_pred):
    mse = mse_metric(y_true, y_pred)
    return 100 if mse == 0 else 20 * math.log10(1.0 / math.sqrt(mse))

def ssim_metric(y_true, y_pred):
    y_true = y_true.squeeze().cpu().numpy()
    y_pred = y_pred.squeeze().cpu().numpy()
    return ssim(y_true, y_pred, data_range=1.0)

# -----------------------------
# 4️⃣ Enhancement Function
# -----------------------------
def enhance_image(file_path):
    img = Image.open(file_path).convert("L")

    # 1. ⭐ Light denoising
    img = img.filter(ImageFilter.MedianFilter(size=3))

    # 2. ⭐ Convert to tensor
    input_tensor = to_tensor(img).unsqueeze(0).to(device)

    # 3. ⭐ Super-resolution enhancement
    with torch.no_grad():
        sr = model(input_tensor)

    # 4. ⭐ Enhance edges (helps pneumonia detection)
    sr_np = sr.squeeze().cpu().numpy()
    sobel = np.abs(np.gradient(sr_np)[0]) + np.abs(np.gradient(sr_np)[1])
    sr_np = sr_np + 0.2 * sobel  # boost edges slightly

    sr_final = torch.tensor(sr_np).clamp(0, 1).unsqueeze(0).unsqueeze(0)

    # 5. Convert back to image
    enhanced_img = to_pil(sr_final.squeeze())

    # Metrics (optional)
    mse_val = mse_metric(input_tensor, sr)
    psnr_val = psnr_metric(input_tensor, sr)
    ssim_val = ssim_metric(input_tensor, sr)

    caption = f"PSNR {psnr_val:.2f}, SSIM {ssim_val:.4f}, MSE {mse_val:.6f}"

    return enhanced_img, caption

# -----------------------------
# 5️⃣ Main Execution
# -----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(json.dumps({"error": f"Image not found: {input_path}"}))
        sys.exit(1)

    try:
        enhanced_img, caption = enhance_image(input_path)

        output_dir = os.path.join(os.path.dirname(__file__), "../uploads")
        os.makedirs(output_dir, exist_ok=True)

        output_file = "enhanced_" + os.path.basename(input_path)
        output_path = os.path.join(output_dir, output_file)
        enhanced_img.save(output_path)

        print(json.dumps({
            "message": "Image enhanced successfully",
            "metrics": caption,
            "output_path": f"uploads/{output_file}"
        }))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
