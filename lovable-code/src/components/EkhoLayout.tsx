import { Outlet } from "@tanstack/react-router";
import { AppHeader } from "./layout/AppHeader";
import { Footer } from "./layout/Footer";
import { PlayerBar } from "./player/PlayerBar";
import { useAppData } from "../lib/app-data";

export function EkhoLayout() {
  const { currentPlayingId } = useAppData();
  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />
      <main
        className={`flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 ${currentPlayingId ? "pb-28" : "pb-8"}`}
      >
        <Outlet />
      </main>
      <Footer />
      <PlayerBar />
    </div>
  );
}
