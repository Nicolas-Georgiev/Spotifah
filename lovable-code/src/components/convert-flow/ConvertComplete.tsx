import { Download, RotateCw } from "lucide-react";
import type { ThemeStyle } from "./types";

interface Props {
  preview: { title: string; subtitle: string };
  theme: ThemeStyle;
  onReset: () => void;
}

export function ConvertComplete({ preview, theme, onReset }: Props) {
  return (
    <div className={`glass rounded-2xl p-6 border ${theme.border} ${theme.glow}`}>
      <p className={`font-mono ${theme.color} ${theme.text} text-lg font-bold`}>
        ✅ ¡Conversión completada!
      </p>
      <div className="mt-4 bg-input/40 rounded-lg p-4 font-mono text-sm">
        <p><span className="text-muted-foreground">archivo:</span> {preview.subtitle.split(",")[0]} - {preview.title}.mp3</p>
        <p><span className="text-muted-foreground">ruta:</span> data/music/</p>
        <p><span className="text-muted-foreground">bitrate:</span> 192kbps</p>
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <button className={`px-5 py-2.5 rounded-lg font-medium ${theme.bg} text-background inline-flex items-center gap-2`}>
          <Download className="w-4 h-4" /> Descargar MP3
        </button>
        <button
          onClick={onReset}
          className="px-5 py-2.5 rounded-lg font-medium border border-border hover:bg-muted inline-flex items-center gap-2"
        >
          <RotateCw className="w-4 h-4" /> Convertir otra
        </button>
      </div>
    </div>
  );
}
