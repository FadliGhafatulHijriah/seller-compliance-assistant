import os
import joblib
import torch
import ahocorasick
import pandas as pd
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification

app = FastAPI(title="Seller Compliance Assistant API")

# Konfigurasi CORS (Localhost & Domain Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"https://seller-compliance-assistant.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Path Model & Dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
DATA_DIR = os.path.join(BASE_DIR, "dataset")

# Inisialisasi device CPU/CUDA
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

logreg_model = joblib.load(os.path.join(MODEL_DIR, "logreg_baseline.joblib"))
tfidf = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib"))

bert_path = os.path.join(MODEL_DIR, "indobert_bpom_model")
tokenizer = AutoTokenizer.from_pretrained(bert_path)
model_bert = AutoModelForSequenceClassification.from_pretrained(bert_path)
model_bert.to(device)
model_bert.eval()

# 4. Inisialisasi Basis Pengetahuan Edukasi & Rekomendasi Resmi BPOM No. 3/2022
EDUKASI_REKOMENDASI_BPOM = {
    "mengobati": "Klaim penyembuhan adalah ranah obat. Gunakan: 'Membantu merawat / menenangkan kondisi kulit'.",
    "menyembuhkan": "Klaim kosmetika tidak boleh menjanjikan kesembuhan. Gunakan: 'Membantu merawat kelembapan kulit'.",
    "meredakan": "Gunakan klaim kosmetika yang diizinkan: 'Memberikan rasa sejuk dan nyaman pada kulit'.",
    "memutihkan": "Klaim pemutih berlebihan dilarang. Gunakan: 'Mencerahkan kulit' atau 'Meratakan warna kulit'.",
    "anti iritasi": "Ganti dengan fungsi perlindungan: 'Membantu menyejukkan kulit kemerahan'.",
    "luka bakar": "Pengobatan luka bakar termasuk klaim medis. Kosmetika hanya berfungsi memelihara kebersihan kulit luar.",
    "gigitan nyamuk": "Ganti dengan: 'Mengurangi rasa tidak nyaman akibat biang keringat / faktor luar'.",
    "anti jamur": "Klaim anti-fungal/antijamur adalah klaim medis terapeutik, dilarang untuk sediaan kosmetika.",
    "ampuh": "Hindari kata hiperbola/superlatif. Jelaskan khasiat bahan secara spesifik dan objektif.",
    "manjur": "Hindari garansi hasil instan/mutlak. Gunakan deskripsi fungsi manfaat produk.",
    "pasti ampuh": "Klaim garansi mutlak dilarang BPOM. Gunakan: 'Diformulasikan untuk membantu merawat kulit'.",
    "100% manjur": "Klaim persentase kesembuhan tanpa uji klinis dilarang. Gunakan klaim manfaat wajar.",
    "tanpa efek samping": "Klaim keamanan absolut dilarang BPOM karena reaksi kulit bersifat individual.",
    "infeksi": "Istilah infeksi/penyakit dilarang pada kosmetik. Gunakan: 'Menjaga kebersihan dan higienitas kulit'.",
}

# 5. Inisialisasi Automaton Aho-Corasick (Bahan Dilarang & Frasa BPOM)
rules_automaton = ahocorasick.Automaton()

# A. Muat 1.707 Bahan Dilarang dari CSV BPOM
csv_bahan_path = os.path.join(DATA_DIR, "daftar_bahan_dilarang_bpom_terstandarisasi_lengkap.csv")
if os.path.exists(csv_bahan_path):
    df_bahan = pd.read_csv(csv_bahan_path)
    for idx, row in df_bahan.iterrows():
        nama_bahan = str(row["nama_bahan_utama"]).strip().lower()
        if len(nama_bahan) >= 3 and str(row.get("status_regulasi", "Dilarang")) == "Dilarang":
            rules_automaton.add_word(
                nama_bahan, 
                ("Bahan Berbahaya", str(row["nama_bahan_utama"]), "Bahan ini dilarang mutlak dalam kosmetika menurut BPOM. Hapus bahan ini.")
            )

# B. Masukkan Aturan Edukasi Klaim Medis & Overclaim
for word, saran in EDUKASI_REKOMENDASI_BPOM.items():
    rules_automaton.add_word(word.lower(), ("Klaim Berisiko / Overclaim", word, saran))

rules_automaton.make_automaton()


class AnalyzeRequest(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "API Seller Compliance Assistant BPOM (IndoBERT + Ensemble Engine) Aktif!",
    }


@app.post("/analyze")
def analyze_text(payload: AnalyzeRequest):
    input_text = payload.text.strip()
    if not input_text:
        return {
            "status": "success",
            "status_label": "Aman / Patuh",
            "risk_score": 0.0,
            "issues": [],
            "total_issues": 0,
            "summary_recommendation": "Teks deskripsi kosong. Masukkan teks untuk evaluasi kepatuhan."
        }

    # 1. Pemindaian Cepat Deterministik (Aho-Corasick)
    issues: List[Dict[str, Any]] = []
    found_keywords = set()
    for end_idx, (category, matched_word, recommendation) in rules_automaton.iter(input_text.lower()):
        if matched_word.lower() not in found_keywords:
            found_keywords.add(matched_word.lower())
            issues.append({
                "keyword": matched_word,
                "category": category,
                "reason": category,
                "recommendation": recommendation
            })

    # 2. Prediksi Baseline (TF-IDF + Logistic Regression)
    vec = tfidf.transform([input_text])
    prob_log = float(logreg_model.predict_proba(vec)[0, 1])

    # 3. Prediksi Kontekstual IndoBERT
    enc = tokenizer(
        input_text,
        truncation=True,
        max_length=64,
        padding="max_length",
        return_tensors="pt"
    )
    with torch.no_grad():
        out = model_bert(
            input_ids=enc["input_ids"].to(device),
            attention_mask=enc["attention_mask"].to(device)
        )
        prob_bert = float(torch.softmax(out.logits, dim=1)[:, 1].item())

    # 4. Soft Voting Ensemble (60% IndoBERT + 40% LogReg)
    ensemble_score = (0.60 * prob_bert) + (0.40 * prob_log)

    # 5. Rule-Based Override jika ditemukan pelanggaran aturan pasti
    if issues:
        ensemble_score = max(ensemble_score, 0.95)

    issue_count = len(issues)

    # 6. Status Label untuk Komponen Frontend Next.js
    if ensemble_score >= 0.70 or issue_count >= 3:
        status_label = "Tidak Patuh"
        summary_rec = "Ditemukan pelanggaran serius terhadap regulasi BPOM. Segera ganti kata-kata yang ditandai merah sesuai saran edukasi."
    elif ensemble_score >= 0.35 or issue_count > 0:
        status_label = "Sedang"
        summary_rec = "Deskripsi mengandung klaim berisiko. Tinjau kembali rekomendasi frasa sebelum menerbitkan produk."
    else:
        status_label = "Aman / Patuh"
        summary_rec = "Deskripsi produk memenuhi kaidah kepatuhan kosmetika regulasi BPOM No. 3 Tahun 2022."

    return {
        "status": "success",
        "status_label": status_label,
        "risk_score": round(ensemble_score * 100, 2),
        "metrics_breakdown": {
            "indobert_confidence": round(prob_bert * 100, 2),
            "baseline_confidence": round(prob_log * 100, 2),
        },
        "issues": issues,
        "total_issues": issue_count,
        "summary_recommendation": summary_rec
    }