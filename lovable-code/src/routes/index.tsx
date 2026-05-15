import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Clock } from "lucide-react";
import { bridge, type Playlist, type Song } from "../lib/bridge";

export const Route = createFileRoute("/")({
  component: Home,
});

function getGreeting() {
  const h = new Date().getHours();
  if (h < 6) return "Buenas noches";
  if (h < 13) return "Buenos dias";
  if (h < 20) return "Buenas tardes";
  return "Buenas noches";
}

function Home() {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [songs, setSongs] = useState<Song[]>([]);

  useEffect(() => {
    bridge.getPlaylists().then(setPlaylists);
    bridge.getSongs().then(setSongs);
  }, []);

  const greeting = getGreeting();
  const recent = songs.slice(0, 4);

  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-4xl sm:text-5xl font-bold">{greeting}</h1>
        <p className="text-muted-foreground mt-2">Que te gustaria escuchar hoy?</p>
      </section>

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
              <div className="w-14 h-14 rounded-md bg-primary/20 flex items-center justify-center text-lg shrink-0">
                ♪
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold truncate">{p.name}</p>
                <p className="text-xs text-muted-foreground">{p.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

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
            <Link
              key={s.id}
              to="/library/$playlistId"
              params={{ playlistId: "all" }}
              className="group"
            >
              <div className="relative rounded-xl overflow-hidden aspect-square bg-muted/40 flex items-center justify-center">
                {s.cover_url ? (
                  <img src={s.cover_url} alt={s.title} className="w-full h-full object-cover transition group-hover:scale-105" />
                ) : (
                  <span className="text-4xl">♪</span>
                )}
              </div>
              <p className="mt-3 font-semibold truncate">{s.title}</p>
              <p className="text-sm text-muted-foreground truncate">{s.artist}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
