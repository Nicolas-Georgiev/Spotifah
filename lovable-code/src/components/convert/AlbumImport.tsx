import { useState, useCallback, useRef, useEffect } from "react";
import {
  Music, ListMusic, ExternalLink, Clock, Album, Link2,
  ChevronDown, ChevronUp, Search,
} from "lucide-react";
import { bridge, type AlbumPreviewData, type TrackPreview } from "../../lib/bridge";
import { useConvertData } from "../../lib/convert-data";
import { PlaylistImport } from "./PlaylistImport";
import { PlatformBadges } from "./PlatformBadges";

const PLATFORM_LABELS: Record<string, string> = {
  spotify: "Spotify",
  youtube: "YouTube",
  soundcloud: "SoundCloud",
};

const PLATFORM_COLORS: Record<string, string> = {
  spotify: "border-l-green-500",
  youtube: "border-l-red-500",
  soundcloud: "border-l-orange-500",
};

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function TrackRow({ track, index }: { track: TrackPreview; index: number }) {
  return (
    <div className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-muted/30 transition text-sm">
      <span className="w-6 text-right text-muted-foreground text-sm font-mono">
        {index}
      </span>
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{track.title}</p>
        <p className="text-xs text-muted-foreground truncate">{track.artist}</p>
      </div>
      <span className="text-sm text-muted-foreground font-mono shrink-0">
        {formatDuration(track.duration)}
      </span>
    </div>
  );
}

interface Props {
  onNavigateToPlaylist?: (playlistId: string) => void;
}

export function AlbumImport({ onNavigateToPlaylist }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<AlbumPreviewData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAllTracks, setShowAllTracks] = useState(false);
  const {
    activeImportTaskId: importTaskId,
    completedPlaylistId,
    setActiveImportTaskId: setImportTaskId,
    setCompletedPlaylistId,
  } = useConvertData();
  const coverRef = useRef<string | null>(null);
  const [coverError, setCoverError] = useState(false);

  const cleanupCover = useCallback((coverUrl: string | null | undefined) => {
    if (coverUrl && coverUrl.startsWith("/api/covers/")) {
      bridge.deletePreviewCover(coverUrl);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (coverRef.current) {
        cleanupCover(coverRef.current);
      }
    };
  }, [cleanupCover]);

  const analyze = useCallback(async () => {
    const trimmed = url.trim();
    if (!trimmed) return;
    if (coverRef.current) {
      cleanupCover(coverRef.current);
      coverRef.current = null;
    }
    setLoading(true);
    setError(null);
    setPreview(null);
    setCoverError(false);
    setImportTaskId(null);
    setCompletedPlaylistId(null);
    try {
      const res = await bridge.getAlbumPreview(trimmed);
      if (res.ok && res.data) {
        setPreview(res.data);
        if (res.data.cover_url && res.data.cover_url.startsWith("/api/covers/")) {
          coverRef.current = res.data.cover_url;
        }
      } else {
        setError(res.error || "No se pudo obtener la vista previa");
      }
    } catch (e: any) {
      setError(e?.message || "Error al analizar la URL");
    } finally {
      setLoading(false);
    }
  }, [url, cleanupCover]);

  const handleImport = useCallback(async () => {
    if (!preview) return;
    if (coverRef.current) {
      cleanupCover(coverRef.current);
      coverRef.current = null;
    }
    setImportTaskId(null);
    setCompletedPlaylistId(null);
    const res = await bridge.importAlbum(url.trim());
    if (res.ok && res.data) {
      setImportTaskId(res.data.task_id);
    } else {
      setError(res.error || "Error al importar el álbum");
    }
  }, [url, preview]);

  const handleImportComplete = useCallback((playlistId: number) => {
    setCompletedPlaylistId(playlistId);
  }, []);

  const displayedTracks = showAllTracks
    ? (preview?.tracks ?? [])
    : (preview?.tracks ?? []).slice(0, 10);

  const hasMore = (preview?.tracks.length ?? 0) > 10;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <ListMusic className="w-5 h-5 text-muted-foreground" />
        <h2 className="text-xl font-semibold">Importar álbum o playlist</h2>
      </div>

