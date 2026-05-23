import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useCallback } from "react";
import { ListMusic, ExternalLink } from "lucide-react";
import { bridge } from "../lib/bridge";
import { ConversionInput } from "../components/convert/ConversionInput";
import { ConversionList } from "../components/convert/ConversionList";
import { PlaylistImport } from "../components/convert/PlaylistImport";
import type { ConvItem } from "../components/convert/ConversionItem";

export const Route = createFileRoute("/convert")({
  component: ConvertPage,
});

type Platform = "youtube" | "spotify" | "soundcloud" | null;

function detectPlatform(url: string): Platform {
  const u = url.toLowerCase();
  if (u.includes("youtube.com") || u.includes("youtu.be")) return "youtube";
  if (u.includes("spotify.com")) return "spotify";
  if (u.includes("soundcloud.com")) return "soundcloud";
  return null;
}

function ConvertPage() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [items, setItems] = useState<ConvItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [isPlaylistUrl, setIsPlaylistUrl] = useState(false);
  const [importTaskId, setImportTaskId] = useState<string | null>(null);
  const [completedPlaylistId, setCompletedPlaylistId] = useState<number | null>(null);
  const [checkingType, setCheckingType] = useState(false);

  const handleUrlChange = useCallback(async (newUrl: string) => {
    setUrl(newUrl);
    setCompletedPlaylistId(null);
    setImportTaskId(null);
    if (!newUrl.trim() || !detectPlatform(newUrl)) {
      setIsPlaylistUrl(false);
      return;
    }
    setCheckingType(true);
    try {
      const result = await bridge.detectUrlType(newUrl);
      setIsPlaylistUrl(result.is_playlist);
    } catch {
      setIsPlaylistUrl(false);
    } finally {
      setCheckingType(false);
    }
  }, []);

  const convert = async () => {
    const platform = detectPlatform(url);
    if (!platform || busy) return;

    if (isPlaylistUrl) {
      const res = await bridge.importPlaylist(url);
      if (res.ok && res.data) {
        setImportTaskId(res.data.task_id);
        setUrl("");
        setCompletedPlaylistId(null);
      }
      return;
    }

    setBusy(true);
    const id = Date.now();
    const entryUrl = url;
    setUrl("");
    setItems((prev) => [{ id, title: entryUrl, platform, status: "processing" }, ...prev]);

    try {
      let result;
      if (platform === "youtube") {
        result = await bridge.convertYoutube(entryUrl);
      } else if (platform === "spotify") {
        result = await bridge.convertSpotify(entryUrl);
      } else if (platform === "soundcloud") {
        result = await bridge.convertSoundcloud(entryUrl);
      } else {
        throw new Error("Plataforma no soportada");
      }

      if (result.ok) {
        setItems((prev) =>
          prev.map((i) =>
            i.id === id
              ? { ...i, status: "done" as const, log: result.data?.log ?? result.log }
              : i
          )
        );
      } else {
        setItems((prev) =>
          prev.map((i) =>
            i.id === id
              ? { ...i, status: "error" as const, error: result.error, log: (result as any).log ?? "" }
              : i
          )
        );
      }
    } catch (e: any) {
      setItems((prev) =>
        prev.map((i) =>
          i.id === id ? { ...i, status: "error" as const, error: e.message } : i
        )
      );
    } finally {
      setBusy(false);
    }
  };

  const handleImportComplete = useCallback((playlistId: number) => {
    setCompletedPlaylistId(playlistId);
  }, []);

  const goToPlaylist = () => {
    if (completedPlaylistId) {
      navigate({ to: "/library/$playlistId", params: { playlistId: String(completedPlaylistId) } });
    }
  };

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold">Conversor de Enlaces</h1>
        <p className="text-sm text-muted-foreground mt-2">
          Convierte canciones o importa playlists completas desde YouTube, Spotify y SoundCloud
        </p>
      </header>

      <ConversionInput
        url={url}
        onUrlChange={handleUrlChange}
        onConvert={convert}
        busy={busy || checkingType}
      />

      {isPlaylistUrl && !importTaskId && url.trim() && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-primary/10 border border-primary/20">
          <ListMusic className="w-5 h-5 text-primary shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">Playlist detectada</p>
            <p className="text-xs text-muted-foreground">
              Se importar\u00e1n todas las canciones de la playlist
            </p>
          </div>
          <button
            onClick={convert}
            disabled={busy}
            className="px-4 py-2 rounded-lg font-medium bg-primary text-primary-foreground glow-violet hover:opacity-90 inline-flex items-center gap-2 text-sm disabled:opacity-50"
          >
            <ListMusic className="w-4 h-4" />
            Importar Playlist
          </button>
        </div>
      )}

      {importTaskId && (
        <section>
          <h2 className="text-xl font-semibold mb-3">Importaci\u00f3n en curso</h2>
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
            <p className="text-sm font-medium text-green-400">Playlist importada correctamente</p>
          </div>
          <button
            onClick={goToPlaylist}
            className="px-4 py-2 rounded-lg font-medium bg-green-600 text-white hover:opacity-90 inline-flex items-center gap-2 text-sm"
          >
            <ExternalLink className="w-4 h-4" />
            Ver playlist
          </button>
        </div>
      )}

      <ConversionList items={items} />
    </div>
  );
}
