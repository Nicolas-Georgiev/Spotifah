import { Youtube, Music2, Cloud } from "lucide-react";

interface Props {
  platform?: string | null;
}

const BADGES: Record<string, { icon: typeof Youtube; label: string; bg: string; text: string; border: string }> = {
  youtube: { icon: Youtube, label: "YouTube", bg: "bg-red-500/15", text: "text-red-400", border: "border-red-500/30" },
  spotify: { icon: Music2, label: "Spotify", bg: "bg-green-500/15", text: "text-green-400", border: "border-green-500/30" },
  soundcloud: { icon: Cloud, label: "SoundCloud", bg: "bg-yellow-500/15", text: "text-yellow-400", border: "border-yellow-500/30" },
};

export function PlatformBadges({ platform }: Props = {}) {
  if (platform) {
    const b = BADGES[platform];
    if (!b) return null;
    const Icon = b.icon;
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full ${b.bg} ${b.text} ${b.border} border text-xs`}>
        <Icon className="w-3 h-3" /> {b.label}
      </span>
    );
  }

  return (
    <div className="flex items-center gap-3 mt-4 text-xs flex-wrap">
      <span className="text-muted-foreground">Plataformas soportadas:</span>
      {Object.values(BADGES).map((b) => {
        const Icon = b.icon;
        return (
          <span key={b.label} className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full ${b.bg} ${b.text} ${b.border} border`}>
            <Icon className="w-3 h-3" /> {b.label}
          </span>
        );
      })}
    </div>
  );
}
