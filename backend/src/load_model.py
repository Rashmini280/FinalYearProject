import os
import gdown
import torch

# Models info: local path -> Google Drive file ID
MODELS = {
    "models/singlish_finetuned_model_best.pth": "1sC3tcliF3UrihtEAnQS5f1YSIavKuIDQ",
    "models/fine_tuned_clip_best.pth": "1t-n-jHXNbA4QENutWGIZC4aRNNdKUbzg"
}

# Ensure models folder exists
os.makedirs("models", exist_ok=True)

_singlish_model = None
_clip_model = None

def download_model(path, file_id):
    """Download model from Google Drive if missing"""
    if not os.path.exists(path):
        url = f"https://drive.google.com/uc?id={file_id}"
        print(f"Downloading {os.path.basename(path)} from Google Drive...")
        success = gdown.download(url, path, quiet=False)
        if success is None:
            raise FileNotFoundError(f"Failed to download {os.path.basename(path)}")

def load_singlish_model():
    global _singlish_model
    if _singlish_model is None:
        download_model(
            "models/singlish_finetuned_model_best.pth",
            MODELS["models/singlish_finetuned_model_best.pth"]
        )
        print("Loading Singlish model...")
        _singlish_model = torch.load("models/singlish_finetuned_model_best.pth", map_location="cpu")
    return _singlish_model

def load_clip_model():
    global _clip_model
    if _clip_model is None:
        download_model(
            "models/fine_tuned_clip_best.pth",
            MODELS["models/fine_tuned_clip_best.pth"]
        )
        print("Loading CLIP model...")
        _clip_model = torch.load("models/fine_tuned_clip_best.pth", map_location="cpu")
    return _clip_model