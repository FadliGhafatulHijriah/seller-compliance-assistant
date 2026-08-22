from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Seller Compliance Assistant API")

# Izinkan CORS agar Frontend (Next.js lokal & Vercel) bisa terhubung ke Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"https://seller-compliance-assistant.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
  text: str


@app.get("/")
def read_root():
  return {
      "status": "ok",
      "message": "API Seller Compliance Assistant BPOM Aktif!",
  }


@app.post("/analyze")
def analyze_text(payload: AnalyzeRequest):
  # Daftar aturan kata kunci BPOM & kategorinya
  rules = [
      ("pasti ampuh", "Klaim Mutlak / Overclaim"),
      ("100% manjur", "Klaim Mutlak / Overclaim"),
      ("ampuh", "Overclaim"),
      ("manjur", "Overclaim"),
      ("mengobati", "Klaim Medis Terlarang"),
      ("meredakan", "Klaim Medis Terlarang"),
      ("menyembuhkan", "Klaim Medis Terlarang"),
      ("infeksi", "Istilah Medis / Penyakit"),
      ("flu", "Istilah Medis / Penyakit"),
      ("sakit gigi", "Istilah Medis / Penyakit"),
      ("sakit kepala", "Istilah Medis / Penyakit"),
      ("nyeri otot", "Istilah Medis / Penyakit"),
      ("tanpa efek samping", "Klaim Keamanan Tanpa Bukti"),
      ("100%", "Klaim Mutlak"),
  ]

  issues = []
  text_lower = payload.text.lower()

  for word, category in rules:
    if word in text_lower:
      # Hindari duplikasi jika kata kunci berulang
      if not any(item["keyword"] == word for item in issues):
        issues.append(
            {"keyword": word, "category": category, "reason": category}
        )

  # Menentukan label status kepatuhan berdasarkan jumlah temuan
  issue_count = len(issues)
  if issue_count == 0:
    status_label = "Aman / Patuh"
  elif issue_count <= 2:
    status_label = "Sedang"
  else:
    status_label = "Tidak Patuh"

  return {
      "status": "success",
      "status_label": status_label,
      "issues": issues,
      "total_issues": issue_count,
  }