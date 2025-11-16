[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/blswXyO9)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20166300&assignment_repo_type=AssignmentRepo)

# SRCNN: Super-Resolution Convolutional Neural Network

This project implements an **SRCNN (Super-Resolution Convolutional Neural Network)** to enhance low-resolution images by reconstructing high-resolution details. The model is based on the seminal paper *"Image Super-Resolution Using Deep Convolutional Networks"* by Dong et al.

---

## 📌 Features
- Implementation of a basic SRCNN model using deep learning.
- Trains on low-resolution and high-resolution image pairs.
- Evaluates results using metrics such as **PSNR** and **SSIM**.
- Supports inference on custom input images.

---

## 📂 Project Structure

- `my-project/`
  - `src/`
    - `main.py`
    - `utils.py`
  - `tests/`
    - `test_main.py`
  - `data/`
    - `README.md`
    - `CONTRIBUTING.md`
  - `requirements.txt`
  - `ml/`
    - `models/`
    - `notebooks`
    - `results`
  - `.gitignore`
  - `README.md`
  - 


## Usage
1. Super-resolving an image
```bash
python3.11 resolution.py /path/to/image
```

2. Prediction of an image
```bash
python3.11 predictor.py /path/to/image
```

## Hugging Face Spaces
https://huggingface.co/spaces/veranyagaka/srcnn

https://huggingface.co/spaces/veranyagaka/super-resolution

## Evaluation Metrics
The metrics used to assess performance:

- **PSNR** (Peak Signal-to-Noise Ratio): Measures the reconstruction quality; higher is better.

- **SSIM** (Structural Similarity Index): Evaluates perceived image quality based on luminance and structure.
  
## References

