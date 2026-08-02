from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Seller Compliance Assistant API")

# Izinkan CORS agar Frontend (Next.js) bisa terhubung ke Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API Seller Compliance Assistant BPOM Aktif!"}

@app.post("/analyze")
def analyze_text(payload: AnalyzeRequest):
    forbidden_words = ["mengobati", "pasti ampuh", "100% manjur", "tanpa efek samping"]
    
    issues = []
    text_lower = payload.text.lower()
    
    for word in forbidden_words:
        if word in text_lower:
            issues.append({
                "keyword": word,
                "category": "Overclaim / Klaim Berisiko"
            })
            
    # Kembalikan kunci dengan nama "issues" (bukan "found_issues")
    return {
        "status": "success",
        "issues": issues
    }