import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import type { Playlist } from "../../lib/bridge";
import { bridge } from "../../lib/bridge";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "../ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { Input } from "../ui/input";

interface Props {
  playlist: Playlist;
  onRename?: () => void;
  onDelete?: () => void;
}

export function PlaylistCard({ playlist, onRename, onDelete }: Props) {
  const isSpecial = playlist.id === "all" || playlist.id === "favorites";
  const [renameOpen, setRenameOpen] = useState(false);
  const [newName, setNewName] = useState(playlist.name);

  const handleRename = async () => {
    if (!newName.trim()) return;
    await bridge.renamePlaylist(playlist.id, newName.trim());
    setRenameOpen(false);
    onRename?.();
  };

  const handleDelete = async () => {
    await bridge.deletePlaylist(playlist.id);
    onDelete?.();
  };

  return (
    <>
      <div className="relative group">
        <Link
          to="/library/$playlistId"
          params={{ playlistId: playlist.id }}
          className="glass rounded-2xl overflow-hidden hover:-translate-y-1 transition block"
        >
          <div className="relative aspect-square overflow-hidden bg-muted/40 flex items-center justify-center">
            <span className="text-6xl">♪</span>
            {isSpecial ? (
              <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-primary/30 backdrop-blur border border-primary/50 text-xs font-medium flex items-center gap-1">
                ♪ Coleccion
              </div>
            ) : null}
          </div>
          <div className="p-4">
            <h3 className="font-semibold text-lg">{playlist.name}</h3>
            <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{playlist.description}</p>
            <div className="flex justify-between text-xs text-muted-foreground mt-3 font-mono">
              <span>{playlist.is_public ? "Publica" : "Privada"}</span>
            </div>
          </div>
        </Link>
        {!isSpecial && (
          <div className="absolute top-3 left-3 opacity-0 group-hover:opacity-100 transition">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="w-8 h-8 rounded-full bg-background/80 backdrop-blur border border-border grid place-items-center hover:bg-muted/50 transition">
                  <MoreHorizontal className="w-4 h-4" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem onClick={() => { setNewName(playlist.name); setRenameOpen(true); }}>
                  <Pencil className="w-4 h-4 mr-2" /> Renombrar
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleDelete} className="text-destructive focus:text-destructive">
                  <Trash2 className="w-4 h-4 mr-2" /> Eliminar
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>

      <Dialog open={renameOpen} onOpenChange={setRenameOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Renombrar Playlist</DialogTitle>
            <DialogDescription>Ingresa el nuevo nombre para la playlist</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              autoFocus
              onKeyDown={(e) => { if (e.key === "Enter") handleRename(); }}
            />
            <div className="flex justify-end gap-2">
              <DialogClose asChild>
                <Button variant="outline">Cancelar</Button>
              </DialogClose>
              <Button onClick={handleRename} disabled={!newName.trim()}>Renombrar</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
