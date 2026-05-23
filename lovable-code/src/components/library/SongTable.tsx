import { useState, useMemo } from "react";
import { ArrowUpDown, ArrowUp, ArrowDown, Clock } from "lucide-react";
import { SongRow } from "./SongRow";
import type { Song } from "../../lib/bridge";
import { GlassCard } from "../shared/GlassCard";

interface Props {
  songs: Song[];
  playingId: string | null;
  onPlay: (id: string) => void;
  fmtDuration: (seconds: number) => string;
  playlistId?: string;
  onRemoveFromPlaylist?: (songId: string) => void;
  onSongDeleted?: (songId: string) => void;
}

type SortKey = "title" | "artist" | "album" | "source" | "duration" | "download_date";
type SortDir = "asc" | "desc";

interface SortConfig {
  key: SortKey;
  dir: SortDir;
}

function sortSongs(songs: Song[], config: SortConfig | null): Song[] {
  if (!config) return songs;
  const { key, dir } = config;
  const mult = dir === "asc" ? 1 : -1;
  return [...songs].sort((a, b) => {
    if (key === "duration") {
      return (a.duration - b.duration) * mult;
    }
    if (key === "download_date") {
      if (!a.download_date && !b.download_date) return 0;
      if (!a.download_date) return 1;
      if (!b.download_date) return -1;
      return a.download_date.localeCompare(b.download_date) * mult;
    }
    const va = (a as any)[key] || "";
    const vb = (b as any)[key] || "";
    return va.localeCompare(vb, "es") * mult;
  });
}

const HEADERS: { key: SortKey | null; label: string; className?: string }[] = [
  { key: null, label: "#" },
  { key: "title", label: "Titulo" },
  { key: "artist", label: "Artista" },
  { key: "album", label: "Album" },
  { key: "source", label: "Origen" },
  { key: "duration", label: "", className: "flex justify-end" },
  { key: "download_date", label: "Descarga" },
  { key: null, label: "" },
];

export function SongTable({ songs, playingId, onPlay, fmtDuration, playlistId, onRemoveFromPlaylist, onSongDeleted }: Props) {
  const [sort, setSort] = useState<SortConfig | null>(null);

  const toggleSort = (key: SortKey) => {
    setSort((prev) => {
      if (!prev || prev.key !== key) return { key, dir: "asc" };
      if (prev.dir === "asc") return { key, dir: "desc" };
      return null;
    });
  };

  const sorted = useMemo(() => sortSongs(songs, sort), [songs, sort]);

  const renderSortIcon = (key: SortKey | null) => {
    if (!key) return null;
    const active = sort?.key === key;
    if (!active) return <ArrowUpDown className="w-3 h-3 ml-1 opacity-30" />;
    return sort?.dir === "asc"
      ? <ArrowUp className="w-3 h-3 ml-1 text-primary" />
      : <ArrowDown className="w-3 h-3 ml-1 text-primary" />;
  };

  return (
    <GlassCard className="overflow-hidden p-0">
      <div className="hidden md:grid grid-cols-[40px_3fr_2fr_2fr_100px_80px_130px_80px] gap-4 px-5 py-3 text-xs font-mono text-muted-foreground border-b border-border uppercase tracking-wider">
        {HEADERS.map((h) =>
          h.key ? (
            <button
              key={h.key}
              onClick={() => toggleSort(h.key!)}
              className={`flex items-center gap-0 text-left hover:text-foreground transition ${h.className || ""}`}
            >
              {h.label === "" ? <Clock className="w-3.5 h-3.5" /> : h.label}
              {h.label === "" ? null : renderSortIcon(h.key)}
            </button>
          ) : (
            <span key={h.label} className={h.className || ""}>
              {h.label === "" && h.className?.includes("flex") ? <Clock className="w-3.5 h-3.5" /> : h.label}
            </span>
          )
        )}
      </div>
      <ul>
        {sorted.map((s, i) => (
          <SongRow
            key={s.id}
            song={s}
            index={i}
            isActive={playingId === s.id}
            onPlay={onPlay}
            fmtDuration={fmtDuration}
            playlistId={playlistId}
            onRemoveFromPlaylist={onRemoveFromPlaylist}
            onSongDeleted={onSongDeleted}
          />
        ))}
      </ul>
    </GlassCard>
  );
}


