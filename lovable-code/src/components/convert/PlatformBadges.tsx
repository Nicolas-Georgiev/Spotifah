import { Youtube, Music2, Cloud } from "lucide-react";

export function PlatformBadges() {
  return (
    <div className="flex items-center gap-3 mt-4 text-xs flex-wrap">
      <span className="text-muted-foreground">Plataformas soportadas:</span>
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/15 text-red-400 border border-red-500/30">
        <Youtube className="w-3 h-3" /> YouTube
      </span>
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/15 text-green-400 border border-green-500/30">
        <Music2 className="w-3 h-3" /> Spotify
      </span>
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-500/15 text-yellow-400 border border-yellow-500/30">
        <Cloud className="w-3 h-3" /> SoundCloud
      </span>
    </div>
  );
}
