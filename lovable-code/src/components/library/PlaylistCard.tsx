import { Link } from "@tanstack/react-router";
import type { Playlist } from "../../lib/bridge";

interface Props {
  playlist: Playlist;
}

export function PlaylistCard({ playlist }: Props) {
  const isSpecial = playlist.id === "all" || playlist.id === "favorites";

  return (
    <Link
      to="/library/$playlistId"
      params={{ playlistId: playlist.id }}
      className="glass rounded-2xl overflow-hidden hover:-translate-y-1 transition group"
    >
      <div className="relative aspect-square overflow-hidden bg-muted/40 flex items-center justify-center">
        <span className="text-6xl">♪</span>
        {isSpecial ? (
          <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-primary/30 backdrop-blur border border-primary/50 text-xs font-medium flex items-center gap-1">
            ♪ Coleccion
          </div>
        ) : null}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-lg">{playlist.name}</h3>
        <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{playlist.description}</p>
        <div className="flex justify-between text-xs text-muted-foreground mt-3 font-mono">
          <span>{playlist.is_public ? "Publica" : "Privada"}</span>
        </div>
      </div>
    </Link>
  );
}
