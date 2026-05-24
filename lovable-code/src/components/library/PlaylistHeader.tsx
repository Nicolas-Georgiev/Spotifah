import { useNavigate } from "@tanstack/react-router";
import { Play, Trash2, Music } from "lucide-react";
import { useState } from "react";
import type { Playlist, Song } from "../../lib/bridge";
import { bridge } from "../../lib/bridge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "../ui/dialog";
import { Button } from "../ui/button";

interface Props {
  playlist: Playlist;
  songs: Song[];
  totalMin: number;
  onPlayAll: () => void;
}

export function PlaylistHeader({ playlist, songs, totalMin, onPlayAll }: Props) {
  const navigate = useNavigate();
  const [deleteOpen, setDeleteOpen] = useState(false);
  const isSpecial = playlist.id === "all" || playlist.name === "Favoritos";

  const handleDelete = async () => {
    await bridge.deletePlaylist(playlist.id);
    setDeleteOpen(false);
    navigate({ to: "/library" });
  };

  return (
    <>
      <header className="flex flex-col sm:flex-row gap-6 items-center sm:items-end">
        <div className="w-40 h-40 sm:w-48 sm:h-48 rounded-2xl bg-primary/20 flex items-center justify-center text-6xl shadow-2xl overflow-hidden">
          {playlist.cover_url ? (
            <img
              src={playlist.cover_url}
              alt={playlist.name}
              className="w-full h-full object-cover"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
            />
          ) : (
            <Music className="w-16 h-16 text-muted-foreground/40" />
          )}
        </div>
        <div className="text-center sm:text-left flex-1">
          <div className="flex flex-wrap items-center gap-2 justify-center sm:justify-start">
            <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-primary/20 text-primary border border-primary/40">
              Playlist
            </span>
          </div>
          <h1 className="text-4xl sm:text-6xl font-bold mt-3">{playlist.name}</h1>
          <p className="text-muted-foreground mt-2">{playlist.description}</p>
          <p className="text-sm text-muted-foreground font-mono mt-3">
            {songs.length} canciones · {totalMin} min
          </p>
        </div>
      </header>

      <div className="flex items-center gap-3">
        <button
          onClick={onPlayAll}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-primary text-primary-foreground font-semibold glow-violet hover:scale-105 transition"
        >
          <Play className="w-4 h-4 fill-current" /> Reproducir todo
        </button>
        {!isSpecial && (
          <button
            onClick={() => setDeleteOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-full border border-border text-muted-foreground hover:text-destructive hover:border-destructive/50 transition text-sm"
            aria-label="Eliminar playlist"
          >
            <Trash2 className="w-4 h-4" /> Eliminar
          </button>
        )}
      </div>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Eliminar Playlist</DialogTitle>
            <DialogDescription>
              ¿Estás seguro de que deseas eliminar "{playlist.name}"? Esta acción no se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 pt-2">
            <DialogClose asChild>
              <Button variant="outline">Cancelar</Button>
            </DialogClose>
            <Button variant="destructive" onClick={handleDelete}>Eliminar</Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
