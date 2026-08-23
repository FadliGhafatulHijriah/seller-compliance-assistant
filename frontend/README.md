<div align="center">
  <img src="frontend/public/LogoSCA.jpg" alt="Seller Compliance Assistant Logo" width="160" style="border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />

  # 🛡️ Seller Compliance Assistant (BPOM)

  <p align="center">
    <strong>Sistem Asisten Kepatuhan Cerdas Berbasis Arsitektur Hibrida (IndoBERT + Soft Voting Ensemble + Aho-Corasick Automaton) untuk Deteksi Dini Klaim Berlebihan (<i>Overclaim</i>) dan Bahan Berbahaya pada E-Commerce.</strong>
  </p>

  <p align="center">
    <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Frontend-Next.js%2014%2F16-black?style=flat&logo=next.js" alt="Next.js" /></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi" alt="FastAPI" /></a>
    <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/AI%20Framework-PyTorch%20%2F%20HuggingFace-EE4C2C?style=flat&logo=pytorch" alt="PyTorch" /></a>
    <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Container-Docker%20Compose-2496ED?style=flat&logo=docker" alt="Docker" /></a>
    <a href="https://www.pom.go.id/"><img src="https://img.shields.io/badge/Regulasi-BPOM%20No.%203%2F2022-blue" alt="Compliance" /></a>
  </p>
</div>

---

## 🎨 Makna & Filosofi Logo

Logo **Seller Compliance Assistant (SCA)** merepresentasikan 3 pilar utama sistem:
* **Bentuk Perisai & Ceklis (Keamanan & Kepatuhan):** Melambangkan perlindungan preventif bagi penjual (*seller protection*) dan jaminan kesesuaian dengan standar hukum BPOM.
* **Elemen Daun Hijau (Alami & Kosmetik Sehat):** Menggambarkan fokus pengawasan sediaan kosmetik, bahan alam, dan produk perawatan kulit yang aman.
* **Gradasi Biru & Kurva Dinamis (Teknologi Cerdas AI):** Melambangkan integrasi kecerdasan buatan (*Machine Learning & Deep Learning*) yang adaptif, presisi, dan modern.

---

## 📌 1. Latar Belakang & Urgensi Proyek

Pertumbuhan pesat platform *e-commerce* di Indonesia diiringi dengan tingginya peredaran produk kosmetika dan obat tradisional yang memuat **klaim kesehatan terlarang/berlebihan (*overclaim*)** serta kandungan bahan berbahaya. Berdasarkan **Peraturan BPOM No. 3 Tahun 2022**, kosmetika dilarang mencantumkan klaim pengobatan/medis yang menyesatkan konsumen.

Banyak UMKM dan penjual online (*sellers*) melakukan pelanggaran bukan karena kesengajaan, melainkan karena **kurangnya literasi regulasi** dan ketiadaan alat validasi otomatis sebelum menerbitkan deskripsi produk. Hal ini memicu risiko pemblokiran etalase toko (*takedown*), sanksi hukum, serta kerugian perlindungan konsumen.

**Seller Compliance Assistant** hadir sebagai platform asistensi *pre-listing compliance* yang memanfaatkan kecerdasan buatan untuk menganalisis teks promosi secara instan, menyajikan visualisasi *highlight* kata berisiko, serta memberikan saran edukasi perbaikan klaim yang sah secara regulasi.

---

## 🧠 2. Arsitektur Kecerdasan Buatan & Metodologi

Sistem ini menerapkan pendekatan **Multi-Layer Hybrid Compliance Architecture**: