from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Seller Compliance Assistant API")

# Izinkan CORS agar Frontend (Next.js) bisa terhubung ke Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    text: str

@app.get("/api")
def read_root():
    return {"status": "ok", "message": "API Seller Compliance Assistant BPOM Aktif!"}

@app.post("/api/analyze")
def analyze_text(payload: AnalyzeRequest):
    # Rule-based BPOM sederhana untuk MVP awal
    forbidden_words = ["mengobati", "pasti ampuh", "100% manjur", "tanpa efek samping", "menyembuhkan"]
    
    found_issues = []
    text_lower = payload.text.lower()
    
    for word in forbidden_words:
        if word in text_lower:
            found_issues.append({
                "keyword": word,
                "type": "OVERCLAIM",
                "reason": f"Penggunaan kata '{word}' melanggar aturan klaim khasiat berlebihan menurut indikasi BPOM."
            })
            
    risk_level = "HIGH" if len(found_issues) > 0 else "SAFE"
    
    return {
        "status": "success",
        "risk_level": risk_level,
        "total_issues": len(found_issues),
        "issues": found_issues
    }