import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Link2, Download, Music2, Youtube, Cloud, Loader2, Check } from "lucide-react";
import { bridge } from "../lib/bridge";

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

interface ConvItem {
  id: number;
  title: string;
  platform: Exclude<Platform, null>;
  status: "processing" | "done" | "error";
  error?: string;
}

function ConvertPage() {
  const [url, setUrl] = useState("");
  const [items, setItems] = useState<ConvItem[]>([]);
  const [busy, setBusy] = useState(false);

  const convert = async () => {
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
      } else {
        throw new Error("Plataforma no soportada");
      }

      if (result.ok) {
        setItems((prev) =>
          prev.map((i) => (i.id === id ? { ...i, status: "done" as const } : i))
        );
      } else {
        setItems((prev) =>
          prev.map((i) =>
            i.id === id ? { ...i, status: "error" as const, error: result.error } : i
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

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold">Conversor de Enlaces</h1>
        <p className="text-sm text-muted-foreground mt-2">
          Convierte canciones de YouTube, Spotify y SoundCloud a MP3
        </p>
      </header>

      <div className="glass rounded-2xl p-5">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Link2 className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && convert()}
              placeholder="Pega aqui el enlace de YouTube, Spotify o SoundCloud..."
              className="w-full bg-input/60 border border-border rounded-lg pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button
            onClick={convert}
            disabled={!url.trim() || busy}
            className="px-6 py-3 rounded-lg font-medium bg-primary text-primary-foreground glow-violet hover:opacity-90 inline-flex items-center gap-2 justify-center disabled:opacity-50"
          >
            {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            Convertir
          </button>
        </div>
        <div className="flex items-center gap-3 mt-4 text-xs flex-wrap">
          <span className="text-muted-foreground">Plataformas soportadas:</span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/15 text-red-400 border border-red-500/30">
            <Youtube className="w-3 h-3" /> YouTube
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/15 text-green-400 border border-green-500/30">
            <Music2 className="w-3 h-3" /> Spotify
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-500/15 text-yellow-400 border border-yellow-500/30">
            <Cloud className="w-3 h-3" /> SoundCloud
          </span>
        </div>
      </div>

      <section>
        <h2 className="text-xl font-semibold mb-3">Conversiones Recientes</h2>
        <div className="glass rounded-2xl p-6 min-h-[220px]">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <div className="w-14 h-14 rounded-full bg-muted/40 grid place-items-center mb-4">
                <Download className="w-6 h-6 text-muted-foreground" />
              </div>
              <p className="text-muted-foreground">No hay conversiones todavia</p>
              <p className="text-xs text-muted-foreground/70 mt-2">Pega un enlace arriba para comenzar</p>
            </div>
          ) : (
            <ul className="space-y-2">
              {items.map((i) => (
                <li key={i.id} className="flex items-center gap-3 p-3 rounded-lg bg-muted/20">
                  <div className="w-9 h-9 rounded-md bg-primary/15 grid place-items-center">
                    {i.platform === "youtube" && <Youtube className="w-4 h-4 text-red-400" />}
                    {i.platform === "spotify" && <Music2 className="w-4 h-4 text-green-400" />}
                    {i.platform === "soundcloud" && <Cloud className="w-4 h-4 text-yellow-400" />}
                  </div>
                  <p className="flex-1 truncate text-sm font-mono">{i.title}</p>
                  {i.status === "processing" ? (
                    <span className="text-xs text-muted-foreground inline-flex items-center gap-1">
                      <Loader2 className="w-3 h-3 animate-spin" /> Procesando...
                    </span>
                  ) : i.status === "done" ? (
                    <span className="text-xs text-green-400 inline-flex items-center gap-1">
                      <Check className="w-3 h-3" /> Listo
                    </span>
                  ) : (
                    <span className="text-xs text-red-400" title={i.error}>
                      Error
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
