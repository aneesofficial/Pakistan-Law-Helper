"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Scale, 
  Search, 
  BookOpen, 
  Landmark, 
  Info, 
  AlertCircle, 
  MapPin, 
  Loader2,
  FileText,
  ChevronDown,
  Check
} from "lucide-react";

interface Source {
  law_name: string;
  year: string;
  section_number: string;
  province: string;
  section_text: string;
}

interface AskResponse {
  answer: string;
  sources: Source[];
}

const LOADING_MESSAGES = [
  "Searching legal sources...",
  "Retrieving relevant sections...",
  "Generating grounded answer..."
];

export default function Home() {
  const [question, setQuestion] = useState("");
  const [province, setProvince] = useState("Federal");
  const [loading, setLoading] = useState(false);
  const [loadingMessageIdx, setLoadingMessageIdx] = useState(0);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Custom Dropdown State
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const PROVINCES = [
    { value: "Federal", label: "Federal (Always Included)" },
    { value: "Punjab", label: "Punjab" },
    { value: "Sindh", label: "Sindh" },
    { value: "Khyber Pakhtunkhwa", label: "Khyber Pakhtunkhwa" },
    { value: "Balochistan", label: "Balochistan" }
  ];

  // Rotating loading messages
  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setLoadingMessageIdx((prev) => (prev + 1) % LOADING_MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setLoadingMessageIdx(0);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          province,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch legal information. The backend might be unavailable or returned an error.");
      }

      const data: AskResponse = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-emerald-50/20 text-slate-700 font-sans selection:bg-emerald-100 selection:text-emerald-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-emerald-700 p-2 rounded-lg text-white">
              <Scale size={20} />
            </div>
            <span className="text-xl font-bold tracking-tight text-slate-900">
              Pakistan Law Helper
            </span>
          </div>
          <nav className="hidden sm:flex gap-6 text-sm font-medium text-slate-700">
            <a href="#" className="hover:text-emerald-700 transition-colors">Home</a>
            <a href="#" className="hover:text-emerald-700 transition-colors">Legal Assistant</a>
            <a href="#" className="hover:text-emerald-700 transition-colors">Sources</a>
            <a href="#" className="hover:text-emerald-700 transition-colors">About</a>
          </nav>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-12 relative z-0">
        {/* Subtle Radial Gradient Glow behind Hero */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-96 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-100/40 via-transparent to-transparent -z-10 pointer-events-none rounded-full blur-3xl opacity-50" />
        
        {/* Hero Section */}
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
            AI-Powered Legal Assistant for Pakistani Laws
          </h1>
          <p className="text-lg text-slate-600 leading-relaxed">
            An intelligent legal research platform that helps you find relevant sections of the law, supported by rigorous, <span className="text-emerald-700 font-medium">offline document retrieval</span> and <span className="text-emerald-700 font-medium">grounded citations</span>.
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200 overflow-hidden mb-12 max-w-3xl mx-auto">
          <div className="bg-white px-6 py-4 border-b border-slate-200 flex items-center gap-2">
            <Search size={18} className="text-emerald-700" />
            <h2 className="text-lg font-bold text-slate-900">Legal Inquiry</h2>
          </div>
          <div className="p-6">
            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
              
              <div className="flex flex-col gap-2">
                <label htmlFor="province" className="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                  <MapPin size={16} className="text-emerald-600 animate-soft-pulse" />
                  Jurisdiction Filter
                </label>
                <div className="relative w-full sm:w-72" ref={dropdownRef}>
                  <button
                    type="button"
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className={`w-full flex items-center justify-between border rounded-lg px-4 py-3 text-slate-700 bg-white transition-all text-sm font-medium shadow-sm outline-none ${isDropdownOpen ? 'border-amber-500 ring-2 ring-amber-500/50' : 'border-slate-300 hover:border-amber-500 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500'}`}
                    aria-haspopup="listbox"
                    aria-expanded={isDropdownOpen}
                  >
                    <span className="flex items-center gap-2">
                      {PROVINCES.find((p) => p.value === province)?.label}
                      {PROVINCES.find((p) => p.value === province)?.value === "Federal" && (
                        <span className="flex h-2 w-2 rounded-full bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.5)]" title="Default Jurisdiction"></span>
                      )}
                    </span>
                    <ChevronDown size={16} className={`text-slate-500 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
                  </button>

                  <div 
                    className={`absolute top-full left-0 w-full z-20 mt-2 bg-white border border-slate-200 rounded-lg shadow-lg overflow-hidden transition-all duration-200 origin-top ${isDropdownOpen ? 'opacity-100 scale-100 pointer-events-auto' : 'opacity-0 scale-95 pointer-events-none'}`} 
                    role="listbox"
                  >
                    {PROVINCES.map((p, idx) => (
                      <div
                        key={p.value}
                        role="option"
                        aria-selected={province === p.value}
                        tabIndex={0}
                        onClick={() => { setProvince(p.value); setIsDropdownOpen(false); }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            setProvince(p.value);
                            setIsDropdownOpen(false);
                          }
                        }}
                        className={`px-4 py-3 text-sm cursor-pointer flex items-center justify-between transition-colors duration-200 outline-none animate-fade-slide-up-stagger
                          ${province === p.value ? 'bg-emerald-50/80 text-emerald-800 font-semibold' : 'text-slate-700 hover:bg-emerald-50/50 focus:bg-emerald-50/50'}
                        `}
                        style={{ animationDelay: `${idx * 40}ms` }}
                      >
                        {p.label}
                        {province === p.value && <Check size={16} className="text-emerald-600" />}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="question" className="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                  <FileText size={16} className="text-slate-500" />
                  Your Legal Question
                </label>
                <textarea
                  id="question"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g., What is Article 14 of the Constitution of Pakistan?"
                  className="w-full border border-slate-300 rounded-lg px-4 py-3 text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 transition-shadow min-h-[120px] resize-y"
                  required
                />
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={loading || !question.trim()}
                  className="bg-emerald-700 hover:bg-emerald-800 text-white font-medium py-3 px-8 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] active:bg-emerald-900 min-w-[240px]"
                >
                  {loading ? (
                    <>
                      <Loader2 size={18} className="animate-spin shrink-0" />
                      <span>{LOADING_MESSAGES[loadingMessageIdx]}</span>
                    </>
                  ) : (
                    <>
                      <Search size={18} className="shrink-0" />
                      <span>Ask a Legal Question</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Results Section */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5 mb-8 flex items-start gap-3 max-w-3xl mx-auto">
            <AlertCircle className="text-red-600 mt-0.5 shrink-0" size={20} />
            <div className="text-red-800 text-sm">{error}</div>
          </div>
        )}

        {result && (
          <div className="space-y-8 animate-fade-slide-up max-w-3xl mx-auto">
            
            {/* Answer Card */}
            <div className="bg-white rounded-lg shadow-md border border-slate-200 overflow-hidden">
              <div className="bg-white px-6 py-4 border-b border-slate-200 flex items-center gap-2">
                <Landmark size={20} className="text-emerald-700" />
                <h2 className="text-lg font-bold text-slate-900">Legal Analysis</h2>
              </div>
              <div className="p-6 prose prose-slate max-w-none prose-p:leading-relaxed text-slate-700">
                {result.answer.split('\n').map((line, i) => (
                  <p key={i} className="mb-2 last:mb-0">{line}</p>
                ))}
              </div>
            </div>

            {/* Sources Header */}
            {result.sources.length > 0 && (
               <div>
                  <div className="flex items-center gap-2 mb-4 px-1">
                    <BookOpen size={20} className="text-slate-600" />
                    <h2 className="text-xl font-bold text-slate-900">Retrieved Legal Sources</h2>
                  </div>
                  
                  <div className="space-y-4">
                    {result.sources.map((source, idx) => (
                      <div key={idx} className="bg-white border border-slate-200 rounded-lg p-5 shadow-md hover:shadow-lg transition-shadow">
                        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-3 mb-4">
                          <h3 className="font-bold text-slate-900 text-lg">
                            {source.law_name} {source.year && source.year !== "N/A" ? `(${source.year})` : ""}
                          </h3>
                          <div className="flex flex-wrap gap-2 shrink-0">
                            <span className="bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                              Section {source.section_number}
                            </span>
                            <span className="bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                              {source.province}
                            </span>
                          </div>
                        </div>
                        <div className="bg-slate-50 border border-slate-100 rounded-lg p-4">
                          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                            <Info size={14} />
                            Relevant Extract
                          </p>
                          <p className="font-mono text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                            {source.section_text}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
               </div>
            )}
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="mt-20 border-t border-slate-800 bg-slate-900">
        <div className="max-w-5xl mx-auto px-4 py-8 flex flex-col items-center">
          <div className="flex items-center gap-2 mb-4 opacity-70">
            <Scale size={20} className="text-slate-300" />
            <span className="font-semibold text-slate-300">Pakistan Law Helper</span>
          </div>
          <p className="text-center text-sm text-slate-400 max-w-2xl">
            This application provides information from retrieved legal sources for educational and research purposes. It is not a substitute for professional legal advice. Always consult a qualified attorney for legal matters.
          </p>
        </div>
      </footer>
    </div>
  );
}
