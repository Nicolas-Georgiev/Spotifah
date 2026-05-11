import { useState } from "react";
import { Search, Download, Check, Loader2, RotateCw } from "lucide-react";

export type ConvertTheme = "spotify" | "youtube";

interface Step { icon: string; label: string; }

interface Props {
  theme: ConvertTheme;
  title: string;
  placeholder: string;
  helper: string;
  steps: Step[];
  preview: { title: string; subtitle: string; album?: string; year?: string; cover: string };
}

const themeMap = {
  spotify: {
    color: "text-[oklch(0.85_0.22_150)]",
    border: "border-[oklch(0.85_0.22_150)]/50",
    bg: "bg-[oklch(0.85_0.22_150)]",
    glow: "glow-green",
    text: "text-glow-green",
  },
  youtube: {
    color: "text-[oklch(0.65_0.25_25)]",
    border: "border-[oklch(0.65_0.25_25)]/50",
    bg: "bg-[oklch(0.65_0.25_25)]",
    glow: "glow-red",
    text: "text-glow-red",
  },
};

export function ConvertFlow({ theme, title, placeholder, helper, steps, preview }: Props) {
  const t = themeMap[theme];
  const [url, setUrl] = useState("");
  const [analyzed, setAnalyzed] = useState(false);
  const [stepIdx, setStepIdx] = useState(-1);
  const [done, setDone] = useState(false);

  const analyze = () => {
    if (!url.trim()) return;
    setAnalyzed(true);
    setDone(false);
    setStepIdx(-1);
  };

  const convert = () => {
    setStepIdx(0);
    setDone(false);
    let i = 0;
    const tick = () => {
      i++;
      if (i >= steps.length) {
        setStepIdx(steps.length);
        setDone(true);
      } else {
        setStepIdx(i);
        setTimeout(tick, 900);
      }
    };
    setTimeout(tick, 900);
  };

  const reset = () => { setUrl(""); setAnalyzed(false); setStepIdx(-1); setDone(false); };

  return (
    <div className="space-y-8">
      <header>
        <div className={`font-mono text-2xl sm:text-3xl font-bold ${t.color} ${t.text}`}>{title}</div>
        <p className="font-mono text-xs text-muted-foreground mt-2">══════════════════════════════════════</p>
      </header>

      <div className="glass rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={placeholder}
            className={`flex-1 bg-input/60 border ${t.border} rounded-lg px-4 py-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-current ${t.color}`}
          />
          <button
            onClick={analyze}
            className={`px-5 py-3 rounded-lg font-medium ${t.bg} text-background hover:opacity-90 ${t.glow} flex items-center gap-2 justify-center`}
          >
            <Search className="w-4 h-4" /> Analizar
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-3 font-mono">{helper}</p>
      </div>

      {analyzed && (
        <div className="glass rounded-2xl p-6 flex flex-col sm:flex-row gap-6 items-center sm:items-start">
          <img src={preview.cover} alt={preview.title} className={`w-32 h-32 rounded-full object-cover border-4 ${t.border} ${t.glow}`} />
          <div className="flex-1 text-center sm:text-left">
            <h3 className="text-2xl font-bold">{preview.title}</h3>
            <p className="text-muted-foreground">{preview.subtitle}</p>
            {preview.album && <p className="text-sm text-muted-foreground mt-1">{preview.album} · {preview.year}</p>}
            <button
              onClick={convert}
              disabled={stepIdx >= 0 && !done}
              className={`mt-4 px-6 py-3 rounded-lg font-bold ${t.bg} text-background ${t.glow} hover:opacity-90 inline-flex items-center gap-2 disabled:opacity-60`}
            >
              <Download className="w-5 h-5" /> CONVERTIR A MP3
            </button>
          </div>
        </div>
      )}

      {stepIdx >= 0 && (
        <div className="glass rounded-2xl p-6">
          <h3 className="font-mono text-sm text-muted-foreground mb-4">// Progreso</h3>
          <ol className="space-y-3">
            {steps.map((s, i) => {
              const completed = i < stepIdx || done;
              const active = i === stepIdx && !done;
              return (
                <li key={i} className={`flex items-center gap-3 font-mono text-sm ${completed ? t.color : active ? "text-foreground" : "text-muted-foreground/50"}`}>
                  <div className={`w-6 h-6 rounded-full grid place-items-center border ${completed ? `${t.border} ${t.bg}/20` : "border-border"}`}>
                    {completed ? <Check className="w-3.5 h-3.5" /> : active ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <span className="text-xs">{i+1}</span>}
                  </div>
                  <span>{s.icon} {s.label}</span>
                </li>
              );
            })}
          </ol>
        </div>
      )}

      {done && (
        <div className={`glass rounded-2xl p-6 border ${t.border} ${t.glow}`}>
          <p className={`font-mono ${t.color} ${t.text} text-lg font-bold`}>✅ ¡Conversión completada!</p>
          <div className="mt-4 bg-input/40 rounded-lg p-4 font-mono text-sm">
            <p><span className="text-muted-foreground">archivo:</span> {preview.subtitle.split(",")[0]} - {preview.title}.mp3</p>
            <p><span className="text-muted-foreground">ruta:</span> data/music/</p>
            <p><span className="text-muted-foreground">bitrate:</span> 192kbps</p>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <button className={`px-5 py-2.5 rounded-lg font-medium ${t.bg} text-background inline-flex items-center gap-2`}>
              <Download className="w-4 h-4" /> Descargar MP3
            </button>
            <button onClick={reset} className="px-5 py-2.5 rounded-lg font-medium border border-border hover:bg-muted inline-flex items-center gap-2">
              <RotateCw className="w-4 h-4" /> Convertir otra
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
