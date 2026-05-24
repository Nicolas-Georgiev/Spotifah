import { Link } from "@tanstack/react-router";
import type { Playlist } from "../../lib/bridge";

interface Props {
  playlists: Playlist[];
}

export function QuickAccessSection({ playlists }: Props) {
  return (
    <section>
      <h2 className="text-lg font-semibold mb-4">Acceso Rapido</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {playlists.map(p => (
          <Link
            key={p.id}
            to="/library/$playlistId"
            params={{ playlistId: p.id }}
            className="glass rounded-xl p-3 flex items-center gap-4 hover:bg-muted/30 transition group"
          >
            {p.cover_url ? (
              <div className="w-14 h-14 rounded-md overflow-hidden shrink-0">
                <img src={p.cover_url} alt={p.name} className="w-full h-full object-cover" />
              </div>
            ) : (
              <div className="w-14 h-14 rounded-md bg-primary/20 flex items-center justify-center text-lg shrink-0">♪</div>
            )}
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{p.name}</p>
              <p className="text-xs text-muted-foreground">{p.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
