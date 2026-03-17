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
from datetime import datetime
from langchain_core.tools import tool

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
# 2.1 PROJECTS DATA (Mock)
# ==========================================
PROJECTS = [
    {"name": "RealizeTogether AI", "tech": "Astro, FastAPI, Gemini", "desc": "Ein KI-Showcase-Portfolio."},
    {"name": "Lean RAG Bot", "tech": "Python, LangChain", "desc": "Effizienter Bot mit In-Context Learning."},
    {"name": "UX Analyzer", "tech": "Vision LLM, Tailwind", "desc": "Analysiert Screenshots auf Design-Qualität."},
]

# ==========================================
# 3. AI MODELS (Resilient Fallback System)
# ==========================================
api_key = os.getenv("GOOGLE_API_KEY")

# Resilience: Multi-Model Fallback List
LLM_MODELS = [
    "gemini-flash-latest",
    "gemini-2.0-flash", 
    "gemini-pro-latest",
    "gemini-flash-lite-latest"
]

async def invoke_resiliently(prompt_or_messages, input_data=None, is_vision=False, structured_class=None):
    """Tries multiple models in sequence if one fails due to Quota or Timeout."""
    last_error: Exception = Exception("Unknown error")
    for model_name in LLM_MODELS:
        try:
            # Create a temporary LLM with the current model name
            temp_llm = ChatGoogleGenerativeAI(
                model=model_name, 
                google_api_key=api_key, 
                max_retries=0,
                request_timeout=30.0 if not is_vision else 45.0
            )
            
            # Handle structured output if requested
            target_llm = temp_llm
            if structured_class:
                target_llm = temp_llm.with_structured_output(structured_class)
            
            # Case 1: Prompt Template + Input Data
            if input_data is not None and hasattr(prompt_or_messages, "invoke"):
                current_prompt_template: ChatPromptTemplate = prompt_or_messages # type: ignore
                chain = current_prompt_template | target_llm
                return await chain.ainvoke(input_data)
            
            # Case 2: List of Messages or raw prompt
            return await target_llm.ainvoke(prompt_or_messages)
            
        except Exception as e:
            print(f"⚠️ Model {model_name} failed: {str(e)[:100]}...")
            last_error = e
            continue
    raise last_error

# ==========================================
# 3.1 AGENT TOOLS
# ==========================================
@tool
def get_current_time():
    """Returns the current server time. Useful for greetings or context-aware replies."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculator(expression: str):
    """Solves mathematical expressions. Input should be a simple math string like '123 * 45'."""
    try:
        # Simple and relatively safe for a showcase
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Fehler bei der Berechnung: {str(e)}"

@tool
def search_projects(query: str):
    """Searches through Sinan's projects. Input should be a keyword like 'KI' or 'Frontend'."""
    query = query.lower()
    results = [p for p in PROJECTS if query in p['name'].lower() or query in p['tech'].lower() or query in p['desc'].lower()]
    if not results:
        return "Keine passenden Projekte gefunden."
    return str(results)

tools = [get_current_time, calculator, search_projects]

# Agent Setup (Manual Tool Calling for better stability)
# Gemini Flash support tool calling via bind_tools
llm_with_tools = chat_llm.bind_tools(tools)

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

