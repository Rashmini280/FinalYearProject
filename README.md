First, it needs to create a virtual environmanet for the installing the project packages . and after creating python -m venev venev, then venv should be activated . using venv\Scripts\activate .
the required packages can be found in requirements.txt file in the backend folder. to run the backend it is need to direct to the backend and should run uvicorn app:app.
then to test the backend after running the backend http://127.0.0.1:8000/docs , this helps to test the endpoint of /predict , this one for meme and /predict_text for text.


Frontend need to create using react.js . and frontend will send the requests and fastapi backend will respond to them and give the prediction. Cors Middleware and proper endpoints will be used to 
connect frontedn and backend