<<<<<<< HEAD
      <div className="glass rounded-2xl p-5">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Link2 className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              value={url}
              onChange={(e) => { setUrl(e.target.value); setPreview(null); setError(null); setImportTaskId(null); setCompletedPlaylistId(null); }}
              onKeyDown={(e) => { if (e.key === "Enter") analyze(); }}
              placeholder="https://open.spotify.com/album/..."
              className="w-full bg-input/60 border border-border rounded-lg pl-11 pr-4 py-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button
            onClick={analyze}
            disabled={loading || !url.trim()}
            className="px-5 py-3 rounded-lg font-medium bg-primary text-primary-foreground hover:opacity-90 glow-violet flex items-center gap-2 justify-center disabled:opacity-50"
          >
            {loading ? (
              <span className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            {loading ? "Analizando..." : "Analizar"}
          </button>
        </div>
=======
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          value={url}
          onChange={(e) => { setUrl(e.target.value); setPreview(null); setError(null); setCoverError(false); setImportTaskId(null); setCompletedPlaylistId(null); if (coverRef.current) { cleanupCover(coverRef.current); coverRef.current = null; } }}
          onKeyDown={(e) => { if (e.key === "Enter") analyze(); }}
          placeholder="https://open.spotify.com/album/..."
          className="flex-1 bg-input/60 border border-border rounded-lg px-4 py-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button
          onClick={analyze}
          disabled={loading || !url.trim()}
          className="px-5 py-3 rounded-lg font-medium bg-primary text-primary-foreground hover:opacity-90 glow-violet flex items-center gap-2 justify-center disabled:opacity-50"
        >
          {loading ? (
            <span className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          {loading ? "Analizando..." : "Analizar"}
        </button>
>>>>>>> e3624042cf0c93c4c4d6911294adee46c25f269e
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-sm text-destructive">
          {error}
        </div>
      )}

      {preview && !importTaskId && !completedPlaylistId && (
        <div className={`glass rounded-2xl overflow-hidden border-l-4 ${PLATFORM_COLORS[preview.platform] || "border-l-primary"}`}>
          <div className="flex flex-col md:flex-row">
            <div className="md:w-64 shrink-0">
              <div className="aspect-square bg-muted/40 relative">
                {preview.cover_url && !coverError ? (
                  <img
                    src={preview.cover_url}
                    alt={preview.name}
                    className="w-full h-full object-cover"
                    onError={() => setCoverError(true)}
                  />
                ) : (
                  <div className="w-full h-full grid place-items-center">
                    <Music className="w-16 h-16 text-muted-foreground/40" />
                  </div>
                )}
              </div>
            </div>
            <div className="flex-1 p-6 flex flex-col justify-between">
              <div className="space-y-3">
                <div>
                  <PlatformBadges platform={preview.platform} />
                </div>
                <h3 className="text-2xl font-bold">{preview.name}</h3>
                {preview.year && (
                  <p className="text-muted-foreground text-sm">{preview.year}</p>
                )}
                <p className="text-sm text-muted-foreground flex items-center gap-2">
                  <ListMusic className="w-4 h-4" />
                  {preview.total_tracks} canciones
                </p>
              </div>
              <button
                onClick={handleImport}
                className="mt-6 px-6 py-3 rounded-lg font-medium bg-primary text-primary-foreground hover:opacity-90 glow-violet inline-flex items-center gap-2 justify-center text-sm w-full sm:w-auto"
              >
                <ListMusic className="w-4 h-4" />
                Importar como Playlist
              </button>
            </div>
          </div>

          <div className="border-t border-border/50">
            <div className="px-3 py-2 flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="w-4 h-4" />
              Lista de canciones
              <span className="text-xs ml-auto">{preview.tracks.length} temas</span>
            </div>
            <div className="max-h-80 overflow-y-auto pb-2">
              {displayedTracks.map((track, i) => (
                <TrackRow key={i} track={track} index={i + 1} />
              ))}
              {hasMore && !showAllTracks && (
                <button
                  onClick={() => setShowAllTracks(true)}
                  className="flex items-center gap-2 py-2 px-3 text-xs text-primary hover:text-primary/80 transition"
                >
                  <ChevronDown className="w-3 h-3" />
                  Mostrar las {preview.tracks.length - 10} restantes
                </button>
              )}
              {showAllTracks && hasMore && (
                <button
                  onClick={() => setShowAllTracks(false)}
                  className="flex items-center gap-2 py-2 px-3 text-xs text-muted-foreground hover:text-foreground transition"
                >
                  <ChevronUp className="w-3 h-3" />
                  Mostrar menos
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {importTaskId && (
        <section>
          <h3 className="text-lg font-semibold mb-3">Importando álbum...</h3>
          <PlaylistImport
            taskId={importTaskId}
            onComplete={handleImportComplete}
          />
        </section>
      )}

      {completedPlaylistId && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-green-500/10 border border-green-500/20">
          <ListMusic className="w-5 h-5 text-green-400 shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-green-400">Álbum importado correctamente</p>
          </div>
          {onNavigateToPlaylist && (
            <button
              onClick={() => onNavigateToPlaylist(String(completedPlaylistId))}
              className="px-4 py-2 rounded-lg font-medium bg-green-600 text-white hover:opacity-90 inline-flex items-center gap-2 text-sm"
            >
              <ExternalLink className="w-4 h-4" />
              Ver playlist
            </button>
          )}
        </div>
      )}
    </div>
  );
}
