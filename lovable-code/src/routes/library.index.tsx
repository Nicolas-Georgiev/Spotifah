import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { bridge, type Playlist } from "../lib/bridge";

export const Route = createFileRoute("/library/")({
  component: LibraryPage,
});

function LibraryPage() {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);

  useEffect(() => {
    bridge.getPlaylists().then(setPlaylists);
  }, []);

  const totalSongs = 0;

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold">Mi Biblioteca</h1>
        <p className="text-sm text-muted-foreground mt-1 font-mono">
          {playlists.length} playlists · {totalSongs} canciones
        </p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {playlists.map(p => (
          <Link
            key={p.id}
            to="/library/$playlistId"
            params={{ playlistId: p.id }}
            className="glass rounded-2xl overflow-hidden hover:-translate-y-1 transition group"
          >
            <div className="relative aspect-square overflow-hidden bg-muted/40 flex items-center justify-center">
              <span className="text-6xl">♪</span>
              {p.id === "all" || p.id === "favorites" ? (
                <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-primary/30 backdrop-blur border border-primary/50 text-xs font-medium flex items-center gap-1">
                  ♪ Coleccion
                </div>
              ) : null}
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg">{p.name}</h3>
              <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{p.description}</p>
              <div className="flex justify-between text-xs text-muted-foreground mt-3 font-mono">
                <span>{p.is_public ? "Publica" : "Privada"}</span>
              </div>
            </div>
          </Link>
        ))}

        <button
          type="button"
          className="glass rounded-2xl border-dashed border-2 border-border/60 flex flex-col items-center justify-center min-h-[280px] hover:bg-muted/20 transition group"
        >
          <div className="w-16 h-16 rounded-full bg-muted/40 grid place-items-center mb-3 group-hover:bg-primary/20 transition">
            <Plus className="w-7 h-7 text-muted-foreground group-hover:text-primary" />
          </div>
          <p className="font-semibold">Crear Nueva Playlist</p>
          <p className="text-xs text-muted-foreground mt-1">Agrupa tus canciones favoritas</p>
        </button>
      </section>
    </div>
  );
}
