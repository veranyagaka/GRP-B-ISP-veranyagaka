import os
import cv2
import torch
import torch.nn as nn
import numpy as np
import sys, json
import torch.nn.functional as F

# ==============================
# 🧠 Updated Model Definition
# ==============================
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
np.random.seed(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

class PneumoniaCNN(nn.Module):
    def __init__(self, in_channels=1):
        super().__init__()

        def conv_block(in_c, out_c):
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, 3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(inplace=True),
                nn.Conv2d(out_c, out_c, 3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2)
            )

        self.layer1 = conv_block(in_channels, 32)
        self.layer2 = conv_block(32, 64)
        self.layer3 = conv_block(64, 128)
        self.layer4 = conv_block(128, 256)

        self.flatten = nn.Flatten()

        # Fully connected head (for 224×224 input)
        self.fc1 = nn.Linear(256 * 14 * 14, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, 1)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.flatten(x)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x  # raw logit


# ==============================
# ⚙️ Model Loader
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "prediction_model.pth")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = PneumoniaCNN().to(device)

model.load_state_dict(torch.load(MODEL_PATH, map_location=device), strict=False)
model.eval()

LABELS = ["NORMAL", "PNEUMONIA"]


# ==============================
# 🧼 Preprocessing Function
# ==============================
def preprocess_image(image_path, target_size=(224, 224)):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"❌ Unable to read image: {image_path}")

    # ❗ Only resize to model input size (224×224)
    img = cv2.resize(img, target_size)

    # Normalize
    img = img.astype("float32") / 255.0
    mean, std = 0.5, 0.25
    img = (img - mean) / std

    # OOD / invalid image detection
    if np.std(img) < 0.05:
        return "INVALID"

    img = np.expand_dims(img, axis=(0, 1))  # (1,1,224,224)
    tensor = torch.from_numpy(img).to(device)
    return tensor


# ==============================
# 🔮 Prediction Function
# ==============================
def predict_pneumonia(image_path: str):
    data = preprocess_image(image_path)

    if data == "INVALID":
        return {"label": "INVALID_IMAGE", "confidence": 0.0}

    with torch.no_grad():
        output = model(data)

        # Binary classifier → sigmoid
        prob = torch.sigmoid(output).item()

        label = LABELS[1] if prob >= 0.5 else LABELS[0]
        confidence = round(prob * 100, 2) if label == "PNEUMONIA" else round((1 - prob) * 100, 2)

    return {"label": label, "confidence": confidence}


# ==============================
# 🏁 CLI Entry
# ==============================
if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not image_path:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)

    result = predict_pneumonia(image_path)
    print(json.dumps(result))
