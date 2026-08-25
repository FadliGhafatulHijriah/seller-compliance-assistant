"use client";

import { useState } from "react";

interface Issue {
  keyword: string;
  category?: string;
  reason?: string;
  recommendation?: string;
}

interface MetricsBreakdown {
  indobert_confidence?: number;
  baseline_confidence?: number;
}

interface AnalysisResult {
  status: string;
  status_label: string;
  risk_score: number;
  metrics_breakdown?: MetricsBreakdown;
  issues: Issue[];
  total_issues: number;
  summary_recommendation?: string;
}

export default function Home() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error("Gagal merespons dari server");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error analyzing text:", error);
      alert(
        "Gagal terhubung ke Backend FastAPI. Pastikan server backend sedang berjalan di port 8000!"
      );
    } finally {
      setLoading(false);
    }
  };

  // Helper untuk membuat regex yang toleran terhadap leetspeak dan pemisah karakter
  const buildFlexiblePattern = (keyword: string) => {
    const charMap: { [key: string]: string } = {
      a: "[a4@]",
      i: "[i1!|]",
      e: "[e3]",
      o: "[o0]",
      s: "[s5$]",
      b: "[b8]",
      g: "[g9]",
      t: "[t7]",
    };

    return keyword
      .split("")
      .map((char) => {
        const lower = char.toLowerCase();
        const pattern = charMap[lower] || lower.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        return pattern;
      })
      .join("[-_\\s]*");
  };

  // Fungsi highlight kata berisiko pada teks
  const renderHighlightedText = () => {
    if (!result || !result.issues || result.issues.length === 0) {
      return <p className="text-slate-700">{text}</p>;
    }

    const patterns = result.issues.map((i) => buildFlexiblePattern(i.keyword));
    const combinedRegex = new RegExp(`(${patterns.join("|")})`, "gi");
    const parts = text.split(combinedRegex);

    return (
      <p className="text-slate-800 leading-relaxed">
        {parts.map((part, index) => {
          const isMatch = result.issues.some((issue) => {
            const regexSingle = new RegExp(`^${buildFlexiblePattern(issue.keyword)}$`, "i");
            return regexSingle.test(part);
          });

          return isMatch ? (
            <mark
              key={index}
              className="bg-rose-200 text-rose-800 font-semibold px-1 rounded mx-0.5"
            >
              {part}
            </mark>
          ) : (
            part
          );
        })}
      </p>
    );
  };

  return (
    <main className="min-h-screen bg-slate-50 p-6 md:p-10 font-sans">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header dengan Logo Resmi SCA */}
        <header className="border-b border-slate-200 pb-4">
          <div className="flex items-center gap-3">
            <img
              src="/LogoSCA.png"
              alt="Logo SCA"
              className="w-10 h-10 rounded-lg object-cover shadow-sm border border-slate-200"
            />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-slate-800">
                  Seller Compliance Assistant (BPOM)
                </h1>
                <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded border border-blue-200">
                  AI IndoBERT Engine
                </span>
              </div>
              <p className="text-slate-600 text-sm mt-0.5">
                Deteksi dini klaim berlebihan (overclaim) & bahan dilarang sebelum memasarkan produk ke e-commerce.
              </p>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Form Input Teks */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="font-semibold text-slate-700">
                Teks Deskripsi / Komposisi Produk
              </h2>
              <span className="text-xs text-slate-400">{text.length} karakter</span>
            </div>

            <textarea
              className="w-full h-56 p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-slate-800"
              placeholder="Contoh: Krim pencerah wajah pasti ampuh mengobati flek hitam dalam seminggu..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />

            <button
              onClick={handleAnalyze}
              disabled={loading || !text.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors text-sm disabled:bg-slate-300 disabled:cursor-not-allowed flex justify-center items-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Menganalisis dengan AI...</span>
                </>
              ) : (
                "Analisis Kepatuhan Regulasi"
              )}
            </button>
          </div>

          {/* Panel Hasil Analisis */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 space-y-4">
            <h2 className="font-semibold text-slate-700">
              Hasil Evaluasi & Rekomendasi
            </h2>

            {!result && !loading && (
              <div className="h-56 flex items-center justify-center border-2 border-dashed border-slate-200 rounded-lg">
                <p className="text-slate-400 text-sm italic text-center px-4">
                  Masukkan deskripsi produk di sebelah kiri lalu klik "Analisis Kepatuhan Regulasi".
                </p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                {/* Status Badge & Skor Risiko */}
                <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-slate-50 border border-slate-200 rounded-lg">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-500 uppercase">Status:</span>
                    {result.total_issues === 0 && result.risk_score < 35 ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-300">
                        <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                        Aman / Patuh BPOM
                      </span>
                    ) : result.total_issues === 1 || (result.risk_score >= 20 && result.risk_score < 65) ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
                        <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                        Klaim Berisiko ({result.total_issues} Temuan)
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700 border border-rose-300">
                        <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                        Pelanggaran Regulasi ({result.total_issues} Temuan)
                      </span>
                    )}
                  </div>

                  <div className="text-right">
                    <span className="text-xs text-slate-500 block">Skor Risiko Pelanggaran:</span>
                    <span
                      className={`text-sm font-bold ${result.total_issues === 0 && result.risk_score < 35
                        ? "text-emerald-600"
                        : result.total_issues === 1 || (result.risk_score >= 20 && result.risk_score < 65)
                          ? "text-amber-600"
                          : "text-rose-600"
                        }`}
                    >
                      {result.risk_score}%
                    </span>
                  </div>
                </div>

                {/* Teks dengan Highlight */}
                <div className="p-3 bg-white rounded-lg border border-slate-200 text-sm max-h-36 overflow-y-auto">
                  {renderHighlightedText()}
                </div>

                {/* Detail Peringatan & Saran Edukasi */}
                {result.issues && result.issues.length > 0 ? (
                  <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                      Detail Temuan & Rekomendasi Edukasi:
                    </h3>
                    {result.issues.map((issue, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-rose-50 border-l-4 border-rose-500 text-xs text-slate-700 rounded-r space-y-1"
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-bold text-rose-700">
                            Frasa: "{issue.keyword}"
                          </span>
                          <span className="bg-rose-200 text-rose-800 px-2 py-0.5 rounded text-[10px] font-semibold">
                            {issue.category || issue.reason}
                          </span>
                        </div>
                        {issue.recommendation && (
                          <p className="text-slate-600 pt-1">
                            <span className="font-semibold text-emerald-700">💡 Saran Perbaikan: </span>
                            {issue.recommendation}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 bg-emerald-50 border-l-4 border-emerald-500 text-xs text-emerald-700 rounded-r">
                    ✅ {result.summary_recommendation || "Deskripsi produk memenuhi kaidah kepatuhan kosmetika regulasi BPOM No. 3 Tahun 2022."}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}