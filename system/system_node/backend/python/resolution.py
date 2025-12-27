import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import numpy as np
import math
import os
import sys
import json
from skimage.metrics import structural_similarity as ssim

# -----------------------------
# 1️⃣ SRCNN Model Definition
# -----------------------------
class SRCNN(nn.Module):
    def __init__(self):
        super(SRCNN, self).__init__()
        self.layer1 = nn.Conv2d(1, 64, kernel_size=9, padding=4)
        self.layer2 = nn.Conv2d(64, 32, kernel_size=1)
        self.layer3 = nn.Conv2d(32, 1, kernel_size=5, padding=2)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return x


# -----------------------------
# 2️⃣ Load Model
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SRCNN().to(device)

model_path = os.path.join(os.path.dirname(__file__), "srcnn_xray.pth")
if not os.path.exists(model_path):
    print(json.dumps({"error": "Trained model weights 'srcnn_xray.pth' not found."}))
    sys.exit(1)

model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()


# -----------------------------
# 3️⃣ Preprocessing & Metrics
# -----------------------------
to_tensor = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((128, 128)),
    transforms.ToTensor()
])
to_pil = transforms.ToPILImage()

def mse_metric(y_true, y_pred):
    return torch.mean((y_true - y_pred) ** 2).item()

def psnr_metric(y_true, y_pred):
    mse = mse_metric(y_true, y_pred)
    if mse == 0:
        return 100
    return 20 * math.log10(1.0 / math.sqrt(mse))

def ssim_metric(y_true, y_pred):
    y_true = y_true.squeeze().cpu().numpy()
    y_pred = y_pred.squeeze().cpu().numpy()
    return ssim(y_true, y_pred, data_range=1.0)


# -----------------------------
# 4️⃣ Enhancement Function
# -----------------------------
def enhance_image(file_path):
    input_image = Image.open(file_path).convert("L")
    input_img = to_tensor(input_image).unsqueeze(0).to(device)

    # Simulate low-res by downsampling and upsampling
    pil_lr = input_image.resize((64, 64), Image.BICUBIC).resize((128, 128), Image.BICUBIC)
    lr_tensor = to_tensor(pil_lr).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(lr_tensor)

    # Compute metrics
    mse_val = mse_metric(input_img, output)
    psnr_val = psnr_metric(input_img, output)
    ssim_val = ssim_metric(input_img, output)

    enhanced_img = to_pil(output.squeeze(0).cpu())
    caption = f"PSNR: {psnr_val:.2f}, SSIM: {ssim_val:.4f}, MSE: {mse_val:.6f}"

    return enhanced_img, caption


# -----------------------------
# 5️⃣ Main Execution for Node
# -----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(json.dumps({"error": f"Image not found at {input_path}"}))
        sys.exit(1)

    try:
        enhanced_img, caption = enhance_image(input_path)

        # Save enhanced image
        output_dir = os.path.join(os.path.dirname(__file__), "../uploads")
        os.makedirs(output_dir, exist_ok=True)

        output_filename = "enhanced_" + os.path.basename(input_path)
        output_path = os.path.join(output_dir, output_filename)
        enhanced_img.save(output_path)

        # Print JSON result for Node controller
        result = {
            "message": "Image enhanced successfully",
            "metrics": caption,
            "output_path": f"uploads/{output_filename}"
        }
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
