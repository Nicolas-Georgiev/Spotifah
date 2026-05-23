import { createFileRoute } from "@tanstack/react-router";
import { useEffect } from "react";
import { PlaylistGrid } from "../components/library/PlaylistGrid";
import { useAppData } from "../lib/app-data";

export const Route = createFileRoute("/library/")({
  component: LibraryPage,
});

function LibraryPage() {
  const { playlists, refreshPlaylists } = useAppData();

  useEffect(() => {
    refreshPlaylists();
  }, []);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold">Mi Biblioteca</h1>
        <p className="text-sm text-muted-foreground mt-1 font-mono">
          {playlists.length} playlists
        </p>
      </header>

      <PlaylistGrid playlists={playlists} onCreated={refreshPlaylists} onChanged={refreshPlaylists} />
    </div>
  );
}
