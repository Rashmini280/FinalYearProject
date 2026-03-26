from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Form, UploadFile, File,Request
from fastapi.responses import  HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI



import shutil, uuid, os
import sqlite3

from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from fastapi.responses import FileResponse

from fastapi import FastAPI, Form, UploadFile, File
from ocr import extract_text
from singlish_normalizer import ProfessionalNormalizer
from text_model import predict_text
from clip_model import predict_image, final_decision
from utils import selective_singlish_normalize, clean_text
from starlette.middleware.sessions import SessionMiddleware

from database import add_user,verify_user,save_prediction



app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

normalizer = ProfessionalNormalizer()

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    if "username" in request.session:
        role = request.session.get("role")

        if role == "admin":
            return RedirectResponse("/admin-dashboard",status_code = 303)
        
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...),password: str = Form(...)):
    success = add_user(username, password)

    if success:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("register.html",{
        "request": request,
        "error": "Username already exists. Try a different one."
    })

@app.post("/login")
async def login(request: Request, username:str = Form(...), password:str = Form(...)):
    role = verify_user(username,password)
    if role:
        request.session["username"] = username
        request.session["role"] = role # Assuming role is the 4th column

        if role == "admin":
            return RedirectResponse("/admin-dashboard", status_code=303)
        return RedirectResponse("/dashboard", status_code=303)
    
    return templates.TemplateResponse("login.html" , {
        "request" : request,
        "error": "Invalid username or password. Please try again."
    })

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()  # clears username, role, etc.
    return RedirectResponse("/", status_code=303)  # redirect to login page

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if "username" not in request.session:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/view-report", response_class=HTMLResponse)
def view_report(request: Request, created_at: str):
    username = request.session.get("username")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT input_text, ocr_text, prediction, confidence, created_at
        FROM history
        WHERE username = ? AND created_at = ?
    """, (username, created_at))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return HTMLResponse("Report not found")

    return templates.TemplateResponse("report.html", {
        "request": request,
        "data": {
            "input_text": row[0],
            "ocr_text": row[1],
            "prediction": row[2],
            "confidence": row[3],
            "created_at": row[4]
        }
    })


@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if  request.session.get("role") !="admin":
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("admin.html", {"request": request})



@app.get("/admin/user-activity/{username}",response_class=HTMLResponse)
async def user_activity(request: Request, username: str):
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=303)
    
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    query = """
        SELECT input_text, ocr_text, prediction, confidence, created_at
        FROM history
        WHERE username = ?
    """
    params = [username]

    if start_date:
        query += " AND date(created_at) >= date(?)"
        params.append(start_date)
    if end_date:
        query += " AND date(created_at) <= date(?)"
        params.append(end_date)

    query += "ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "input_text": row[0],
            "ocr_text": row[1],
            "prediction": row[2],
            "confidence": row[3],
            "created_at": row[4]
        })

    return templates.TemplateResponse("useractivity.html", {
        "request": request,
        "history": history,
        "username": username,
        "start_date" : start_date,
        "end_date":end_date
    })



@app.get("/admin/history")
def get_all_history(request: Request):
    if request.session.get("role") != "admin":
        return {"error": "Unauthorized"}

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, input_text, ocr_text, prediction, confidence, created_at
        FROM history
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "username": row[0],
            "input_text": row[1],
            "ocr_text": row[2],
            "prediction": row[3],
            "confidence": row[4],
            "created_at": row[5]
        })

    return {"history": history}

@app.delete("/admin/delete-user/{username}")
def delete_user(request: Request, username: str):
    if request.session.get("role") != "admin":
        return {"error": "Unauthorized"}

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()

    return {"message": f"User '{username}' deleted successfully."}

@app.delete("/admin/delete-history/{created_at}")
def delete_history(created_at: str, request: Request):
    if request.session.get("role") != "admin":
        return {"error": "Unauthorized"}

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM history WHERE created_at=?", (created_at,))
    conn.commit()
    conn.close()

    return {"message": f"History record from '{created_at}' deleted successfully."}

@app.get("/admin/users")
def get_users(request:Request):
    if request.session.get("role") != "admin":
        return {"error": "Unauthorized"}
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username,role FROM users")
    rows = cursor.fetchall()
    conn.close()

    return {"users" : rows}
@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    if "username" not in request.session:
        return RedirectResponse("/", status_code=303)

    username = request.session.get("username")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT input_text, ocr_text, prediction, confidence, created_at 
        FROM history 
        WHERE username = ?
        ORDER BY created_at DESC
    """, (username,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "input_text": row[0],
            "ocr_text": row[1],
            "prediction": row[2],
            "confidence": row[3],
            "created_at": row[4]
        })

    # ✅ PASS history to template
    return templates.TemplateResponse("history.html", {
        "request": request,
        "history": history
    })

