import torch
import clip
from PIL import Image
import torch.nn as nn

# =========================
# CONFIG
# =========================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Label mapping
# 0 = Real, 1 = Fake
LABELS = ["real", "fake"]

# =========================
# LOAD MODEL
# =========================
model, preprocess = clip.load("ViT-B/32", device=DEVICE)

# Classifier (same as training)
classifier = nn.Linear(model.visual.output_dim, 2).to(DEVICE)

# =========================
# LOAD CHECKPOINT (FIXED)
# =========================
checkpoint = torch.load("Models/fine_tuned_clip_best.pth", map_location=DEVICE)

# ✅ Load classifier
classifier.load_state_dict(checkpoint["classifier_state_dict"])

# ✅ CRITICAL FIX: Load fine-tuned CLIP visual backbone
model.visual.load_state_dict(checkpoint["visual_state_dict"])

# =========================
# SET EVAL MODE
# =========================
model.eval()
classifier.eval()

# =========================
# IMAGE PREDICTION
# =========================
def predict_image(image_path: str):
    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        features = model.encode_image(image).float()

        # same normalization used in training
        features = features / features.norm(dim=-1, keepdim=True)

        outputs = classifier(features)
        probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]

    return {
        "real": float(probs[0]),   # index 0 → Real
        "fake": float(probs[1])    # index 1 → Fake
    }

# =========================
# FINAL DECISION (IMPROVED)
# =========================
def final_decision(text_probs, image_probs):
    fake_score = (text_probs["fake"] * 0.5) + (image_probs["fake"] * 0.5)

    # Optional: uncertainty handling (recommended)
    if fake_score > 0.65:
        return {
            "label": "Fake",
            "reason": "Text and image analysis indicates misinformation",
            "confidence": float(fake_score)
        }

    elif fake_score < 0.35:
        return {
            "label": "Real",
            "reason": "Consistent multimodal content",
            "confidence": float(1 - fake_score)
        }

    else:
        return {
            "label": "Uncertain",
            "reason": "Model is not confident",
            "confidence": float(1 - abs(fake_score - 0.5))
        }