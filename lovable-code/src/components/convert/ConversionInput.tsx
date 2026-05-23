import { Link2, Download, Loader2 } from "lucide-react";
import { PlatformBadges } from "./PlatformBadges";

interface Props {
  url: string;
  onUrlChange: (url: string) => void;
  onConvert: () => void;
  busy: boolean;
}

export function ConversionInput({ url, onUrlChange, onConvert, busy }: Props) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Link2 className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            value={url}
            onChange={(e) => onUrlChange(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onConvert()}
            placeholder="Pega aqui el enlace de YouTube, Spotify o SoundCloud..."
            className="w-full bg-input/60 border border-border rounded-lg pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button
          onClick={onConvert}
          disabled={!url.trim() || busy}
          className="px-6 py-3 rounded-lg font-medium bg-primary text-primary-foreground glow-violet hover:opacity-90 inline-flex items-center gap-2 justify-center disabled:opacity-50"
        >
          {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
          Convertir
        </button>
      </div>
      <PlatformBadges />
    </div>
  );
}
