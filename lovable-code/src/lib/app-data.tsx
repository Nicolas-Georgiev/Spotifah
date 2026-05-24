import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from "react";
import { bridge, type Playlist, type Song } from "./bridge";
import { SplashScreen } from "../components/shared/SplashScreen";

interface AppData {
  playlists: Playlist[];
  songs: Song[];
  recentSongs: Song[];
  loading: boolean;
  error: string | null;
  currentPlayingId: string | null;
  setCurrentPlayingId: (id: string | null) => void;
  playerRefreshTrigger: number;
  triggerPlayerRefresh: () => void;
  refreshPlaylists: () => Promise<void>;
  refreshSongs: () => Promise<void>;
  refreshRecentSongs: () => Promise<void>;
}

const AppDataContext = createContext<AppData | null>(null);

export function useAppData() {
  const ctx = useContext(AppDataContext);
  if (!ctx) throw new Error("useAppData must be used within AppDataProvider");
  return ctx;
}

interface Props {
  children: ReactNode;
}

const MIN_SPLASH_MS = 1000;
const LOAD_RETRIES = 2;

export function AppDataProvider({ children }: Props) {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [songs, setSongs] = useState<Song[]>([]);
  const [recentSongs, setRecentSongs] = useState<Song[]>([]);
  const [currentPlayingId, setCurrentPlayingId] = useState<string | null>(null);
  const [playerRefreshTrigger, setPlayerRefreshTrigger] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadKey, setLoadKey] = useState(0);

  const refreshPlaylists = useCallback(async () => {
    const p = await bridge.getPlaylists();
    setPlaylists(p);
  }, []);

  const refreshSongs = useCallback(async () => {
    const s = await bridge.getSongs();
    setSongs(s);
  }, []);

  const refreshRecentSongs = useCallback(async () => {
    const r = await bridge.getRecentlyPlayed(4);
    setRecentSongs(r);
  }, []);

  const triggerPlayerRefresh = useCallback(() => {
    setPlayerRefreshTrigger((n) => n + 1);
  }, []);

  const handleRetry = useCallback(() => {
    setLoadKey((k) => k + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    let retries = 0;

    async function attempt(): Promise<void> {
      while (!cancelled && retries <= LOAD_RETRIES) {
        try {
          setLoading(true);
          setError(null);
          const startedAt = Date.now();
          const [p, s, r] = await Promise.all([
            bridge.getPlaylists(),
            bridge.getSongs(),
            bridge.getRecentlyPlayed(4),
          ]);
          if (cancelled) return;

          const hasRealPlaylists = p.length > 1;

          if (!hasRealPlaylists && retries < LOAD_RETRIES) {
            retries++;
            if (!cancelled) await new Promise((r2) => setTimeout(r2, 500));
            continue;
          }

          setPlaylists(p);
          setSongs(s);
          setRecentSongs(r);

          const elapsed = Date.now() - startedAt;
          const remaining = MIN_SPLASH_MS - elapsed;
          if (remaining > 0) {
            await new Promise((r2) => setTimeout(r2, remaining));
          }
          if (cancelled) return;
          setLoading(false);

          if (!hasRealPlaylists) {
            setTimeout(() => {
              refreshPlaylists();
            }, 2000);
          }
          return;
        } catch (err: any) {
          retries++;
          if (retries <= LOAD_RETRIES && !cancelled) {
            await new Promise((r2) => setTimeout(r2, 500));
          } else if (!cancelled) {
            setError(err?.message ?? "Error al cargar datos");
            setLoading(false);
            return;
          }
        }
      }

      if (!cancelled) {
        setLoading(false);
      }
    }

    attempt();

    return () => { cancelled = true; };
  }, [loadKey, refreshPlaylists]);

  if (loading || error) {
    return <SplashScreen error={error} onRetry={error ? handleRetry : undefined} />;
  }

  return (
      <AppDataContext.Provider
        value={{
          playlists,
          songs,
          recentSongs,
          currentPlayingId,
          setCurrentPlayingId,
          playerRefreshTrigger,
          triggerPlayerRefresh,
          loading,
          error,
          refreshPlaylists,
          refreshSongs,
          refreshRecentSongs,
        }}
      >
      {children}
    </AppDataContext.Provider>
  );
}