class VisionAnalysis(BaseModel):
    impression: Literal['positive', 'negative', 'neutral'] = Field(description="First impression of the design")
    usability_score: int = Field(description="Score from 1 to 10 for usability")
    design_feedback: str = Field(description="Feedback on colors, whitespace, typography")
    improvements: list[str] = Field(description="Exactly 3 concrete actionable improvements")
    tailwind_code: Optional[str] = Field(description="A short Tailwind CSS snippet if applicable, else empty string")

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

    chain = ChatPromptTemplate.from_template(template)
    try:
        start_time = datetime.now()
        res = await invoke_resiliently(chain, {"cv_text": CV_CONTEXT, "user_message": request.message})
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✅ AI Response in {duration:.2f}s")
        return {"reply": res.content}
    except Exception as e:
        if "429" in str(e):
            return {"reply": "Quota Error: Alle KI-Modelle haben ihr Tageslimit erreicht. Bitte versuche es später wieder! (API Quota Exhausted)"}
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
            You are a Senior UX/UI Designer. Analyze this screenshot and return structured JSON.
            1. 'impression': Your first impression (positive, negative, neutral).
            2. 'usability_score': Score from 1 to 10.
            3. 'design_feedback': General feedback on design elements.
            4. 'improvements': 3 concrete points to improve.
            5. 'tailwind_code': A short Tailwind CSS snippet if applicable.
            """
        else:
            prompt_text = """
            Du bist ein Senior UX/UI Designer. Analysiere diesen Screenshot und antworte strikt in JSON.
            1. 'impression': Dein erster Eindruck (positive, negative, neutral) - der Wert MUSS auf Englisch sein!
            2. 'usability_score': Punktzahl von 1 bis 10.
            3. 'design_feedback': Feedback zu Design-Elementen (auf Deutsch).
            4. 'improvements': 3 konkrete Verbesserungsvorschläge (auf Deutsch).
            5. 'tailwind_code': Ein kurzes Tailwind CSS Snippet (falls anwendbar).
            """

        message = HumanMessage(content=[
            {"type": "text", "text": prompt_text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ])
        
        response = await invoke_resiliently([message], is_vision=True, structured_class=VisionAnalysis)
        return response

    except Exception as e:
        print(f"❌ Vision Error: {e}")
        return {"error": str(e)}

# --- SENTIMENT ---
@app.post("/api/analyze")
async def analyze_sentiment(request: AnalyzeRequest):
    print(f"📊 Sentiment ({request.language}): {request.text[:30]}...")
    
    # SYSTEM PROMPT UMSCHALTEN
    if request.language == "en":
        sys_prompt = "You are a sentiment analysis expert. Analyze the text. The 'suggestion' field MUST be in English. For 'emotion', strictly select the best fitting key from the allowed list (even if they are German words)."
    else:
        sys_prompt = "Du bist ein Experte für Sentiment-Analyse. Analysiere den Text und gib JSON zurück. Das Feld 'suggestion' soll auf Deutsch sein."

    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_prompt),
        ("human", "Text: {text}")
    ])
    
    try:
        result = await invoke_resiliently(prompt, {"text": request.text}, structured_class=SentimentAnalysis)
        return result
    except Exception as e:
        print(f"❌ Analyze Error: {e}")
        return {"error": str(e)}

# --- AGENT ---
@app.post("/api/agent")
async def agent_endpoint(request: ChatRequest):
    print(f"🤖 Agent Request (Async Loop): {request.message}")
    try:
        start_time = datetime.now()
        
        system_content = f"Du bist Sinans smarter Portfolio-Assistent. Nutze Tools wenn nötig. Antworte in der Sprache: {request.language}. CV Kontext: {str(CV_CONTEXT)[:500]}"
        messages: list = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": request.message}
        ]
        
        # Helper for Agent Tool Binding (since we have to bind tools to each model in the fallback)
        async def agent_invoke(msgs: list):
            last_err: Exception = Exception("Agent fallback failed")
            for model_name in LLM_MODELS:
                try:
                    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, request_timeout=45.0)
                    llm_with_tools = llm.bind_tools(tools)
                    return await llm_with_tools.ainvoke(msgs)
                except Exception as ex:
                    print(f"⚠️ Agent Model {model_name} failed: {str(ex)[:50]}...")
                    last_err = ex
            raise last_err

        # 1. LLM Reasoning
        print("🔄 Step 1: LLM reasoning...")
        ai_msg = await agent_invoke(messages)
        messages.append(ai_msg)

        # Sicherer Zugriff auf Tool-Calls (LangChain Returns können variieren)
        tool_calls = getattr(ai_msg, 'tool_calls', [])
        if not tool_calls and isinstance(ai_msg, dict):
            tool_calls = ai_msg.get('tool_calls', [])

        # 2. Tool EXECUTION
        if tool_calls:
            print(f"🛠️ Executing {len(tool_calls)} Tool Calls...")
            for tool_call in tool_calls:
                selected_tool = next((t for t in tools if t.name == tool_call["name"]), None)
                if selected_tool:
                    print(f"  -> Action: {tool_call['name']}")
                    tool_output = await selected_tool.ainvoke(tool_call["args"])
                    messages.append({
                        "role": "tool",
                        "content": str(tool_output),
                        "tool_call_id": tool_call["id"]
                    })
            
            # 3. Finaler Call
            print("🔄 Step 2: Final response with tool data...")
            # We need the fallback here too
            final_res = await agent_invoke(messages)
            reply = getattr(final_res, 'content', str(final_res))
            return {"reply": reply}
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✅ Agent Response in {duration:.2f}s")
        reply = getattr(ai_msg, 'content', str(ai_msg))
        return {"reply": reply}
        
    except Exception as e:
        print(f"❌ Agent Error: {e}")
        return {"reply": f"Sorry, mein System hängt gerade: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)