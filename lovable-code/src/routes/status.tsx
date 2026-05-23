import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Sparkles, Music2, Check } from "lucide-react";
import { bridge } from "../lib/bridge";
import { LoadingMessage } from "../components/shared/LoadingMessage";
import { StatCard } from "../components/status/StatCard";
import { DependencyRow } from "../components/status/DependencyRow";
import { GlassCard } from "../components/shared/GlassCard";

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
    return <LoadingMessage message="Cargando estado del sistema..." />;
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
        <StatCard
          icon={<Music2 className="w-4 h-4" />}
          label="Biblioteca"
          value={status.music_count}
          description="canciones en tu biblioteca"
        />
        <StatCard
          icon={<Check className="w-4 h-4" />}
          label="Dependencias"
          value={`${okCount}/${depEntries.length}`}
          description="librerias instaladas"
        />
        <StatCard
          icon={<Sparkles className="w-4 h-4" />}
          label="FFmpeg"
          value={status.ffmpeg ? "Si" : "No"}
          description="motor de conversion de audio"
        />
      </div>

      <GlassCard>
        <h2 className="text-base font-semibold mb-5">Dependencias del Sistema</h2>
        <div className="space-y-3">
          {depEntries.map(([key, label]) => (
            <DependencyRow key={key} label={label} ok={!!status.dependencies[key]} />
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
