from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
# WICHTIG: Wir nutzen jetzt NUR NOCH das Standard-Pydantic (v2)
from pydantic import BaseModel, Field 
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import base64

# ==========================================
# 1. SETUP & KONFIGURATION
# ==========================================
load_dotenv()
app = FastAPI()

# DEBUG: Zeigt uns im Render-Log, wer anfragt
@app.middleware("http")
async def log_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin:
        print(f"🔔 Eingehender Request von Origin: {origin}")
    response = await call_next(request)
    return response

# CORS - Konfiguration
origins = [
    "http://localhost:4321",
    "http://localhost:3000",
    "https://sinan.realizetogether.com",
    "https://www.sinan.realizetogether.com",
    "https://realizetogether.com",
    "https://www.realizetogether.com",
    "https://realizetogether-ai.onrender.com", 
]

# NEU: Regex, der deine Cloud-Umgebung (und Localhost Ports) erlaubt
origin_regex = r"https://.*\.cloudworkstations\.dev|http://localhost:\d+"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Deine feste Liste
    allow_origin_regex=origin_regex, # <--- WICHTIG: Erlaubt die dynamische Cloud-URL
    allow_credentials=True,    
    allow_methods=["*"],       
    allow_headers=["*"],       
)

# ==========================================
# 2. DATEN & LOGIK (Lebenslauf)
# ==========================================
CV_CONTEXT = ""

def load_cv():
    """Liest die Markdown-Datei aus dem data-Ordner ein."""
    global CV_CONTEXT
    file_path = os.path.join("data", "cv.md")

    try:
        if not os.path.exists(file_path):
            print(f"⚠️ WARNUNG: Datei unter '{file_path}' nicht gefunden!")
            CV_CONTEXT = "Kein Lebenslauf hinterlegt."
            return

        print(f"📂 Lade Lebenslauf von: {file_path} ...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            CV_CONTEXT = f.read()
            
        print(f"✅ Lebenslauf geladen! ({len(CV_CONTEXT)} Zeichen)")
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Datei: {e}")
        CV_CONTEXT = "Fehler beim Laden des Lebenslaufs."

# Beim Starten einmal ausführen
load_cv()

# ==========================================
# 3. AI SETUP (Modelle)
# ==========================================
api_key = os.getenv("GOOGLE_API_KEY")

# Modell für den Chat
chat_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest", 
    google_api_key=api_key,
    max_retries=0,       
    request_timeout=10.0
)

# Modell für Vision
vision_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", 
    google_api_key=api_key,
    max_retries=0,
    request_timeout=20.0 
)

# ==========================================
# 4. DATENMODELLE (Pydantic v2)
# ==========================================

# Modell für Chat-Requests
class ChatRequest(BaseModel):
    message: str
    language: str = "de"

# Modell für Sentiment-Analyse Input
class AnalyzeRequest(BaseModel):
    text: str

# Modell für Sentiment-Analyse OUTPUT
# Jetzt erben wir einfach von BaseModel (Standard)
class SentimentAnalysis(BaseModel):
    score: float = Field(
        description="Ein Wert zwischen -1.0 (sehr negativ) und 1.0 (sehr positiv)."
    )
    emotion: Literal['freude', 'wut', 'trauer', 'neutral', 'angst'] = Field(
        description="Die primäre Emotion, die im Text erkannt wurde."
    )
    suggestion: str = Field(
        description="Ein kurzer, höflicher Tipp an den Verfasser, wie er den Text professioneller formulieren könnte (max. 1 Satz)."
    )

# ==========================================
# 5. ENDPUNKTE (API Routes)
# ==========================================

# --- CHAT ---
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"📩 Frage: {request.message} | Sprache: {request.language}")
    
    if request.language == "en":
        prompt_template = ChatPromptTemplate.from_template("""
        You are the professional AI assistant for Sinan. 
        Use the following resume to answer questions:

        RESUME DATA:
        {cv_text}

        RULES:
        - Answer in ENGLISH.
        - Keep it short, professional, and helpful.
        - If the info is not in the resume, say honestly that you don't know.
        - Speak as an assistant ("Sinan has...", "He has...").

        USER QUESTION: 
        {user_message}
        """)
    else:
        prompt_template = ChatPromptTemplate.from_template("""
        Du bist der professionelle AI-Assistent von Sinan. 
        Nutze den folgenden Lebenslauf, um Fragen zu beantworten:

        LEBENSLAUF DATEN:
        {cv_text}

        REGELN:
        - Antworte kurz, professionell und hilfreich.
        - Wenn die Info nicht im Lebenslauf steht, sag ehrlich, dass du es nicht weißt.
        - Du sprichst als Assistent ("Sinan hat...", "Er hat...").

        FRAGE DES USERS: 
        {user_message}
        """)

    chain = prompt_template | chat_llm
    
    try:
        response = chain.invoke({
            "cv_text": CV_CONTEXT,
            "user_message": request.message
        })
        return {"reply": response.content}
        
    except Exception as e:
        error_str = str(e).lower()
        print(f"❌ Fehler: {error_str}") 
        
        if "429" in error_str or "resource_exhausted" in error_str or "timeout" in error_str:
            return {"reply": "⚠️ **Kurze Pause!** Ich habe gerade zu viele Anfragen erhalten. Bitte warte 30 Sekunden. ⏳"}
        
        return {"reply": f"Ein technisches Problem ist aufgetreten: {str(e)}"}

# --- VISION ---
@app.post("/api/vision")
async def vision_endpoint(file: UploadFile = File(...)):
    print(f"🖼️ Bild empfangen: {file.filename}")
    
    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode("utf-8")
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": """
Du bist ein Senior UX/UI Designer und Frontend-Experte. Analysiere diesen Screenshot. 

Erstelle eine Analyse im Markdown-Format:
1. **Erster Eindruck:** Was fällt sofort auf? (Positiv/Negativ)
2. **UX & Usability:** Sind Buttons erkennbar? Ist die Navigation logisch?
3. **Design & Ästhetik:** Farbwahl, Whitespace, Typografie.
4. **Verbesserungsvorschläge:** 3 konkrete Punkte für bessere Conversion oder User Experience.
5. **Bonus Code:** Gib mir einen kurzen Tailwind-CSS Code-Schnipsel, um das wichtigste Element (z.B. CTA Button) zu verbessern.
                """},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]
        )
        
        response = vision_llm.invoke([message])
        
        # --- FIX: LISTE ZU STRING KONVERTIEREN ---
        # Manchmal gibt Gemini eine Liste von Textblöcken zurück.
        # Wir kleben sie hier sicherheitshalber zusammen.
        analysis_text = response.content
        if isinstance(analysis_text, list):
            print("⚠️ Antwort war eine Liste, wird zusammengefügt...")
            analysis_text = "".join([str(item) for item in analysis_text])
            
        return {"analysis": analysis_text}

    except Exception as e:
        print(f"❌ Vision Fehler: {e}")
        error_str = str(e).lower()
        if "429" in error_str or "resource_exhausted" in error_str:
             return {"analysis": "⚠️ **Rate Limit erreicht.** Google's Vision AI braucht eine kurze Pause."}
        return {"analysis": f"Fehler bei der Bildanalyse: {str(e)}"}

# Optional: Root-Endpunkt für Health-Checks
@app.get("/")
async def root():
    return {"status": "Server läuft! 🚀", "endpoints": ["/api/chat", "/api/vision", "/api/analyze"]}
    
# ==========================================
# 6. STARTUP
# ==========================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)