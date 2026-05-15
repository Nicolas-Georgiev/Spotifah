import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Sparkles, Music2, Check, X } from "lucide-react";
import { bridge } from "../lib/bridge";

export const Route = createFileRoute("/status")({
  component: StatusPage,
});

interface SystemStatus {
  dependencies: Record<string, boolean>;
  ffmpeg: boolean;
  music_count: number;
}

const DEP_NAMES: Record<string, string> = {
  spotdl: "SpotDL",
  yt_dlp: "yt-dlp",
  moviepy: "MoviePy",
  mutagen: "Mutagen",
  requests: "Requests",
  pytubefix: "PyTubefix",
  pygame: "PyGame",
};

function StatusPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    bridge.getSystemStatus().then(setStatus);
  }, []);

  if (!status) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-muted-foreground">Cargando estado del sistema...</p>
      </div>
    );
  }

  const depEntries = Object.entries(DEP_NAMES);
  const okCount = depEntries.filter(([k]) => status.dependencies[k]).length;

  return (
    <div className="space-y-8">
      <header className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-accent grid place-items-center glow-violet">
          <Sparkles className="w-7 h-7 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold">Estado del Sistema</h1>
          <p className="text-sm text-muted-foreground mt-1">Verifica las dependencias y recursos de EKHO</p>
        </div>
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass rounded-2xl p-5">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Music2 className="w-4 h-4" />
            <span>Biblioteca</span>
          </div>
          <p className="text-3xl font-semibold mt-4">{status.music_count}</p>
          <p className="text-xs text-muted-foreground mt-3">canciones en tu biblioteca</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Check className="w-4 h-4" />
            <span>Dependencias</span>
          </div>
          <p className="text-3xl font-semibold mt-4">{okCount}/{depEntries.length}</p>
          <p className="text-xs text-muted-foreground mt-3">librerias instaladas</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Sparkles className="w-4 h-4" />
            <span>FFmpeg</span>
          </div>
          <p className="text-3xl font-semibold mt-4">{status.ffmpeg ? "Si" : "No"}</p>
          <p className="text-xs text-muted-foreground mt-3">motor de conversion de audio</p>
        </div>
      </div>

      <section className="glass rounded-2xl p-6">
        <h2 className="text-base font-semibold mb-5">Dependencias del Sistema</h2>
        <div className="space-y-3">
          {depEntries.map(([key, label]) => {
            const ok = status.dependencies[key];
            return (
              <div key={key} className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
                <span className="text-sm font-mono">{label}</span>
                {ok ? (
                  <span className="inline-flex items-center gap-1 text-xs text-green-400">
                    <Check className="w-3.5 h-3.5" /> Instalado
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs text-red-400">
                    <X className="w-3.5 h-3.5" /> No instalado
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <section className="glass rounded-2xl p-6">
        <h2 className="text-base font-semibold mb-5">Componentes del Sistema</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
            <span className="text-sm font-mono">FFmpeg</span>
            {status.ffmpeg ? (
              <span className="inline-flex items-center gap-1 text-xs text-green-400">
                <Check className="w-3.5 h-3.5" /> Disponible
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-xs text-red-400">
                <X className="w-3.5 h-3.5" /> No encontrado en PATH
              </span>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
