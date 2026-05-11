import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Palette, Bell, Download, Music2, Info } from "lucide-react";
import { bridge } from "../lib/bridge";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [{ title: "Configuracion — EKHO" }] }),
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
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-muted-foreground">Cargando configuracion...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold">Configuracion</h1>
        <p className="text-sm text-muted-foreground mt-2">Personaliza tu experiencia en EKHO</p>
      </header>

      <Card icon={<Download className="w-5 h-5" />} iconBg="bg-secondary/25 text-secondary" title="Calidad de Descarga" subtitle="Bitrate predeterminado para conversiones a MP3">
        <label className="text-xs font-medium text-muted-foreground">Bitrate</label>
        <select
          value={settings.download_quality ?? "192"}
          onChange={(e) => update("download_quality", e.target.value)}
          className="mt-1.5 w-full bg-input/60 border border-border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="128">128 kbps</option>
          <option value="192">192 kbps</option>
          <option value="256">256 kbps</option>
          <option value="320">320 kbps</option>
        </select>
      </Card>

      <Card icon={<Bell className="w-5 h-5" />} iconBg="bg-yellow-500/25 text-yellow-400" title="Notificaciones" subtitle="Recibe avisos cuando se completen las conversiones">
        <Toggle label="Notificaciones del sistema" value={settings.notifications ?? true} onChange={(v) => update("notifications", v)} />
      </Card>

      <Card icon={<Music2 className="w-5 h-5" />} iconBg="bg-primary/25 text-primary" title="Reproduccion" subtitle="Comportamiento del reproductor de musica">
        <Toggle label="Reproduccion automatica al abrir playlist" value={settings.autoplay ?? false} onChange={(v) => update("autoplay", v)} />
      </Card>

      <Card icon={<Info className="w-5 h-5" />} iconBg="bg-muted/60 text-muted-foreground" title="Acerca de" subtitle="Informacion sobre EKHO">
        <div className="grid grid-cols-2 gap-3 text-sm font-mono">
          <span className="text-muted-foreground">Version</span>
          <span>v0.1.0</span>
          <span className="text-muted-foreground">Build</span>
          <span>2026.05.11</span>
        </div>
      </Card>
    </div>
  );
}

function Card({ icon, iconBg, title, subtitle, children }: { icon: React.ReactNode; iconBg: string; title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <section className="glass rounded-2xl p-5 sm:p-6">
      <div className="flex items-start gap-4">
        <div className={`w-11 h-11 rounded-xl grid place-items-center shrink-0 ${iconBg}`}>{icon}</div>
        <div className="flex-1">
          <h2 className="text-lg font-semibold">{title}</h2>
          <p className="text-sm text-muted-foreground mt-0.5">{subtitle}</p>
          <div className="mt-4">{children}</div>
        </div>
      </div>
    </section>
  );
}

function Toggle({ label, value, onChange }: { label: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!value)}
      className="w-full flex items-center justify-between p-3 rounded-lg bg-muted/20 hover:bg-muted/30 transition"
    >
      <span className="text-sm">{label}</span>
      <span className={`relative w-11 h-6 rounded-full transition ${value ? "bg-primary" : "bg-muted"}`}>
        <span className={`absolute top-0.5 ${value ? "left-5" : "left-0.5"} w-5 h-5 rounded-full bg-background transition-all`} />
      </span>
    </button>
  );
}
