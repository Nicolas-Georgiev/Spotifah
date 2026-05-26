import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, useCallback } from "react";
import { bridge } from "../lib/bridge";
import { useAppData } from "../lib/app-data";
import { SettingCard } from "../components/settings/SettingCard";
import { Toggle } from "../components/settings/Toggle";
import { BitrateSelect } from "../components/settings/BitrateSelect";
import { ThemeSelect } from "../components/settings/ThemeSelect";
import { DownloadPathSelect } from "../components/settings/DownloadPathSelect";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, any>>({});
  const { setCurrentPlayingId, triggerPlayerRefresh, refreshPlaylists, refreshSongs } = useAppData();
  const [deleteOpen, setDeleteOpen] = useState(false);

  useEffect(() => {
    bridge.getSettings().then((s) => {
      setSettings(s);
    });
  }, []);

  const update = async (key: string, value: any) => {
    await bridge.updateSettings({ [key]: value });
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleDeleteAll = async () => {
    const res = await bridge.deleteAllData();
    if (res.ok) {
      setCurrentPlayingId(null);
      triggerPlayerRefresh();
      await Promise.all([refreshPlaylists(), refreshSongs()]);
      toast.success("Todos los datos eliminados");
    } else {
      toast.error("Error al eliminar datos", { description: res.error });
    }
    setDeleteOpen(false);
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

      <SettingCard title="Spotify" subtitle="Conecta tu cuenta para recomendaciones más precisas">
        <SpotifyConnect />
      </SettingCard>

      <SettingCard title="Acerca de" subtitle="Informacion sobre EKHO">
        <div className="grid grid-cols-2 gap-3 text-sm font-mono">
          <span className="text-muted-foreground">Version</span>
          <span>v0.1.0</span>
          <span className="text-muted-foreground">Build</span>
          <span>2026.05.11</span>
        </div>
      </SettingCard>

      <SettingCard title="Eliminar todos los datos" subtitle="Borra todas las canciones y playlists de tu biblioteca">
        <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
          <AlertDialogTrigger asChild>
            <Button variant="destructive" className="w-full">
              <Trash2 className="w-4 h-4" /> Eliminar todo
            </Button>
          </AlertDialogTrigger>
          <AlertDialogPortal>
            <AlertDialogOverlay />
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Eliminar todos los datos</AlertDialogTitle>
                <AlertDialogDescription>
                  ¿Estás seguro? Se eliminarán todas las canciones, playlists y archivos del disco.
                  Esta acción no se puede deshacer.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                <AlertDialogAction asChild>
                  <Button variant="destructive" onClick={handleDeleteAll}>
                    Eliminar todo
                  </Button>
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialogPortal>
        </AlertDialog>
      </SettingCard>
    </div>
  );
}

function SpotifyConnect() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [expiresAt, setExpiresAt] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const s = await bridge.getSettings();
    setLoggedIn(!!(s.spotify_access_token ?? null));
    setExpiresAt(s.spotify_token_expires_at ?? null);
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  useEffect(() => {
    bridge.getSettings().then((s) => {
      setClientId(s.spotify_client_id ?? s.SPOTIFY_CLIENT_ID ?? "");
      setClientSecret(s.spotify_client_secret ?? s.SPOTIFY_CLIENT_SECRET ?? "");
    });
  }, []);

  const handleSave = async () => {
    // Open a blank popup immediately to avoid browser popup blockers
    let popup: Window | null = null;
    try {
      popup = window.open("", "_blank");
    } catch {}

    setErrorMsg(null);
    setSaving(true);
    try {
      await bridge.updateSettings({ spotify_client_id: clientId || null, spotify_client_secret: clientSecret || null });
      // If credentials were provided, navigate the popup to the OAuth login URL
      if (clientId && clientSecret) {
        try {
          const host = window.location.hostname || "127.0.0.1";
          const url = `http://${host}:57291/spotify/login`;
          if (popup) {
            popup.location.href = url;
          } else {
            const ok = await bridge.openSpotifyLogin();
            if (!ok) setErrorMsg("No se pudo abrir el navegador. Reinicia la app o abre esta URL manualmente: " + url);
          }
        } catch {
          const ok = await bridge.openSpotifyLogin();
          if (!ok) setErrorMsg("No se pudo abrir el navegador. Reinicia la app o abre esta URL manualmente: " + URL);
        }
      }
    } catch (e) {
      // ignore
    } finally {
      setSaving(false);
    }

    await refresh();
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await bridge.spotifyLogout();
    } finally {
      setLoading(false);
      await refresh();
    }
  };

  return (
    <div className="grid gap-3">
      <div className="text-sm text-muted-foreground">{loggedIn ? "Conectado a Spotify" : "No conectado"}</div>
      <div className="flex items-center gap-2">
        {loggedIn ? (
          <Button onClick={handleLogout} variant="secondary" className={loading ? "cursor-not-allowed" : "cursor-pointer"} disabled={loading}>Desconectar</Button>
        ) : (
          <Button onClick={handleSave} className={saving ? "cursor-not-allowed" : "cursor-pointer"} disabled={saving}>Guardar credenciales</Button>
        )}
      </div>
      {expiresAt ? (
        <div className="text-xs text-muted-foreground">Token expira: {new Date(expiresAt * 1000).toLocaleString()}</div>
      ) : null}

      {errorMsg ? <div className="text-xs text-destructive">{errorMsg}</div> : null}

      <div className="grid gap-2 pt-2">
        <label className="text-xs text-muted-foreground">Client ID</label>
        <input value={clientId} onChange={(e) => setClientId(e.target.value)} className="w-full rounded-md border px-3 py-2 bg-background/10 text-sm" />
        <label className="text-xs text-muted-foreground">Client Secret</label>
        <input value={clientSecret} onChange={(e) => setClientSecret(e.target.value)} className="w-full rounded-md border px-3 py-2 bg-background/10 text-sm" />
      </div>
    </div>
  );
}
