import { useState, useRef, useEffect, useCallback } from "react";
import { Search } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { bridge, type Song } from "../../lib/bridge";
import { useAppData } from "../../lib/app-data";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Song[]>([]);
  const [focused, setFocused] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const doSearch = useCallback(async (q: string) => {
    if (q.trim().length < 2) {
      setResults([]);
      return;
    }
    const res = await bridge.searchSongs(q.trim());
    setResults(res);
  }, []);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => doSearch(query), 300);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [query, doSearch]);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setFocused(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const { setCurrentPlayingId, triggerPlayerRefresh } = useAppData();
  const navigate = useNavigate();

  const handleSelectSong = useCallback(async (song: Song) => {
    await bridge.playSong(song.id);
    setCurrentPlayingId(song.id);
    triggerPlayerRefresh();
    navigate({ to: "/library/$playlistId", params: { playlistId: "all" } });
    setFocused(false);
    setQuery("");
  }, [setCurrentPlayingId, triggerPlayerRefresh, navigate]);

  const showDropdown = focused && query.trim().length >= 2;

  return (
    <div ref={ref} className="flex-1 max-w-xl mx-auto relative hidden md:block">
      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setFocused(true)}
        placeholder="Buscar canciones, artistas, álbumes..."
        className="w-full bg-input/60 border border-border rounded-full pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      />
      {showDropdown && (
        <div className="absolute top-full mt-2 left-0 right-0 bg-background/95 backdrop-blur border border-border rounded-xl shadow-2xl overflow-hidden z-50 max-h-80 overflow-y-auto">
          {results.length === 0 ? (
            <p className="px-4 py-6 text-sm text-muted-foreground text-center">Sin resultados</p>
          ) : (
            results.map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => handleSelectSong(s)}
                className="flex items-center gap-3 px-4 py-2.5 hover:bg-muted/30 transition w-full text-left"
              >
                <div className="w-9 h-9 rounded bg-muted/40 flex items-center justify-center text-sm shrink-0 overflow-hidden">
                  {s.cover_url ? (
                    <img src={s.cover_url} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <span>♪</span>
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate">{s.title}</p>
                  <p className="text-xs text-muted-foreground truncate">{s.artist}</p>
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
