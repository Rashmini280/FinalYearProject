from cProfile import label
from fastapi import FastAPI, Form,UploadFile,File
import shutil
import uuid


from ocr import extract_text
from singlish_normalizer import ProfessionalNormalizer
from text_model import encode_text,clf,scaler
from clip_model import clipsimilarity,final_decision
from utils import selective_singlish_normalize,clean_text


app = FastAPI()

normalizer = ProfessionalNormalizer()


@app.post("/predict_text")
async def predict_text_only(text: str = Form(...)):

    
    normalized_text = selective_singlish_normalize(text,normalizer)
    normalized_text = clean_text(normalized_text)
    
    emb = encode_text(normalized_text)
    emb = scaler.transform(emb)


    probs = clf.predict_proba(emb)[0]
    classes = clf.classes_
    prob_map = dict(zip(classes,probs))
    
    real_prob = float(prob_map.get(1,0.0))
    fake_prob = float(prob_map.get(0,0.0))

    

    label = "Real" if real_prob > fake_prob else "Fake"

    return{
        "input_text" :text,
        "normalized_text" : normalized_text,
        "text_probs":{"real": real_prob, "fake": fake_prob},
        "label": label
    }



@app.post("/predict")
async def predict_meme(file:UploadFile= File(...)):
    path = f"temp_{uuid.uuid4().hex}.jpg"
    with open(path,"wb") as buffer: 
        shutil.copyfileobj(file.file,buffer)

    ocr_text = extract_text(path)
    
    normalized_text = selective_singlish_normalize(ocr_text,normalizer)
    normalized_text = clean_text(normalized_text)
    
    emb = encode_text(normalized_text)
    emb = scaler.transform(emb)
    probs = clf.predict_proba(emb)[0]
    classes = clf.classes_
    prob_map = dict(zip(classes,probs))
    
    real_prob = float(prob_map.get(1,0.0))
    fake_prob = float(prob_map.get(0,0.0))

    # text_probs = predict_text(normalized_text)
    clip_sim = max(
        clipsimilarity(path, normalized_text[:200]),
        clipsimilarity(path,ocr_text[:200])
    )
    decision = final_decision(
        {"real": real_prob, "fake": fake_prob},
             clip_sim)
    return{
        "ocr_text" :ocr_text,
        "normalized_text" : normalized_text,
        "text_probs":{"real": real_prob, "fake": fake_prob},
        "clip_similarity": clip_sim,
        "final_decision": decision
    }

       
   