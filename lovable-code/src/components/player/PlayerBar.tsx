import { useState, useEffect, useRef, useCallback } from "react";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Shuffle,
  Repeat,
  Repeat1,
  Volume2,
  VolumeX,
} from "lucide-react";
import { bridge, type NowPlayingData } from "../../lib/bridge";
import { useAppData } from "../../lib/app-data";
import { Slider } from "../ui/slider";

type NowPlayingInfo = NowPlayingData;

export function PlayerBar() {
  const { setCurrentPlayingId, currentPlayingId, playerRefreshTrigger } = useAppData();
  const [np, setNp] = useState<NowPlayingInfo | null>(null);
  const [position, setPosition] = useState(0);
  const [volume, setVolume] = useState(0);
  const [muted, setMuted] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [shuffle, setShuffle] = useState(false);
  const [repeat, setRepeat] = useState("none");
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const posPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const barRef = useRef<HTMLDivElement | null>(null);
  const isDraggingRef = useRef(false);
  const justSkippedRef = useRef(false);
  const npRef = useRef<NowPlayingInfo | null>(null);

  const dur = np?.duration || 1;

  const getPosFromClientX = useCallback(
    (clientX: number) => {
      const rect = barRef.current?.getBoundingClientRect();
      if (!rect) return -1;
      const frac = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
      return frac * dur;
    },
    [dur],
  );

  const startPolling = useCallback(() => {
    const poll = async () => {
      const res = await bridge.getNowPlaying();
      if (res.debug) {
        console.log("[PlayerBar] POLL DEBUG:", JSON.stringify(res.debug));
      }
      if (res.ok && res.data) {
        const data = res.data as NowPlayingInfo;
        setNp((prev) => {
          if (prev?.id !== data.id) {
            setPosition(data.position);
          }
          return data;
        });
        setShuffle(data.shuffle);
        setRepeat(data.repeat);
        setCurrentPlayingId(data.id);
      }
    };
    poll();
    if (pollingRef.current) clearInterval(pollingRef.current);
    pollingRef.current = setInterval(poll, 1500);
  }, []);

  useEffect(() => {
    bridge.getVolume().then((res) => {
      if (res.ok && res.data !== undefined) {
        setVolume(res.data.volume);
      }
    });
  }, []);

  useEffect(() => {
    startPolling();

    const pollPos = async () => {
      if (isDraggingRef.current) return;
      const res = await bridge.getPlaybackPosition();
      setPosition(res.position);
      const prevNp = npRef.current;
      if (prevNp && prevNp.is_playing && !res.is_playing && !justSkippedRef.current) {
        const dur = prevNp.duration;
        if (dur > 0 && res.position >= dur - 1) {
          const nr = await bridge.nextSong();
          if (nr.ok && nr.data?.now_playing) {
            updateNowPlaying(nr.data.now_playing);
          } else {
            await new Promise(r => setTimeout(r, 100));
            refreshNowPlaying();
          }
        }
      }
    };
    pollPos();
    posPollRef.current = setInterval(pollPos, 200);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
      if (posPollRef.current) clearInterval(posPollRef.current);
    };
  }, [startPolling]);

  useEffect(() => {
    isDraggingRef.current = isDragging;
  }, [isDragging]);

  useEffect(() => {
    npRef.current = np;
  }, [np]);

  useEffect(() => {
    if (!isDragging) return;
    const handleMove = (e: MouseEvent) => {
      const pos = getPosFromClientX(e.clientX);
      if (pos >= 0) setPosition(pos);
    };
    const handleUp = (e: MouseEvent) => {
      setIsDragging(false);
      const pos = getPosFromClientX(e.clientX);
      if (pos >= 0) {
        setPosition(pos);
        bridge.seekSong(pos);
      }
    };
    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup", handleUp);
    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseup", handleUp);
    };
  }, [isDragging, getPosFromClientX]);

  const updateNowPlaying = useCallback((data: NowPlayingInfo) => {
    setNp((prev) => {
      if (prev?.id !== data.id) {
        setPosition(data.position);
      }
      return data;
    });
    setShuffle(data.shuffle);
    setRepeat(data.repeat);
    setCurrentPlayingId(data.id);
  }, [setCurrentPlayingId]);

  const refreshNowPlaying = useCallback(async (retries = 0): Promise<boolean> => {
    const res = await bridge.getNowPlaying();
    if (res.debug) {
      console.log("[PlayerBar] DEBUG backend state:", JSON.stringify(res.debug));
    }
    console.log("[PlayerBar] getNowPlaying response:", JSON.stringify(res));
    if (res.ok && res.data) {
      const data = res.data as NowPlayingInfo;
      if (npRef.current && data.id === npRef.current.id && retries < 3) {
        console.log("[PlayerBar] same song id, retrying...");
        await new Promise(r => setTimeout(r, 500));
        return refreshNowPlaying(retries + 1);
      }
      updateNowPlaying(data);
      return true;
    }
    if (retries < 3) {
      const delays = [300, 800, 2000];
      await new Promise(r => setTimeout(r, delays[retries]));
      return refreshNowPlaying(retries + 1);
    }
    console.log("[PlayerBar] refreshNowPlaying failed after retries, keeping current np");
    return false;
  }, [updateNowPlaying]);

  useEffect(() => {
    refreshNowPlaying();
  }, [currentPlayingId, playerRefreshTrigger, refreshNowPlaying]);

  const handlePlayPause = async () => {
    if (np?.is_playing) {
      await bridge.pauseSong();
    } else if (np) {
      await bridge.resumeSong();
    } else {
      const songs = await bridge.getSongs();
      if (songs.length) {
        await bridge.playSong(
          songs[0].id,
          songs.map((s) => s.id),
        );
      }
    }
    await new Promise(r => setTimeout(r, 100));
    await refreshNowPlaying();
  };

  const handlePrev = async () => {
    justSkippedRef.current = true;
    setTimeout(() => {
      justSkippedRef.current = false;
    }, 500);
    const res = await bridge.prevSong();
    console.log("[PlayerBar] prevSong response:", JSON.stringify(res));
    if (res.ok && res.data?.now_playing) {
      updateNowPlaying(res.data.now_playing);
    } else {
      await new Promise(r => setTimeout(r, 100));
      await refreshNowPlaying();
    }
  };
  const handleNext = async () => {
    justSkippedRef.current = true;
    setTimeout(() => {
      justSkippedRef.current = false;
    }, 500);
    const res = await bridge.nextSong();
    console.log("[PlayerBar] nextSong response:", JSON.stringify(res));
    if (res.ok && res.data?.now_playing) {
      updateNowPlaying(res.data.now_playing);
    } else {
      await new Promise(r => setTimeout(r, 100));
      await refreshNowPlaying();
    }
  };

  const handleShuffle = async () => {
    const res = await bridge.toggleShuffle();
    if (res.ok && res.data) setShuffle(res.data.shuffle);
  };

  const handleRepeat = async () => {
    const res = await bridge.cycleRepeat();
    if (res.ok && res.data) setRepeat(res.data.repeat);
  };

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

  const handleBarMouseDown = (e: React.MouseEvent) => {
    if (!np) return;
    setIsDragging(true);
    const pos = getPosFromClientX(e.clientX);
    if (pos >= 0) setPosition(pos);
    e.preventDefault();
  };

  const fmt = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  const hasSong = !!np;
  const displayPosition = Math.min(position, dur);
  const progress = np ? Math.min(displayPosition / dur, 1) : 0;
  const showTransition = !isDragging;

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-50 glass border-t border-border/40 px-4 py-2 flex items-center gap-4 transition-transform duration-500 ease-out ${currentPlayingId ? "translate-y-0" : "translate-y-full"}`}
    >
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
          <button
            onClick={handlePrev}
            className="text-muted-foreground hover:text-foreground transition p-1"
            aria-label="Anterior"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={handleShuffle}
            className={`transition p-1.5 rounded ${shuffle ? "text-primary" : "text-muted-foreground hover:text-foreground"}`}
            aria-label="Aleatorio"
          >
            <Shuffle className="w-4 h-4" />
          </button>
          <button
            onClick={handlePlayPause}
            className="w-9 h-9 rounded-full bg-primary text-primary-foreground grid place-items-center hover:scale-105 transition"
            aria-label={np?.is_playing ? "Pausar" : "Reproducir"}
          >
            {np?.is_playing ? (
              <Pause className="w-4 h-4 fill-current" />
            ) : (
              <Play className="w-4 h-4 fill-current ml-0.5" />
            )}
          </button>
          <button
            onClick={handleRepeat}
            className={`transition p-1.5 rounded ${repeat !== "none" ? "text-primary" : "text-muted-foreground hover:text-foreground"}`}
            aria-label="Repetir"
          >
            {repeat === "one" ? <Repeat1 className="w-4 h-4" /> : <Repeat className="w-4 h-4" />}
          </button>
          <button
            onClick={handleNext}
            className="text-muted-foreground hover:text-foreground transition p-1"
            aria-label="Siguiente"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center gap-2 w-full">
          <span className="text-xs font-mono text-muted-foreground w-8 text-right tabular-nums">
            {fmt(displayPosition)}
          </span>
          <div
            ref={barRef}
            className="flex-1 relative group cursor-pointer"
            onMouseDown={handleBarMouseDown}
          >
            <div
              className={`h-1.5 rounded-full bg-muted/40 overflow-hidden ${showTransition ? "transition-all duration-75" : ""}`}
            >
              <div
                className={`h-full bg-primary rounded-full ${showTransition ? "transition-all duration-75" : ""}`}
                style={{ width: `${progress * 100}%` }}
              />
            </div>
            <div
              className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
              style={{ left: `calc(${progress * 100}% - 6px)` }}
            />
          </div>
          <span className="text-xs font-mono text-muted-foreground w-8 tabular-nums">
            {fmt(dur)}
          </span>
        </div>
      </div>

      {/* Right: volume */}
      <div className="flex items-center gap-2 w-40 shrink-0 justify-end">
        <button
          onClick={toggleMute}
          className="text-muted-foreground hover:text-foreground transition p-1"
          aria-label="Silenciar"
        >
          {muted || volume === 0 ? (
            <VolumeX className="w-4 h-4" />
          ) : (
            <Volume2 className="w-4 h-4" />
          )}
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
