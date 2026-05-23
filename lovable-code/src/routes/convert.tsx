import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { bridge } from "../lib/bridge";
import { ConversionInput } from "../components/convert/ConversionInput";
import { ConversionList } from "../components/convert/ConversionList";

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
      } else if (platform === "soundcloud") {
        result = await bridge.convertSoundcloud(entryUrl);
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

      <ConversionInput
        url={url}
        onUrlChange={setUrl}
        onConvert={convert}
        busy={busy}
      />

      <ConversionList items={items} />
    </div>
  );
}