@app.get("/generate-report")
def generate_report(request: Request, created_at: str):
    username = request.session.get("username")
    if not username:
        return {"error": "Not logged in"}

    # Fetch the record from DB
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT input_text, ocr_text, prediction, confidence, created_at
        FROM history
        WHERE username = ? AND created_at = ?
    """, (username, created_at))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": "Record not found"}

    # Make sure folder exists
    os.makedirs("static/reports", exist_ok=True)

    # Sanitize filename
    safe_created_at = created_at.replace(":", "-").replace(" ", "_")
    file_path = f"static/reports/report_{safe_created_at}.pdf"

    # Setup PDF
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    # Sinhala font style
    sinhala_style = ParagraphStyle(
        'SinhalaStyle',
        fontName='NotoSansSinhala',
        fontSize=12,
        leading=14
    )

    content = []

    # Title
    content.append(Paragraph("FairLanka Detection Report", styles['Title']))
    content.append(Spacer(1,10))

    # Metadata
    content.append(Paragraph(f"Date: {row[4]}", styles['Normal']))
    content.append(Paragraph(f"Prediction: {row[2]}", styles['Normal']))
    content.append(Paragraph(f"Confidence: {row[3]*100:.2f}%", styles['Normal']))
    content.append(Spacer(1, 10))

    # Input Text
    content.append(Paragraph("Input Text:", styles['Heading3']))
    input_text = row[0] or "-"
    for line in input_text.splitlines():
        content.append(Paragraph(line, sinhala_style))
    content.append(Spacer(1,10))

    # OCR Text
    content.append(Paragraph("OCR Text:", styles['Heading3']))
    ocr_text = row[1] or "-"
    for line in ocr_text.splitlines():
        content.append(Paragraph(line, sinhala_style))
    content.append(Spacer(1,10))

    # Build PDF
    doc.build(content)

    # Return PDF
    return FileResponse(
        file_path,
        filename=f"report_{safe_created_at}.pdf",
        media_type="application/pdf"
    )
@app.get("/view-report", response_class=HTMLResponse)
def view_report(request: Request, created_at: str):
    username = request.session.get("username")
    if not username:
        return RedirectResponse("/", status_code=303)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT input_text, ocr_text, prediction, confidence, created_at
        FROM history
        WHERE username = ? AND created_at = ?
    """, (username, created_at))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return HTMLResponse("Report not found")

    return templates.TemplateResponse("report.html", {
        "request": request,
        "data": {
            "input_text": row[0],
            "ocr_text": row[1],
            "prediction": row[2],
            "confidence": row[3],
            "created_at": row[4]
        }
    })

@app.post("/predict_text")
async def predict_text_only(text: str = Form(...)):
    normalized_text = selective_singlish_normalize(clean_text(text), normalizer)
    t_probs = predict_text(normalized_text)
    label = "Real" if t_probs["real"] > t_probs["fake"] else "Fake"
    return {"input_text": text, "normalized_text": normalized_text, "text_probs": t_probs, "label": label}

@app.post("/predict")
async def predict_meme(file: UploadFile = File(...)):
    path = f"temp_{uuid.uuid4().hex}.jpg"
    with open(path,"wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
    try:
        raw_text = extract_text(path)
        normalized_text = selective_singlish_normalize(clean_text(raw_text), normalizer)
        t_probs = predict_text(normalized_text)
        image_probs = predict_image(path)
        decision = final_decision(t_probs, image_probs)
        return {
            "ocr_text": raw_text,
            "normalized_text": normalized_text,
            "text_probs": t_probs,
            "image_probs": image_probs,
            "final_decision": decision
        }
    finally:
        if os.path.exists(path):
            os.remove(path)

@app.post("/detect")
async def detect(
    request: Request,
    text_input: Optional[str] = Form(None),
    meme: Optional[UploadFile] = File(None)
):

    result = {}

    t_probs = None
    image_probs = None
    raw_text = None

    # -------------------------
    # TEXT PROCESSING
    # -------------------------
    if text_input and text_input.strip() != "":
        normalized_text = selective_singlish_normalize(
            clean_text(text_input),
            normalizer
        )

        t_probs = predict_text(normalized_text)

        result["input_text"] = text_input
        result["normalized_text"] = normalized_text
        result["text_probs"] = t_probs
        result["text_confidence"] = max(t_probs["fake"], t_probs["real"])

    # -------------------------
    # IMAGE PROCESSING
    # -------------------------
    if meme and meme.filename != "":

        path = f"temp_{uuid.uuid4().hex}.jpg"

        with open(path, "wb") as buffer:
            shutil.copyfileobj(meme.file, buffer)

        try:
            raw_text = extract_text(path) or ""

            normalized_ocr = selective_singlish_normalize(
                clean_text(raw_text),
                normalizer
            )

            image_probs = predict_image(path)

            result["image_probs"] = image_probs
            result["ocr_text"] = raw_text
            result["normalized_ocr"] = normalized_ocr
            result["image_confidence"] = max(
                image_probs["fake"],
                image_probs["real"]
            )

        finally:
            if os.path.exists(path):
                os.remove(path)

    # -------------------------
    # FINAL DECISION
    # -------------------------
    if t_probs or image_probs:

        label = None
        confidence = None

        if t_probs and image_probs:
            decision = final_decision(t_probs, image_probs)
            label = decision["label"]
            confidence = decision["confidence"]
            result["final_decision"] = decision

        elif t_probs:
            label = "Real" if t_probs["real"] > t_probs["fake"] else "Fake"
            confidence = max(t_probs["real"], t_probs["fake"])

        elif image_probs:
            label = "Real" if image_probs["real"] > image_probs["fake"] else "Fake"
            confidence = max(image_probs["real"], image_probs["fake"])

        # ✅ FIX: Save for ALL cases
        save_prediction(
            username=request.session.get("username"),
            input_text=text_input,
            ocr_text=raw_text,
            prediction=label,
            confidence=confidence
        )

    # -------------------------
    # EMPTY INPUT CASE
    # -------------------------
    if not result:
        return {"error": "Please enter text or upload an image"}

    return result


@app.get("/my-history")
def get_user_history(request: Request):
    username = request.session.get("username")
    if not username:
        return {"error": "Not logged in"}
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT input_text, ocr_text, prediction, confidence, created_at 
        FROM history 
        WHERE username = ? 
        ORDER BY created_at DESC
    """, (username,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "input_text": row[0],
            "ocr_text": row[1],
            "prediction": row[2],
            "confidence": row[3],
            "created_at":row[4]
        })
    return {"history": history}