import { Clock } from "lucide-react";
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
}

export function SongTable({ songs, playingId, onPlay, fmtDuration, playlistId, onRemoveFromPlaylist }: Props) {
  return (
    <GlassCard className="overflow-hidden p-0">
      <div className="hidden md:grid grid-cols-[40px_3fr_2fr_2fr_120px_80px_40px] gap-4 px-5 py-3 text-xs font-mono text-muted-foreground border-b border-border uppercase tracking-wider">
        <span>#</span>
        <span>Titulo</span>
        <span>Artista</span>
        <span>Album</span>
        <span>Origen</span>
        <span className="flex justify-end"><Clock className="w-3.5 h-3.5" /></span>
        <span></span>
      </div>
      <ul>
        {songs.map((s, i) => (
          <SongRow
            key={s.id}
            song={s}
            index={i}
            isActive={playingId === s.id}
            onPlay={onPlay}
            fmtDuration={fmtDuration}
            playlistId={playlistId}
            onRemoveFromPlaylist={onRemoveFromPlaylist}
          />
        ))}
      </ul>
    </GlassCard>
  );
}
