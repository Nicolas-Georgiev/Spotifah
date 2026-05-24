import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useCallback } from "react";
import { Music, ListMusic, ArrowRight } from "lucide-react";
import { bridge } from "../lib/bridge";
import { useConvertData } from "../lib/convert-data";
import { ConversionInput } from "../components/convert/ConversionInput";
import { ConversionList } from "../components/convert/ConversionList";
import { AlbumImport } from "../components/convert/AlbumImport";
import { LocalFileImport } from "../components/convert/LocalFileImport";

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
  const { items, setItems } = useConvertData();
  const [busy, setBusy] = useState(false);
  const [isPlaylistUrl, setIsPlaylistUrl] = useState(false);
  const [checkingType, setCheckingType] = useState(false);

  const handleUrlChange = useCallback(async (newUrl: string) => {
    setUrl(newUrl);
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

  const convertSingle = async () => {
    const platform = detectPlatform(url);
    if (!platform || busy) return;

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

  const handleNavigateToPlaylist = useCallback((playlistId: string) => {
    navigate({ to: "/library/$playlistId", params: { playlistId } });
  }, [navigate]);

  return (
    <div className="space-y-12">
      <header>
        <h1 className="text-4xl font-bold">Conversor</h1>
        <p className="text-sm text-muted-foreground mt-2">
          Importa álbumes completos como playlists o convierte canciones individuales
        </p>
      </header>

      <AlbumImport onNavigateToPlaylist={handleNavigateToPlaylist} />

      <hr className="border-border/50" />

      <section>
        <div className="flex items-center gap-3 mb-6">
          <Music className="w-5 h-5 text-muted-foreground" />
          <h2 className="text-xl font-semibold">Convertir Canción Individual</h2>
        </div>

        <ConversionInput
          url={url}
          onUrlChange={handleUrlChange}
          onConvert={convertSingle}
          busy={busy || checkingType}
        />

        {isPlaylistUrl && url.trim() && (
          <div className="flex items-center gap-3 p-4 rounded-lg bg-primary/10 border border-primary/20 mt-4">
            <ListMusic className="w-5 h-5 text-primary shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">¿Quieres importar un álbum o playlist?</p>
              <p className="text-xs text-muted-foreground">
                Usa la sección "Importar Álbum" de arriba para ver la vista previa e importar todas las canciones
              </p>
            </div>
            <ArrowRight className="w-5 h-5 text-primary/60 shrink-0" />
          </div>
        )}

        <div className="mt-8">
          <ConversionList items={items} />
        </div>
      </section>

      <hr className="border-border/50" />

      <LocalFileImport />
    </div>
  );
}
