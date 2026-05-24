import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { bridge } from "../lib/bridge";
import { SettingCard } from "../components/settings/SettingCard";
import { Toggle } from "../components/settings/Toggle";
import { BitrateSelect } from "../components/settings/BitrateSelect";
import { ThemeSelect } from "../components/settings/ThemeSelect";
import { DownloadPathSelect } from "../components/settings/DownloadPathSelect";

export const Route = createFileRoute("/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, any>>({});

  useEffect(() => {
    bridge.getSettings().then((s) => {
      setSettings(s);
    });
  }, []);

  const update = async (key: string, value: any) => {
    await bridge.updateSettings({ [key]: value });
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold">Configuracion</h1>
        <p className="text-sm text-muted-foreground mt-2">Personaliza tu experiencia en EKHO</p>
      </header>

      <SettingCard title="Calidad de Descarga" subtitle="Bitrate predeterminado para conversiones a MP3">
        <BitrateSelect value={settings.download_quality ?? "192"} onChange={(v) => update("download_quality", v)} />
      </SettingCard>

      <SettingCard title="Carpeta de Descarga" subtitle="Donde se guardaran las canciones convertidas">
        <DownloadPathSelect value={settings.download_path ?? ""} onChange={(v) => update("download_path", v)} />
      </SettingCard>

      <SettingCard title="Notificaciones" subtitle="Recibe avisos cuando se completen las conversiones">
        <Toggle label="Notificaciones del sistema" value={settings.notifications ?? true} onChange={(v) => update("notifications", v)} />
      </SettingCard>

      <SettingCard title="Reproduccion" subtitle="Comportamiento del reproductor de musica">
        <Toggle label="Reproduccion automatica al abrir playlist" value={settings.autoplay ?? false} onChange={(v) => update("autoplay", v)} />
      </SettingCard>

      <SettingCard title="Tema" subtitle="Personaliza la apariencia de EKHO">
        <ThemeSelect />
      </SettingCard>

      <SettingCard title="Acerca de" subtitle="Informacion sobre EKHO">
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
