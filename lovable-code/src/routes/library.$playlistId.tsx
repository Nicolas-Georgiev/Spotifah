import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useEffect, useState, useMemo } from "react";
import { ChevronLeft } from "lucide-react";
import { bridge, type Song } from "../lib/bridge";
import { PlaylistHeader } from "../components/library/PlaylistHeader";
import { SongTable, sortSongs, type SortConfig } from "../components/library/SongTable";

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
  const [sort, setSort] = useState<SortConfig | null>(null);

  useEffect(() => {
    bridge.getPlaylistSongs(playlist.id).then(setSongs);
    const defaultSort: SortConfig | null = playlist.id === "all"
      ? { key: "download_date", dir: "desc" }
      : null;
    setSort(defaultSort);
  }, [playlist.id]);

  const sortedSongs = useMemo(() => sortSongs(songs, sort), [songs, sort]);

  const totalSecs = sortedSongs.reduce((acc, s) => acc + s.duration, 0);
  const totalMin = Math.round(totalSecs / 60);

  const handlePlay = (songId: string) => {
    setPlayingId(songId);
    bridge.playSong(songId, sortedSongs.map((s) => s.id));
  };

  const handleRemove = async (songId: string) => {
    await bridge.removeSongFromPlaylist(playlist.id, songId);
    setSongs((prev) => prev.filter((s) => s.id !== songId));
  };

  const handleSongDeleted = async (songId: string) => {
    setSongs((prev) => prev.filter((s) => s.id !== songId));
  };

  const handleSongUpdated = async () => {
    const freshSongs = await bridge.getPlaylistSongs(playlist.id);
    setSongs(freshSongs);
  };

  return (
    <div className="space-y-8">
      <Link to="/library" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ChevronLeft className="w-4 h-4" /> Volver a Biblioteca
      </Link>

      <PlaylistHeader
        playlist={playlist}
        songs={sortedSongs}
        totalMin={totalMin}
        onPlayAll={() => sortedSongs.length > 0 && handlePlay(sortedSongs[0].id)}
      />

      <SongTable
        songs={sortedSongs}
        playingId={playingId}
        onPlay={handlePlay}
        fmtDuration={fmtDuration}
        playlistId={playlist.id}
        onRemoveFromPlaylist={handleRemove}
        onSongDeleted={handleSongDeleted}
        onSongUpdated={handleSongUpdated}
        sort={sort}
        onSortChange={setSort}
      />
    </div>
  );
}
