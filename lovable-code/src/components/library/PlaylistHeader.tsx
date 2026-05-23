import { Play } from "lucide-react";
import type { Playlist, Song } from "../../lib/bridge";

interface Props {
  playlist: Playlist;
  songs: Song[];
  totalMin: number;
  onPlayAll: () => void;
}

export function PlaylistHeader({ playlist, songs, totalMin, onPlayAll }: Props) {
  return (
    <>
      <header className="flex flex-col sm:flex-row gap-6 items-center sm:items-end">
        <div className="w-40 h-40 sm:w-48 sm:h-48 rounded-2xl bg-primary/20 flex items-center justify-center text-6xl shadow-2xl">
          ♪
        </div>
        <div className="text-center sm:text-left flex-1">
          <div className="flex flex-wrap items-center gap-2 justify-center sm:justify-start">
            <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-primary/20 text-primary border border-primary/40">
              Playlist
            </span>
          </div>
          <h1 className="text-4xl sm:text-6xl font-bold mt-3">{playlist.name}</h1>
          <p className="text-muted-foreground mt-2">{playlist.description}</p>
          <p className="text-xs text-muted-foreground font-mono mt-3">
            {songs.length} canciones · {totalMin} min
          </p>
        </div>
      </header>

      <button
        onClick={onPlayAll}
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-primary text-primary-foreground font-semibold glow-violet hover:scale-105 transition"
      >
        <Play className="w-4 h-4 fill-current" /> Reproducir todo
      </button>
    </>
  );
}
