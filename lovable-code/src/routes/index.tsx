import { createFileRoute } from "@tanstack/react-router";
import { Greeting } from "../components/home/Greeting";
import { QuickAccessSection } from "../components/home/QuickAccessSection";
import { RecentSongsSection } from "../components/home/RecentSongsSection";
import { useAppData } from "../lib/app-data";

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  const { playlists, recentSongs } = useAppData();

  return (
    <div className="space-y-10">
      <Greeting />
      <QuickAccessSection playlists={playlists} />
      <RecentSongsSection songs={recentSongs} />
    </div>
  );
}
