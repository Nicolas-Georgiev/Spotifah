import { Link } from "@tanstack/react-router";
import { Clock } from "lucide-react";
import { SongCard } from "../shared/SongCard";
import type { Song } from "../../lib/bridge";

interface Props {
  songs: Song[];
}

export function RecentSongsSection({ songs }: Props) {
  const recent = songs.slice(0, 4);

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Clock className="w-4 h-4 text-muted-foreground" />
          Canciones en tu Biblioteca
        </h2>
        <Link to="/library" className="text-xs text-muted-foreground hover:text-foreground">Ver todas</Link>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {recent.map(s => (
          <SongCard key={s.id} song={s} />
        ))}
      </div>
    </section>
  );
}
