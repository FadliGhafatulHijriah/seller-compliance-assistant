# 🛡️ Seller Compliance Assistant (BPOM)

Sistem asisten kepatuhan untuk deteksi klaim berlebihan (*overclaim*) dan bahan berbahaya pada deskripsi produk e-commerce. Menggabungkan kamus deterministik (Aho-Corasick), model leksikal (TF-IDF + Logistic Regression), dan model kontekstual (IndoBERT) dengan soft voting ensemble.

## Intisari
- Deteksi bahan berbahaya berbasis kamus: 1.707 istilah bahan terlarang BPOM.
- Klasifikasi klaim berlebihan menggunakan IndoBERT (fine-tuned) + baseline TF-IDF.
- Soft voting ensemble dengan rule-override untuk kasus bahan berbahaya.

## Fitur Utama
- Highlight kata/istilah berisiko pada deskripsi produk.
- Skor risiko gabungan (ensemble) dan rekomendasi perbaikan klaim sesuai regulasi BPOM.
- API backend (FastAPI) dan frontend Next.js untuk antarmuka interaktif.

## Arsitektur Singkat
1. Aho-Corasick automaton untuk pencocokan deterministic (span exact match).
2. TF-IDF + Logistic Regression sebagai model baseline (stabil, cepat).
3. IndoBERT fine-tuned untuk pemahaman konteks semantik.
4. Soft voting ensemble: Ensemble Score = 0.60 * P_IndoBERT + 0.40 * P_LogReg (dengan rule-override bila perlu).

## Struktur Direktori (ringkas)
```
seller-compliance-assistant/
├── backend/
│   ├── dataset/  # daftar_bahan_dilarang_bpom_terstandarisasi_lengkap.csv
│   ├── saved_models/
│   │   ├── indobert_bpom_model/
│   │   ├── logreg_baseline.joblib
│   │   └── tfidf_vectorizer.joblib
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   └── public/LogoSCA.jpg
├── docker-compose.yml
└── README.md
```

## Prasyarat
- Docker & Docker Compose (direkomendasikan), atau
- Node.js (v18+) untuk frontend dan Python 3.10/3.11 untuk backend.

## Menjalankan (Docker Compose)
1. Clone repositori dan masuk ke folder proyek:

```bash
git clone https://github.com/FadliGhafatulHijriah/seller-compliance-assistant.git
cd seller-compliance-assistant
```

2. Letakkan artefak model di `backend/saved_models/` (file .safetensors dan .joblib tidak dilacak di git).

3. Build dan jalankan service:

```bash
sudo docker compose up --build -d
```

4. Akses layanan:

- Frontend: http://localhost:3000
- Backend (Swagger): http://localhost:8000/docs

## Menjalankan secara manual (development)

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# Install PyTorch CPU wheels (contoh):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Catatan Model & Artefak
- `backend/saved_models/indobert_bpom_model/` — bobot IndoBERT (safetensors).
- `backend/saved_models/logreg_baseline.joblib` — model Logistic Regression.
- `backend/dataset/daftar_bahan_dilarang_bpom_terstandarisasi_lengkap.csv` — kamus bahan terlarang.

Model besar tidak disimpan di repository; simpan secara lokal atau unduh dari penyimpanan model terpisah.

## Endpoint API (ringkas)
- `GET /` — Health check.
- `POST /analyze` — Analisis teks deskripsi produk; mengembalikan skor risiko, highlights, dan rekomendasi.

## Kontribusi
- Buka issue atau PR untuk perbaikan fitur, dataset, atau dokumentasi.

## Lisensi
Lisensi proyek tercantum di file `LICENSE`.

