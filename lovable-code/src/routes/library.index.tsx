import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, useCallback } from "react";
import { bridge, type Playlist } from "../lib/bridge";
import { PlaylistGrid } from "../components/library/PlaylistGrid";

export const Route = createFileRoute("/library/")({
  component: LibraryPage,
});

function LibraryPage() {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);

  const load = useCallback(async () => {
    const p = await bridge.getPlaylists();
    setPlaylists(p);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold">Mi Biblioteca</h1>
        <p className="text-sm text-muted-foreground mt-1 font-mono">
          {playlists.length} playlists
        </p>
      </header>

      <PlaylistGrid playlists={playlists} onCreated={load} onChanged={load} />
    </div>
  );
}
