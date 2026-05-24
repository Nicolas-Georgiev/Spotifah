import { useState, useRef } from "react";
import { Link } from "@tanstack/react-router";
import { MoreHorizontal, Pencil, Trash2, Music, Upload } from "lucide-react";
import type { Playlist } from "../../lib/bridge";
import { bridge } from "../../lib/bridge";
import { CoverArt } from "../shared/CoverArt";
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
import { Textarea } from "../ui/textarea";

interface Props {
  playlist: Playlist;
  onRename?: () => void;
  onDelete?: () => void;
}

export function PlaylistCard({ playlist, onRename, onDelete }: Props) {
  const isSpecial = playlist.id === "all" || playlist.name === "Favoritos";
  const [renameOpen, setRenameOpen] = useState(false);
  const [newName, setNewName] = useState(playlist.name);
  const [newDescription, setNewDescription] = useState(playlist.description);
  const [coverBase64, setCoverBase64] = useState<string | null>(null);
  const [coverPreview, setCoverPreview] = useState<string | null>(null);
  const [coverVersion, setCoverVersion] = useState(() => Date.now());
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      setCoverBase64(result);
      setCoverPreview(result);
    };
    reader.readAsDataURL(file);
  };

  const handleRename = async () => {
    if (!newName.trim()) return;
    await bridge.renamePlaylist(playlist.id, newName.trim(), newDescription.trim(), coverBase64 || undefined);
    if (coverBase64) setCoverVersion(Date.now());
    setRenameOpen(false);
    setCoverBase64(null);
    setCoverPreview(null);
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
            {coverPreview || playlist.cover_url ? (
              <img
                src={coverPreview || `${playlist.cover_url}?v=${coverVersion}`}
                alt={playlist.name}
                className="w-full h-full object-cover"
                onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
              />
            ) : (
              <Music className="w-16 h-16 text-muted-foreground/40" />
            )}
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
                <DropdownMenuItem onClick={() => { setNewName(playlist.name); setNewDescription(playlist.description); setCoverBase64(null); setCoverPreview(null); setRenameOpen(true); }} className="focus:bg-muted focus:text-foreground">
                  <Pencil className="w-4 h-4 mr-2" /> Renombrar
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleDelete} className="text-destructive focus:bg-muted focus:text-destructive">
                  <Trash2 className="w-4 h-4 mr-2" /> Eliminar
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>

      <Dialog open={renameOpen} onOpenChange={(open) => { setRenameOpen(open); if (!open) { setCoverBase64(null); setCoverPreview(null); } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar playlist</DialogTitle>
            <DialogDescription>Cambia el nombre, descripción o portada de la playlist</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <div className="flex flex-col items-center gap-2">
              <div className="w-28 h-28 rounded-lg overflow-hidden bg-muted/40">
                <CoverArt
                  src={coverPreview || playlist.cover_url}
                  alt={playlist.name}
                  className="w-full h-full object-cover"
                  icon="♪"
                />
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleFileChange}
              />
              <Button
                variant="outline"
                size="sm"
                type="button"
                className="hover:bg-muted hover:text-foreground"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-4 h-4 mr-2" />
                Cambiar portada
              </Button>
            </div>
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              autoFocus
              onKeyDown={(e) => { if (e.key === "Enter") handleRename(); }}
            />
            <Textarea
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              placeholder="Descripción (opcional)"
              className="resize-none"
              rows={3}
            />
            <div className="flex justify-end gap-2">
              <DialogClose asChild>
                <Button variant="outline" className="hover:bg-muted hover:text-foreground">Cancelar</Button>
              </DialogClose>
              <Button onClick={handleRename} disabled={!newName.trim()}>Guardar</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
