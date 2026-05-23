import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { bridge, type Playlist, type Song } from "../lib/bridge";
import { Greeting } from "../components/home/Greeting";
import { QuickAccessSection } from "../components/home/QuickAccessSection";
import { RecentSongsSection } from "../components/home/RecentSongsSection";

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [songs, setSongs] = useState<Song[]>([]);

  useEffect(() => {
    bridge.getPlaylists().then(setPlaylists);
    bridge.getSongs().then(setSongs);
  }, []);

  return (
    <div className="space-y-10">
      <Greeting />
      <QuickAccessSection playlists={playlists} />
      <RecentSongsSection songs={songs} />
    </div>
  );
}
