import { useState } from "react";
import { Search } from "lucide-react";
import { themeMap, type ConvertTheme } from "./convert-flow/types";
import { ConvertPreview } from "./convert-flow/ConvertPreview";
import { ConvertProgress } from "./convert-flow/ConvertProgress";
import { ConvertComplete } from "./convert-flow/ConvertComplete";

export type { ConvertTheme };

interface Step { icon: string; label: string; }

interface Props {
  theme: ConvertTheme;
  title: string;
  placeholder: string;
  helper: string;
  steps: Step[];
  preview: { title: string; subtitle: string; album?: string; year?: string; cover: string };
}

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
        <ConvertPreview
          preview={preview}
          theme={t}
          onConvert={convert}
          disabled={stepIdx >= 0 && !done}
        />
      )}

      {stepIdx >= 0 && (
        <ConvertProgress
          steps={steps}
          stepIdx={stepIdx}
          done={done}
          theme={t}
        />
      )}

      {done && (
        <ConvertComplete
          preview={preview}
          theme={t}
          onReset={reset}
        />
      )}
    </div>
  );
}
