import { useState, useEffect, useRef, useCallback } from "react";
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX } from "lucide-react";
import { bridge } from "../../lib/bridge";
import { Slider } from "../ui/slider";

interface NowPlayingInfo {
  id: string;
  title: string;
  artist: string;
  duration: number;
  cover_url: string;
  is_playing: boolean;
  position: number;
}

export function PlayerBar() {
  const [np, setNp] = useState<NowPlayingInfo | null>(null);
  const [position, setPosition] = useState(0);
  const [volume, setVolume] = useState(80);
  const [muted, setMuted] = useState(false);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startPolling = useCallback(() => {
    const poll = async () => {
      const res = await bridge.getNowPlaying();
      if (res.ok && res.data) {
        const data = res.data as NowPlayingInfo;
        setNp(prev => {
          if (prev?.id !== data.id) {
            setPosition(data.position);
          }
          return data;
        });
      } else {
        setNp(null);
      }
    };
    poll();
    if (pollingRef.current) clearInterval(pollingRef.current);
    pollingRef.current = setInterval(poll, 2000);
  }, []);

  useEffect(() => {
    bridge.getVolume().then((r) => { if (r.ok && r.data) setVolume(r.data.volume); });
    startPolling();
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [startPolling]);

  useEffect(() => {
    if (!np?.is_playing) return;
    const interval = setInterval(() => {
      setPosition(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [np?.is_playing, np?.id]);

  const refreshNowPlaying = useCallback(async () => {
    const res = await bridge.getNowPlaying();
    if (res.ok && res.data) {
      const data = res.data as NowPlayingInfo;
      setNp(prev => {
        if (prev?.id !== data.id) {
          setPosition(data.position);
        }
        return data;
      });
    } else {
      setNp(null);
    }
  }, []);

  const handlePlayPause = async () => {
    if (np?.is_playing) {
      await bridge.pauseSong();
    } else if (np) {
      await bridge.resumeSong();
    } else {
      const songs = await bridge.getSongs();
      if (songs.length) await bridge.playSong(songs[0].id);
    }
    await refreshNowPlaying();
  };

  const handlePrev = async () => { await bridge.prevSong(); await refreshNowPlaying(); };
  const handleNext = async () => { await bridge.nextSong(); await refreshNowPlaying(); };

  const handleVolume = async (v: number[]) => {
    const val = v[0];
    setVolume(val);
    await bridge.setVolume(val);
    if (val === 0) setMuted(true);
    else setMuted(false);
  };

  const toggleMute = async () => {
    if (muted) {
      setMuted(false);
      const v = volume || 80;
      await bridge.setVolume(v);
    } else {
      setMuted(true);
      await bridge.setVolume(0);
    }
  };

  const fmt = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  const hasSong = !!np;
  const dur = np?.duration || 1;
  const progress = Math.min(position / dur, 1);

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 glass border-t border-border/40 px-4 py-2 flex items-center gap-4">
      {/* Left: cover + info */}
      <div className="flex items-center gap-3 w-64 shrink-0">
        <div className="w-12 h-12 rounded-lg bg-muted/40 flex items-center justify-center text-lg shrink-0 overflow-hidden">
          {hasSong && np.cover_url ? (
            <img src={np.cover_url} alt="" className="w-full h-full object-cover" />
          ) : (
            <span>♪</span>
          )}
        </div>
        <div className="min-w-0">
          <p className="text-sm font-medium truncate">{hasSong ? np.title : "Sin reproducción"}</p>
          <p className="text-xs text-muted-foreground truncate">{hasSong ? np.artist : "—"}</p>
        </div>
      </div>

      {/* Center: controls + progress */}
      <div className="flex-1 flex flex-col items-center gap-1 max-w-2xl mx-auto">
        <div className="flex items-center gap-3">
          <button onClick={handlePrev} className="text-muted-foreground hover:text-foreground transition p-1" aria-label="Anterior">
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={handlePlayPause}
            className="w-9 h-9 rounded-full bg-primary text-primary-foreground grid place-items-center hover:scale-105 transition"
            aria-label={np?.is_playing ? "Pausar" : "Reproducir"}
          >
            {np?.is_playing ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
          </button>
          <button onClick={handleNext} className="text-muted-foreground hover:text-foreground transition p-1" aria-label="Siguiente">
            <SkipForward className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center gap-2 w-full">
          <span className="text-xs font-mono text-muted-foreground w-8 text-right tabular-nums">{fmt(Math.floor(position))}</span>
          <div className="flex-1 relative">
            <div className="h-1 rounded-full bg-muted/40 overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${progress * 100}%` }}
              />
            </div>
          </div>
          <span className="text-xs font-mono text-muted-foreground w-8 tabular-nums">{fmt(dur)}</span>
        </div>
      </div>

      {/* Right: volume */}
      <div className="flex items-center gap-2 w-40 shrink-0 justify-end">
        <button onClick={toggleMute} className="text-muted-foreground hover:text-foreground transition p-1" aria-label="Silenciar">
          {muted || volume === 0 ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
        </button>
        <Slider
          value={[muted ? 0 : volume]}
          onValueChange={handleVolume}
          max={100}
          step={1}
          className="w-24"
        />
      </div>
    </div>
  );
}
