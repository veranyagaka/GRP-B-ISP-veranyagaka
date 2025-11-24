import cv2
import torch
import matplotlib.pyplot as plt
from torchvision.transforms.functional import to_pil_image
from PIL import Image
import numpy as np

# --- Set your image path here ---
image_path = '/content/your_image.png'  # replace with your image file

# --- Load image ---
# Convert to grayscale (common for medical images)
img = Image.open(image_path).convert('L')  # 'L' for grayscale
img = np.array(img).astype('float32') / 255.0  # normalize to [0,1]

# Convert to torch tensor [C,H,W]
img_tensor = torch.tensor(img).unsqueeze(0)  # [1,H,W]

# --- Function for bicubic interpolation ---
def bicubic_interpolation(img_tensor, scale=2):
    """
    img_tensor: torch.Tensor [C,H,W], normalized [0,1]
    scale: upscaling factor
    """
    img_np = img_tensor.permute(1,2,0).cpu().numpy()  # HxWxC
    h, w, c = img_np.shape
    new_h, new_w = h*scale, w*scale

    upscaled = cv2.resize(img_np, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    return torch.tensor(upscaled).permute(2,0,1)

# --- Apply bicubic interpolation ---
upscaled_img = bicubic_interpolation(img_tensor, scale=2)

# --- Display ---
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.imshow(to_pil_image(img_tensor))
plt.title('Original Image')
plt.axis('off')

plt.subplot(1,2,2)
plt.imshow(to_pil_image(upscaled_img))
plt.title('Bicubic Interpolation')
plt.axis('off')

plt.show()
