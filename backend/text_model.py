import os
import gdown
import torch
import clip
import torch.nn as nn

# Models info: local path -> Google Drive file ID
MODELS = {
    "models/singlish_finetuned_model_best.pth": "1sC3tcliF3UrihtEAnQS5f1YSIavKuIDQ",
    "models/fine_tuned_clip_best.pth": "1t-n-jHXNbA4QENutWGIZC4aRNNdKUbzg"
}

# Ensure models folder exists
os.makedirs("models", exist_ok=True)

_singlish_model = None
_clip_model = None
_clip_preprocess = None
_clip_classifier = None

# -------------------------
# HELPER: Download from Google Drive
# -------------------------
def download_model(path, file_id):
    """Download model from Google Drive if missing"""
    if not os.path.exists(path):
        url = f"https://drive.google.com/uc?id={file_id}"
        print(f"Downloading {os.path.basename(path)} from Google Drive...")
        success = gdown.download(url, path, quiet=False)
        if success is None:
            raise FileNotFoundError(f"Failed to download {os.path.basename(path)}")

# -------------------------
# LOAD SINGLISH MODEL
# -------------------------
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

# -------------------------
# LOAD CLIP MODEL + CLASSIFIER
# -------------------------
def load_clip_model():
    global _clip_model, _clip_preprocess, _clip_classifier
    if _clip_model is None:
        download_model(
            "models/fine_tuned_clip_best.pth",
            MODELS["models/fine_tuned_clip_best.pth"]
        )
        print("Loading CLIP model...")

        # Load base CLIP model
        _clip_model, _clip_preprocess = clip.load("ViT-B/32", device="cpu")
        _clip_model.eval()

        # Load classifier
        _clip_classifier = nn.Linear(_clip_model.visual.output_dim, 2)
        checkpoint = torch.load("models/fine_tuned_clip_best.pth", map_location="cpu")
        _clip_classifier.load_state_dict(checkpoint["classifier_state_dict"])
        _clip_classifier.eval()

    return _clip_model, _clip_classifier, _clip_preprocess