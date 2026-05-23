import { Download } from "lucide-react";
import type { ThemeStyle } from "./types";

interface Props {
  preview: { title: string; subtitle: string; album?: string; year?: string; cover: string };
  theme: ThemeStyle;
  onConvert: () => void;
  disabled: boolean;
}

export function ConvertPreview({ preview, theme, onConvert, disabled }: Props) {
  return (
    <div className="glass rounded-2xl p-6 flex flex-col sm:flex-row gap-6 items-center sm:items-start">
      <img
        src={preview.cover}
        alt={preview.title}
        className={`w-32 h-32 rounded-full object-cover border-4 ${theme.border} ${theme.glow}`}
      />
      <div className="flex-1 text-center sm:text-left">
        <h3 className="text-2xl font-bold">{preview.title}</h3>
        <p className="text-muted-foreground">{preview.subtitle}</p>
        {preview.album && (
          <p className="text-sm text-muted-foreground mt-1">{preview.album} · {preview.year}</p>
        )}
        <button
          onClick={onConvert}
          disabled={disabled}
          className={`mt-4 px-6 py-3 rounded-lg font-bold ${theme.bg} text-background ${theme.glow} hover:opacity-90 inline-flex items-center gap-2 disabled:opacity-60`}
        >
          <Download className="w-5 h-5" /> CONVERTIR A MP3
        </button>
      </div>
    </div>
  );
}
