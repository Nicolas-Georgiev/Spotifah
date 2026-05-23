import { useState } from "react";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { bridge } from "../../lib/bridge";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose } from "../ui/dialog";
import { Button } from "../ui/button";
import { Input } from "../ui/input";

interface Props {
  onCreated: () => void;
}

export function CreatePlaylistButton({ onCreated }: Props) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [busy, setBusy] = useState(false);

  const handleCreate = async () => {
    if (!name.trim() || busy) return;
    setBusy(true);
    const result = await bridge.createPlaylist(name.trim(), desc.trim());
    setBusy(false);
    if (result.ok) {
      toast.success("Playlist creada", {
        description: `"${name.trim()}" se ha creado correctamente.`,
      });
      setOpen(false);
      setName("");
      setDesc("");
      onCreated();
    } else {
      toast.error("Error al crear playlist", {
        description: result.error ?? "Ocurrió un error inesperado",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <button
          type="button"
          className="glass rounded-2xl border-dashed border-2 border-border/60 flex flex-col items-center justify-center min-h-[280px] hover:bg-muted/20 transition group cursor-pointer w-full"
        >
          <div className="w-16 h-16 rounded-full bg-muted/40 grid place-items-center mb-3 group-hover:bg-primary/20 transition">
            <Plus className="w-7 h-7 text-muted-foreground group-hover:text-primary" />
          </div>
          <p className="font-semibold">Crear Nueva Playlist</p>
          <p className="text-xs text-muted-foreground mt-1">Agrupa tus canciones favoritas</p>
        </button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nueva Playlist</DialogTitle>
          <DialogDescription>Crea una nueva playlist para agrupar tus canciones</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <Input
            placeholder="Nombre de la playlist"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoFocus
            onKeyDown={(e) => { if (e.key === "Enter") handleCreate(); }}
          />
          <Input
            placeholder="Descripción (opcional)"
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleCreate(); }}
          />
          <div className="flex justify-end gap-2 pt-2">
            <DialogClose asChild>
              <Button variant="outline">Cancelar</Button>
            </DialogClose>
            <Button onClick={handleCreate} disabled={!name.trim() || busy}>
              {busy ? "Creando..." : "Crear"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
