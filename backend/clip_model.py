# clipmodel.py
import os
import torch
import clip
from PIL import Image
import torch.nn as nn
import gdown

# -------------------------
# CONFIG
# -------------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Label mapping (IMPORTANT)
# 0 = Real, 1 = Fake
LABELS = ["real", "fake"]

# -------------------------
# MODEL FILE INFO
# -------------------------
MODELS = {
    "models/fine_tuned_clip_best.pth": "1t-n-jHXNbA4QENutWGIZC4aRNNdKUbzg"
}

# Ensure models folder exists
os.makedirs("models", exist_ok=True)

# Global variables
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
# LOAD CLIP MODEL + CLASSIFIER
# -------------------------
def load_clip_model():
    global _clip_model, _clip_preprocess, _clip_classifier
    if _clip_model is None:
        # Download checkpoint if missing
        download_model(
            "models/fine_tuned_clip_best.pth",
            MODELS["models/fine_tuned_clip_best.pth"]
        )

        print("Loading CLIP model...")
        # Load base CLIP
        _clip_model, _clip_preprocess = clip.load("ViT-B/32", device=DEVICE)
        _clip_model.eval()

        # Load classifier
        _clip_classifier = nn.Linear(_clip_model.visual.output_dim, 2).to(DEVICE)
        checkpoint = torch.load("models/fine_tuned_clip_best.pth", map_location=DEVICE)
        _clip_classifier.load_state_dict(checkpoint["classifier_state_dict"])
        _clip_classifier.eval()

    return _clip_model, _clip_classifier, _clip_preprocess

# -------------------------
# IMAGE PREDICTION
# -------------------------
def predict_image(image_path: str):
    model, classifier, preprocess = load_clip_model()

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        features = model.encode_image(image).float()
        features = features / features.norm(dim=-1, keepdim=True)
        outputs = classifier(features)
        probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]

    return {
        "real": float(probs[0]),   # index 0 → Real
        "fake": float(probs[1])    # index 1 → Fake
    }

# -------------------------
# FINAL DECISION
# -------------------------
def final_decision(text_probs, image_probs):
    fake_score = (text_probs["fake"] * 0.6) + (image_probs["fake"] * 0.4)

    if fake_score > 0.6:
        return {
            "label": "Fake",
            "reason": "Text and image analysis indicates misinformation",
            "confidence": float(fake_score)
        }

    return {
        "label": "Real",
        "reason": "Consistent multimodal content",
        "confidence": float(1 - fake_score)
    }