import os
import re
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

# Konfigurasi CORS
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

# 2. Modul Two-Way Text Normalization (Regex & Anti-Obfuscation)
LEET_MAP = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "8": "b", "@": "a"})

def two_way_normalize(text: str) -> str:
    cleaned = re.sub(r"[-_.\s]+", " ", text)
    normalized = cleaned.lower().translate(LEET_MAP)
    return normalized

# 3. Modul Test-Time Augmentation (TTA) Generator
def predict_indobert_with_tta(text: str) -> float:
    variants = [text, two_way_normalize(text)]
    scores = []
    
    for v in variants:
        enc = tokenizer(
            v,
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
            prob = float(torch.softmax(out.logits, dim=1)[:, 1].item())
            scores.append(prob)
            
    return sum(scores) / len(scores)

# 4. Basis Pengetahuan Bahan Berbahaya Tambahan (Nama Umum Indonesia)
BAHAN_BERBAHAYA_TAMBAHAN = {
    "merkuri": "Merkuri (Hg) dilarang mutlak dalam kosmetika karena berbahaya bagi ginjal dan saraf (Peraturan BPOM No. 23/2019).",
    "mercury": "Merkuri dilarang mutlak dalam kosmetika menurut regulasi BPOM.",
    "hidrokuinon": "Hidrokuinon dilarang dalam kosmetika bebas (OTC) tanpa resep dokter.",
    "hydroquinone": "Hydroquinone dilarang dalam kosmetik tanpa resep dokter.",
    "asam retinoat": "Asam retinoat dilarang dalam kosmetika karena risiko iritasi berat dan efek teratogenik.",
    "retinoic acid": "Retinoic acid termasuk sediaan obat keras, dilarang untuk kosmetika bebas.",
    "steroid": "Kandungan steroid dilarang dalam sediaan kosmetik perawatan kulit.",
    "klobetasol": "Klobetasol propionat adalah kortikosteroid kuat yang dilarang keras dalam kosmetika."
}

# 5. Inisialisasi Basis Pengetahuan Edukasi & Rekomendasi Resmi BPOM No. 3/2022
EDUKASI_REKOMENDASI_BPOM = {
    # Klaim Waktu & Instan
    "instan": "Hindari klaim instan untuk hasil perawatan permanen. Gunakan: 'Memberikan efek tampilan cerah seketika (tone-up)'.",
    "secara instan": "Klaim efek instan dilarang BPOM jika menjanjikan perubahan struktur kulit tanpa uji klinis.",
    "dalam seminggu": "Janji durasi hasil instan dilarang tanpa uji klinis terakreditasi. Gunakan: 'Dengan penggunaan teratur'.",
    "dalam 7 hari": "Klaim durasi waktu spesifik dilarang BPOM. Gunakan: 'Membantu merawat kulit secara berkala'.",
    "dalam sekejap": "Klaim perubahan seketika dilarang regulasi kosmetika BPOM.",
    "hasil kilat": "Klaim superlatif waktu dilarang BPOM.",
    "permanen": "Kosmetika tidak dapat memberikan hasil permanen. Hapus klaim ini.",
    
    # Klaim Alami / Natural
    "alami": "Klaim 'alami' atau '100% alami' harus dapat dibuktikan secara formulasi dan tidak boleh menyesatkan konsumen (Peraturan BPOM No. 3/2022).",
    "secara alami": "Pastikan klaim bahan alami memiliki dokumen spesifikasi bahan baku resmi dan tidak melebih-lebihkan efikasi produk.",
    "100% alami": "Klaim 100% alami dilarang jika produk masih mengandung bahan sintetis atau pengawet.",
    "bebas bahan kimia": "Klaim 'bebas kimia' dilarang BPOM karena seluruh sediaan kosmetika tersusun atas zat kimiawi.",
    "tanpa bahan kimia": "Klaim 'tanpa bahan kimia' dilarang oleh regulasi BPOM.",

    # Klaim Medis & Terapeutik
    "mengobati": "Klaim penyembuhan adalah ranah obat. Gunakan: 'Membantu merawat / menenangkan kondisi kulit'.",
    "menyembuhkan": "Klaim kesembuhan dilarang pada kosmetik. Gunakan: 'Membantu merawat kelembapan kulit'.",
    "meredakan": "Gunakan klaim kosmetika yang diizinkan: 'Memberikan rasa sejuk dan nyaman pada kulit'.",
    "memutihkan": "Klaim pemutih berlebihan dilarang. Gunakan: 'Mencerahkan kulit' atau 'Meratakan warna kulit'.",
    "anti iritasi": "Ganti dengan fungsi perlindungan: 'Membantu menyejukkan kulit kemerahan'.",
    "luka bakar": "Pengobatan luka bakar termasuk ranah medis. Kosmetika hanya berfungsi memelihara kebersihan kulit luar.",
    "gigitan nyamuk": "Ganti dengan: 'Mengurangi rasa tidak nyaman akibat faktor luar'.",
    "anti jamur": "Klaim anti-fungal/antijamur adalah klaim medis terapeutik, dilarang untuk sediaan kosmetika.",
    "ampuh": "Hindari kata hiperbola/superlatif. Jelaskan khasiat bahan secara spesifik dan objektif.",
    "manjur": "Hindari garansi hasil mutlak. Gunakan deskripsi fungsi manfaat produk.",
    "pasti ampuh": "Klaim garansi mutlak dilarang BPOM. Gunakan: 'Diformulasikan untuk membantu merawat kulit'.",
    "100% manjur": "Klaim persentase kesembuhan dilarang BPOM.",
    "tanpa efek samping": "Klaim keamanan absolut dilarang BPOM karena reaksi kulit bersifat individual.",
    "infeksi": "Istilah infeksi/penyakit dilarang pada kosmetik. Gunakan: 'Menjaga kebersihan dan higienitas kulit'."
}

# 6. Inisialisasi Automaton Aho-Corasick
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

# B. Masukkan Bahan Berbahaya Populer Tambahan
for bahan, saran in BAHAN_BERBAHAYA_TAMBAHAN.items():
    rules_automaton.add_word(bahan.lower(), ("Bahan Berbahaya", bahan, saran))

# C. Masukkan Aturan Edukasi Klaim Medis & Overclaim
for word, saran in EDUKASI_REKOMENDASI_BPOM.items():
    rules_automaton.add_word(word.lower(), ("Klaim Berisiko / Overclaim", word, saran))

rules_automaton.make_automaton()


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

    # 1. Normalisasi Teks Dua Arah
    normalized_input = two_way_normalize(input_text)

    # 2. Pemindaian Cepat Deterministik (Aho-Corasick)
    issues: List[Dict[str, Any]] = []
    found_keywords = set()
    
    # Pindai teks input asli
    for end_idx, (category, matched_word, recommendation) in rules_automaton.iter(input_text.lower()):
        if matched_word.lower() not in found_keywords:
            found_keywords.add(matched_word.lower())
            issues.append({
                "keyword": matched_word,
                "category": category,
                "reason": category,
                "recommendation": recommendation
            })
            
    # Pindai teks hasil normalisasi (menangkap leetspeak seperti m3rkuri -> merkuri)
    for end_idx, (category, matched_word, recommendation) in rules_automaton.iter(normalized_input):
        if matched_word.lower() not in found_keywords:
            found_keywords.add(matched_word.lower())
            issues.append({
                "keyword": matched_word,
                "category": category,
                "reason": category,
                "recommendation": recommendation
            })

    # 3. Prediksi Baseline (TF-IDF + Logistic Regression)
    vec = tfidf.transform([normalized_input])
    prob_log = float(logreg_model.predict_proba(vec)[0, 1])

    # 4. Prediksi Kontekstual IndoBERT dengan TTA
    prob_bert = predict_indobert_with_tta(input_text)

    # 5. Soft Voting Ensemble (60% IndoBERT + 40% LogReg)
    ensemble_score = (0.60 * prob_bert) + (0.40 * prob_log)

    # 6. Rule-Based Override jika ditemukan pelanggaran pasti
    if issues:
        ensemble_score = max(ensemble_score, 0.85)

    issue_count = len(issues)

    # 7. Penentuan Label Status Kepatuhan
    if ensemble_score >= 0.65 or issue_count >= 2:
        status_label = "Tidak Patuh"
        summary_rec = "Ditemukan klaim terlarang atau janji hasil instan yang melanggar Peraturan BPOM No. 3 Tahun 2022."
    elif ensemble_score >= 0.20 or issue_count == 1:
        status_label = "Sedang"
        summary_rec = "Deskripsi mengandung indikasi klaim berisiko. Disarankan menyesuaikan frasa promosi."
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