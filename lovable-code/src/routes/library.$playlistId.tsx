import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Play, ChevronLeft, Clock } from "lucide-react";
import { bridge, type Song, type Playlist } from "../lib/bridge";

export const Route = createFileRoute("/library/$playlistId")({
  head: ({ params }) => {
    return { meta: [{ title: `Playlist — EKHO` }] };
  },
  loader: async ({ params }) => {
    const playlists = await bridge.getPlaylists();
    const playlist = playlists.find((p) => p.id === params.playlistId);
    if (!playlist) throw notFound();
    return { playlist };
  },
  notFoundComponent: () => (
    <div className="text-center py-20">
      <h1 className="text-2xl font-bold">Playlist no encontrada</h1>
      <Link to="/library" className="inline-block mt-4 text-primary underline">
        Volver a la biblioteca
      </Link>
    </div>
  ),
  errorComponent: ({ error }) => <div className="p-6 text-destructive">{error.message}</div>,
  component: PlaylistDetail,
});

function fmtDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function PlaylistDetail() {
  const { playlist } = Route.useLoaderData();
  const [songs, setSongs] = useState<Song[]>([]);
  const [playingId, setPlayingId] = useState<string | null>(null);

  useEffect(() => {
    bridge.getPlaylistSongs(playlist.id).then(setSongs);
  }, [playlist.id]);

  const totalSecs = songs.reduce((acc, s) => acc + s.duration, 0);
  const totalMin = Math.round(totalSecs / 60);

  const handlePlay = (songId: string) => {
    setPlayingId(songId);
    bridge.playSong(songId);
  };

  return (
    <div className="space-y-8">
      <Link to="/library" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ChevronLeft className="w-4 h-4" /> Volver a Biblioteca
      </Link>

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
        onClick={() => songs.length > 0 && handlePlay(songs[0].id)}
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-primary text-primary-foreground font-semibold glow-violet hover:scale-105 transition"
      >
        <Play className="w-4 h-4 fill-current" /> Reproducir todo
      </button>

      <section className="glass rounded-2xl overflow-hidden">
        <div className="hidden md:grid grid-cols-[40px_3fr_2fr_2fr_120px_80px] gap-4 px-5 py-3 text-xs font-mono text-muted-foreground border-b border-border uppercase tracking-wider">
          <span>#</span>
          <span>Titulo</span>
          <span>Artista</span>
          <span>Album</span>
          <span>Origen</span>
          <span className="flex justify-end"><Clock className="w-3.5 h-3.5" /></span>
        </div>
        <ul>
          {songs.map((s, i) => (
            <li
              key={s.id}
              onClick={() => handlePlay(s.id)}
              className={`grid grid-cols-[40px_3fr_2fr_2fr_120px_80px] gap-4 px-5 py-3 items-center hover:bg-muted/30 transition group cursor-pointer ${
                playingId === s.id ? "bg-primary/10" : ""
              }`}
            >
              <span className="text-sm font-mono text-muted-foreground group-hover:hidden">{i + 1}</span>
              <Play className="w-4 h-4 hidden group-hover:block fill-current text-primary" />
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded bg-muted/40 flex items-center justify-center shrink-0">
                  {s.cover_url ? (
                    <img src={s.cover_url} alt="" className="w-full h-full rounded object-cover" />
                  ) : (
                    <span className="text-lg">♪</span>
                  )}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">{s.title}</p>
                </div>
              </div>
              <span className="text-sm text-muted-foreground truncate">{s.artist}</span>
              <span className="text-sm text-muted-foreground truncate">{s.album}</span>
              <span>
                {s.source === "spotify" ? (
                  <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/30">
                    spotify
                  </span>
                ) : (
                  <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400 border border-red-500/30">
                    {s.source || "local"}
                  </span>
                )}
              </span>
              <span className="text-sm text-muted-foreground font-mono text-right">{fmtDuration(s.duration)}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
