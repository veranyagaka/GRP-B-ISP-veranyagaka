import os
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

# ==============================
# 🧠 Model Definition (Same as Training)
# ==============================
class PneumoniaCNN(nn.Module):
    def __init__(self, in_channels=1, num_classes=2):
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
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(0.4)
        self.fc = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        return x


# ==============================
# ⚙️ Model Loader
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "prediction_model.pth")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = PneumoniaCNN(num_classes=2).to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

LABELS = ["NORMAL", "PNEUMONIA"]


# ==============================
# 🧼 Preprocessing Function
# ==============================
def preprocess_image(image_path, target_size=(224, 224)):
    """
    Preprocess the image exactly as during training:
    1. Convert to grayscale
    2. Resize to 224x224
    3. Normalize to [0,1]
    4. Expand dims to (1, 1, 224, 224)
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"❌ Unable to read image: {image_path}")

    img = cv2.resize(img, target_size)
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=(0, 1))  # (1, 1, 224, 224)

    tensor = torch.from_numpy(img).to(device)
    return tensor


# ==============================
# 🔮 Prediction Function
# ==============================
def predict_pneumonia(image_path: str):
    """
    Run inference on a single image.
    Returns: {"label": "NORMAL"/"PNEUMONIA", "confidence": float}
    """
    try:
        tensor = preprocess_image(image_path)
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = F.softmax(outputs, dim=1)
            pred_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][pred_class].item()
           

        return LABELS[pred_class], round(confidence * 100, 2)
        

    except Exception as e:
        return {"error": str(e)}
