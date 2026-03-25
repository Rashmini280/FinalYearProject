import torch
import clip
from PIL import Image
import torch.nn as nn

# -------------------------
# CONFIG
# -------------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Label mapping (IMPORTANT)
# 0 = Real, 1 = Fake
LABELS = ["real", "fake"]

# -------------------------
# LOAD CLIP MODEL
# -------------------------
model, preprocess = clip.load("ViT-B/32", device=DEVICE)

# -------------------------
# LOAD CLASSIFIER
# -------------------------
classifier = nn.Linear(model.visual.output_dim, 2).to(DEVICE)

checkpoint = torch.load("Models/fine_tuned_clip_best.pth", map_location=DEVICE)
classifier.load_state_dict(checkpoint["classifier_state_dict"])

# Set eval mode
model.eval()
classifier.eval()

# -------------------------
# IMAGE PREDICTION
# -------------------------
def predict_image(image_path: str):

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        features = model.encode_image(image).float()
        features = features / features.norm(dim=-1, keepdim=True)

        outputs = classifier(features)
        probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]

    # ✅ CORRECT mapping
    return {
        "real": float(probs[0]),   # index 0 → Real
        "fake": float(probs[1])    # index 1 → Fake
    }

# -------------------------
# FINAL DECISION (UNCHANGED)
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