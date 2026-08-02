"use client";

import { useState } from "react";

interface Issue {
  keyword: string;
  type: string;
  reason: string;
}

interface AnalysisResult {
  status: string;
  risk_level: string;
  total_issues: number;
  issues: Issue[];
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
      // Sesuaikan dengan port Uvicorn kamu (biasanya 8000)
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error analyzing text:", error);
      alert(
        "Gagal terhubung ke Backend FastAPI. Pastikan server Uvicorn di backend sedang menyala!",
      );
    } finally {
      setLoading(false);
    }
  };

  // Fungsi untuk highlight kata berisiko pada teks
  const renderHighlightedText = () => {
    if (!result || result.issues.length === 0)
      return <p className="text-gray-700">{text}</p>;

    const keywords = result.issues.map((i) => i.keyword.toLowerCase());
    const regex = new RegExp(`(${keywords.join("|")})`, "gi");
    const parts = text.split(regex);

    return (
      <p className="text-gray-800 leading-relaxed">
        {parts.map((part, index) => {
          const isForbidden = keywords.includes(part.toLowerCase());
          return isForbidden ? (
            <mark
              key={index}
              className="bg-red-200 text-red-800 font-semibold px-1 rounded"
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
    <main className="min-h-screen bg-slate-50 p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-6">
        <header className="border-b pb-4">
          <h1 className="text-2xl font-bold text-slate-800">
            🛡️ Seller Compliance Assistant (BPOM)
          </h1>
          <p className="text-slate-600 text-sm">
            Deteksi dini klaim berlebihan (overclaim) & kata berisiko sebelum
            memasarkan produk ke e-commerce.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Form Input Teks */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 space-y-4">
            <h2 className="font-semibold text-slate-700">
              Teks Deskripsi / Caption Produk
            </h2>
            <textarea
              className="w-full h-48 p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-slate-800"
              placeholder="Contoh: Obat herbal ini pasti ampuh mengobati dan menyembuhkan segala jenis penyakit tanpa efek samping..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm disabled:bg-slate-400"
            >
              {loading ? "Menganalisis..." : "Analisis Kepatuhan BPOM"}
            </button>
          </div>

          {/* Panel Hasil Analisis */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 space-y-4">
            <h2 className="font-semibold text-slate-700">
              Hasil Analisis & Highlight
            </h2>

            {!result && !loading && (
              <p className="text-slate-400 text-sm italic">
                Masukkan deskripsi di sebelah kiri lalu klik Analisis.
              </p>
            )}

            {result && (
              <div className="space-y-4">
                {/* Status Badge */}
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-700">
                    Tingkat Risiko:
                  </span>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${
                      result.risk_level === "HIGH"
                        ? "bg-red-100 text-red-700 border border-red-300"
                        : "bg-green-100 text-green-700 border border-green-300"
                    }`}
                  >
                    {result.risk_level}
                  </span>
                </div>

                {/* Teks dengan Highlight */}
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-sm">
                  {renderHighlightedText()}
                </div>

                {/* Detail Peringatan */}
                {result.issues.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                      Detail Peringatan ({result.total_issues}):
                    </h3>
                    {result.issues.map((issue, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-red-50 border-l-4 border-red-500 text-xs text-red-700 rounded-r"
                      >
                        <p className="font-semibold">
                          Kata Kunci: "{issue.keyword}"
                        </p>
                        <p>{issue.reason}</p>
                      </div>
                    ))}
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
