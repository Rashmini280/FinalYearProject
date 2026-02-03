import torch
import clip
from PIL import Image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model,preprocess = clip.load("ViT-B/32", device= device)

def clipsimilarity(image_path:str, text:str)-> float:
    text = text[:200]
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    text = clip.tokenize([text], truncate=True).to(device)

    with torch.no_grad():
        image_features= model.encode_image(image)
        text_features = model.encode_text(text)

        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        similarity = (image_features @ text_features.T).item()

        return similarity
    
def final_decision(text_probs:dict, clip_sim:float) -> dict:
    if clip_sim > 0.28:
            if text_probs["fake"] < 0.98:
                return {
                    "label": "Real",
                    "reason": "High visual-text consistency",
                    "confidence": clip_sim
            }
    if clip_sim > 0.15:
             return {
                "label": "Fake",
                "reason": "Visual and Text do not match",
                "confidence": 0.85
    }
        
   # Note: (1 - clip_sim) is used because high similarity should decrease the fake score.
    fake_score = (text_probs["fake"] * 0.6) + ((1 - clip_sim) * 0.4)

    if fake_score > 0.65:
        return {
            "label": "Fake",
            "reason": "Textual markers indicate misinformation",
            "confidence": float(fake_score)
        }
    
    return {
        "label": "Real",
        "reason": "Consistent multimodal content",
        "confidence": text_probs["real"]
    }