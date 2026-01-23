from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field 
from typing import Literal, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import base64

# ==========================================
# 1. SETUP
# ==========================================
load_dotenv()
app = FastAPI()

# DEBUG: Origin Logging
@app.middleware("http")
async def log_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin:
        print(f"🔔 Request from Origin: {origin}")
    response = await call_next(request)
    return response

# CORS
origins = [
    "http://localhost:4321",
    "http://localhost:3000",
    "https://sinan.realizetogether.com",
    "https://www.sinan.realizetogether.com",
    "https://realizetogether.com",
    "https://www.realizetogether.com",
    "https://realizetogether-ai.onrender.com", 
]
origin_regex = r"https://.*\.cloudworkstations\.dev|http://localhost:\d+"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=origin_regex,
    allow_credentials=True,    
    allow_methods=["*"],       
    allow_headers=["*"],       
)

# ==========================================
# 2. DATA (CV)
# ==========================================
CV_CONTEXT = ""
def load_cv():
    global CV_CONTEXT
    file_path = os.path.join("data", "cv.md")
    try:
        if not os.path.exists(file_path):
            CV_CONTEXT = "Kein Lebenslauf gefunden."
            return
        with open(file_path, "r", encoding="utf-8") as f:
            CV_CONTEXT = f.read()
        print(f"✅ CV loaded! ({len(CV_CONTEXT)} chars)")
    except Exception as e:
        print(f"❌ Error loading CV: {e}")
        CV_CONTEXT = "Error loading CV."
load_cv()

# ==========================================
# 3. AI MODELS
# ==========================================
api_key = os.getenv("GOOGLE_API_KEY")
chat_llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", google_api_key=api_key, max_retries=0, request_timeout=10.0)
vision_llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key, max_retries=0, request_timeout=20.0)

# ==========================================
# 4. DATA MODELS
# ==========================================
class ChatRequest(BaseModel):
    message: str
    language: str = "de"

class AnalyzeRequest(BaseModel):
    text: str
    language: str = "de"  # NEU: Sprache optional, default deutsch

class SentimentAnalysis(BaseModel):
    score: float = Field(description="Score -1.0 to 1.0")
    # Wir behalten die internen IDs (freude, wut...), mappen aber die Ausgabe im Frontend
    emotion: Literal['freude', 'wut', 'trauer', 'neutral', 'angst'] = Field(description="Primary emotion key")
    suggestion: str = Field(description="Short suggestion for improvement")

# ==========================================
# 5. ENDPOINTS
# ==========================================

# --- CHAT ---
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"📩 Chat: {request.message} | Lang: {request.language}")
    
    if request.language == "en":
        template = """You are Sinan's AI assistant. Use this resume: {cv_text}. 
        Answer in ENGLISH. Short, professional. 
        User Question: {user_message}"""
    else:
        template = """Du bist Sinans AI Assistent. Nutze diesen CV: {cv_text}. 
        Antworte auf DEUTSCH. Kurz, professionell. 
        Frage: {user_message}"""

    chain = ChatPromptTemplate.from_template(template) | chat_llm
    try:
        res = chain.invoke({"cv_text": CV_CONTEXT, "user_message": request.message})
        return {"reply": res.content}
    except Exception as e:
        return {"reply": "Error/Fehler: " + str(e)}

# --- VISION ---
@app.post("/api/vision")
async def vision_endpoint(file: UploadFile = File(...), language: str = Form("de")):
    print(f"🖼️ Vision: {file.filename} | Lang: {language}")
    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode("utf-8")
        
        # PROMPT UMSCHALTEN
        if language == "en":
            prompt_text = """
            You are a Senior UX/UI Designer. Analyze this screenshot.
            Output in Markdown:
            1. **First Impression:** (Positive/Negative)
            2. **UX & Usability:** Buttons, Navigation?
            3. **Design:** Colors, Whitespace, Typography.
            4. **Improvements:** 3 concrete points.
            5. **Bonus Code:** A short Tailwind CSS snippet.
            """
        else:
            prompt_text = """
            Du bist ein Senior UX/UI Designer. Analysiere diesen Screenshot.
            Antworte in Markdown:
            1. **Erster Eindruck:** (Positiv/Negativ)
            2. **UX & Usability:** Buttons erkennbar?
            3. **Design:** Farben, Whitespace, Typo.
            4. **Verbesserungsvorschläge:** 3 konkrete Punkte.
            5. **Bonus Code:** Ein kurzer Tailwind CSS Schnipsel.
            """

        message = HumanMessage(content=[
            {"type": "text", "text": prompt_text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ])
        
        response = vision_llm.invoke([message])
        
        # Cleanup List responses
        analysis_text = response.content
        if isinstance(analysis_text, list):
            analysis_text = "".join([str(item) for item in analysis_text])
            
        return {"analysis": analysis_text}

    except Exception as e:
        print(f"❌ Vision Error: {e}")
        return {"analysis": f"Error: {str(e)}"}

# --- SENTIMENT ---
@app.post("/api/analyze")
async def analyze_sentiment(request: AnalyzeRequest):
    print(f"📊 Sentiment ({request.language}): {request.text[:30]}...")
    
    structured_llm = chat_llm.with_structured_output(SentimentAnalysis)
    
    # SYSTEM PROMPT UMSCHALTEN
    if request.language == "en":
        sys_prompt = "You are a sentiment analysis expert. Analyze the text. The 'suggestion' field MUST be in English. For 'emotion', strictly select the best fitting key from the allowed list (even if they are German words)."
    else:
        sys_prompt = "Du bist ein Experte für Sentiment-Analyse. Analysiere den Text und gib JSON zurück. Das Feld 'suggestion' soll auf Deutsch sein."

    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_prompt),
        ("human", "Text: {text}")
    ])
    
    chain = prompt | structured_llm

    try:
        result = chain.invoke({"text": request.text})
        return result
    except Exception as e:
        print(f"❌ Analyze Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)