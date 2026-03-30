This project presents a multimodal fake news detection system designed for Singlish (Sinhala-English code-mixed language). The system analyzes both text and images (memes) using OCR, transformer-based models, and multimodal fusion to classify content as Real or Fake.


First, it needs to create a virtual environmanet for the installing the project packages . 
and after creating python -m venev venev, then venv should be activated . using venv\Scripts\activate .
the required packages can be found in requirements.txt file in the backend folder. to run the backend it is need to direct to the backend and should run uvicorn app:app.
then to test the backend after running the backend http://127.0.0.1:8000/docs , this helps to test the endpoint of /predict , this one for meme and /predict_text for text.


Frontend need to create using react.js . and frontend will send the requests and fastapi backend will respond to them and give the prediction. Cors Middleware and proper endpoints will be used to 
connect frontend and backend

Features are as follows

Text based news detection using XLM-Roberta 

Image and Text similarity based news detection using CLIP Model

OCR (Tessearact OCR for extract text from images)

Multimodal Fusion Output

Confidence Score Output

Frontend :- Html, Css and Java Script
Backend :- FastAPI/ Python
ML Models : Pytorch, XLM-R ,CLIP
OCR : Tesseract OCR

First clone the github reporsitory 

create a virtual environment python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

cd backend

uvicorn app:app --reload

The models have not included in the Github repository due to the storage limits so , after cloning the prohect create a folder called Models and include these two models. Go to the google drive links and download it to your device. 
singlish_finetuned_model.pth - https://drive.google.com/file/d/1sC3tcliF3UrihtEAnQS5f1YSIavKuIDQ/view?usp=sharing
fine_tuned_clip_best.pth - https://drive.google.com/file/d/1t-n-jHXNbA4QENutWGIZC4aRNNdKUbzg/view?usp=sharing


The project will run in  http://127.0.0.1:8000 

The login page will display.


