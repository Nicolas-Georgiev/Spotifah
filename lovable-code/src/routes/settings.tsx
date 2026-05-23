import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Bell, Download, Music2, Info } from "lucide-react";
import { bridge } from "../lib/bridge";
import { LoadingMessage } from "../components/shared/LoadingMessage";
import { SettingCard } from "../components/settings/SettingCard";
import { Toggle } from "../components/settings/Toggle";
import { BitrateSelect } from "../components/settings/BitrateSelect";

export const Route = createFileRoute("/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    bridge.getSettings().then((s) => {
      setSettings(s);
      setLoaded(true);
    });
  }, []);

  const update = async (key: string, value: any) => {
    const next = { ...settings, [key]: value };
    setSettings(next);
    await bridge.updateSettings({ [key]: value });
  };

  if (!loaded) {
    return <LoadingMessage message="Cargando configuracion..." />;
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold">Configuracion</h1>
        <p className="text-sm text-muted-foreground mt-2">Personaliza tu experiencia en EKHO</p>
      </header>

      <SettingCard icon={<Download className="w-5 h-5" />} iconBg="bg-secondary/25 text-secondary" title="Calidad de Descarga" subtitle="Bitrate predeterminado para conversiones a MP3">
        <BitrateSelect value={settings.download_quality ?? "192"} onChange={(v) => update("download_quality", v)} />
      </SettingCard>

      <SettingCard icon={<Bell className="w-5 h-5" />} iconBg="bg-yellow-500/25 text-yellow-400" title="Notificaciones" subtitle="Recibe avisos cuando se completen las conversiones">
        <Toggle label="Notificaciones del sistema" value={settings.notifications ?? true} onChange={(v) => update("notifications", v)} />
      </SettingCard>

      <SettingCard icon={<Music2 className="w-5 h-5" />} iconBg="bg-primary/25 text-primary" title="Reproduccion" subtitle="Comportamiento del reproductor de musica">
        <Toggle label="Reproduccion automatica al abrir playlist" value={settings.autoplay ?? false} onChange={(v) => update("autoplay", v)} />
      </SettingCard>

      <SettingCard icon={<Info className="w-5 h-5" />} iconBg="bg-muted/60 text-muted-foreground" title="Acerca de" subtitle="Informacion sobre EKHO">
        <div className="grid grid-cols-2 gap-3 text-sm font-mono">
          <span className="text-muted-foreground">Version</span>
          <span>v0.1.0</span>
          <span className="text-muted-foreground">Build</span>
          <span>2026.05.11</span>
        </div>
      </SettingCard>
    </div>
  );
}
