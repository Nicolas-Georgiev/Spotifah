import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Trash2 } from "lucide-react";
import { bridge } from "../lib/bridge";
import { useAppData } from "../lib/app-data";
import { SettingCard } from "../components/settings/SettingCard";
import { Toggle } from "../components/settings/Toggle";
import { BitrateSelect } from "../components/settings/BitrateSelect";
import { ThemeSelect } from "../components/settings/ThemeSelect";
import { DownloadPathSelect } from "../components/settings/DownloadPathSelect";
import { Button } from "../components/ui/button";
import {
  AlertDialog,
  AlertDialogPortal,
  AlertDialogOverlay,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogAction,
  AlertDialogCancel,
} from "../components/ui/alert-dialog";

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
