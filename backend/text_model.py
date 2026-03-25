import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# -------------------------
# CONFIG
# -------------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_NAME = "xlm-roberta-base"

# Label mapping (VERY IMPORTANT)
# 0 = Real, 1 = Fake
LABELS = ["real", "fake"]

# -------------------------
# LOAD TOKENIZER + MODEL
# -------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

text_model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2
)

# -------------------------
# LOAD TRAINED WEIGHTS
# -------------------------

# -----------------------------
# Load fine-tuned checkpoint (if exists)
# -----------------------------
checkpoint_path = "Models/singlish_finetuned_model_best.pth"
try:
    text_model.load_state_dict(
        torch.load(checkpoint_path, map_location=DEVICE),strict=False
    )
    print("Fine-tuned Singlish model loaded.")
except Exception as e:
    print("⚠️ singlish_finetuned_model_best.pth not found, using base model.")
    print("Error:", e)

# Move to device + eval mode
text_model.to(DEVICE)
text_model.eval()

# -------------------------
# PREDICTION FUNCTION
# -------------------------
def predict_text(text: str) -> dict:
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    ).to(DEVICE)

    with torch.no_grad():
        outputs = text_model(**inputs)
        probs = F.softmax(outputs.logits, dim=1).cpu().numpy()[0]

    # ✅ CORRECT LABEL MAPPING
    return {
        "real": float(probs[0]),   # index 0 → Real
        "fake": float(probs[1])    # index 1 → Fake
    }