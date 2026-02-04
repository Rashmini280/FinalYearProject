import joblib
import torch
import numpy as np
from transformers import AutoTokenizer,AutoModel

# Load the pre-trained XLM-RoBERTa model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
text_model = AutoModel.from_pretrained("xlm-roberta-base")
text_model.eval()# set this to evaluation mode

clf = joblib.load("Models/fake_news_classifier.pkl")
scaler = joblib.load("Models/text_scaler.pkl")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
text_model.to(device)

def encode_text(text:str)-> np.ndarray:
    inputs = tokenizer(
        text,
        return_tensors ="pt",
        truncation = True,
        padding = True,
        max_length = 256
    ).to(device)

    with torch.no_grad():
        outputs = text_model(**inputs)
        embedding = outputs.last_hidden_state[:,0,:] # CLS token embedding for sentence representation

        return embedding.cpu().numpy()
    #predict the probabilities using the loaded classifier and scaler
def predict_text(text:str)-> dict:
    emb = encode_text(text)
    emb = scaler.transform(emb)

    probs = clf.predict_proba(emb)[0]
    classes = clf.clases_
    
    prob_map = dict(zip(classes,probs))

    return{
        "real": float(prob_map.get(1,0.0)),
        "fake" :float(prob_map.get(0,0.0))

    }

