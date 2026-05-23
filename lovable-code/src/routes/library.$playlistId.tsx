import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ChevronLeft } from "lucide-react";
import { bridge, type Song } from "../lib/bridge";
import { PlaylistHeader } from "../components/library/PlaylistHeader";
import { SongTable } from "../components/library/SongTable";

export const Route = createFileRoute("/library/$playlistId")({
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

  const handleRemove = async (songId: string) => {
    await bridge.removeSongFromPlaylist(playlist.id, songId);
    setSongs((prev) => prev.filter((s) => s.id !== songId));
  };

  return (
    <div className="space-y-8">
      <Link to="/library" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ChevronLeft className="w-4 h-4" /> Volver a Biblioteca
      </Link>

      <PlaylistHeader
        playlist={playlist}
        songs={songs}
        totalMin={totalMin}
        onPlayAll={() => songs.length > 0 && handlePlay(songs[0].id)}
      />

      <SongTable
        songs={songs}
        playingId={playingId}
        onPlay={handlePlay}
        fmtDuration={fmtDuration}
        playlistId={playlist.id}
        onRemoveFromPlaylist={handleRemove}
      />
    </div>
  );
}
