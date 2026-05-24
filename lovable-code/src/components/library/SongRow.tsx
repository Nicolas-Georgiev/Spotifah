import { useState, useEffect } from "react";
import { Play, Heart, MoreVertical, ListMusic, Trash2, ListMinus, Plus, Pencil } from "lucide-react";
import { toast } from "sonner";
import { CoverArt } from "../shared/CoverArt";
import { SourceBadge } from "./SourceBadge";
import { SongEditDialog } from "./SongEditDialog";
import { bridge, type Song, type Playlist } from "../../lib/bridge";
import {
  ContextMenu,
  ContextMenuTrigger,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
} from "../ui/context-menu";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "../ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "../ui/alert-dialog";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";

interface Props {
  song: Song;
  index: number;
  isActive: boolean;
  onPlay: (id: string) => void;
  fmtDuration: (seconds: number) => string;
  playlistId?: string;
  onRemoveFromPlaylist?: (songId: string) => void;
  onSongDeleted?: (songId: string) => void;
  onSongUpdated?: (song: Song) => void;
}

function formatDownloadDate(date: string): string {
  if (!date) return "";
  try {
    const d = new Date(date);
    if (isNaN(d.getTime())) return date;
    return d.toLocaleDateString("es-ES", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return date;
  }
}

export function SongRow({ song, index, isActive, onPlay, fmtDuration, playlistId, onRemoveFromPlaylist, onSongDeleted, onSongUpdated }: Props) {
  const [favorite, setFavorite] = useState(false);
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [localSong, setLocalSong] = useState(song);

  useEffect(() => {
    setLocalSong(song);
  }, [song]);

  useEffect(() => {
    bridge.getPlaylists().then(setPlaylists);
  }, []);

  useEffect(() => {
    bridge.isFavorite(localSong.id).then((res) => {
      if (res.ok) setFavorite(res.favorite);
    });
  }, [localSong.id]);

  const handleSongUpdated = (updatedSong: Song) => {
    setLocalSong(updatedSong);
    onSongUpdated?.(updatedSong);
  };

  const toggleFav = async (e?: React.MouseEvent) => {
    e?.stopPropagation();
    const res = await bridge.toggleFavorite(song.id);
    if (res.ok) {
      setFavorite(res.favorite);
      if (!res.favorite && onRemoveFromPlaylist) {
        const favPlaylist = playlists.find((p) => p.name === "Favoritos");
        if (favPlaylist && playlistId === favPlaylist.id) {
          onRemoveFromPlaylist(song.id);
        }
      }
    }
  };

  const handleAddToPlaylist = async (e: React.MouseEvent, targetPlaylistId: string, playlistName: string) => {
    e.stopPropagation();
    const res = await bridge.addSongToPlaylist(targetPlaylistId, localSong.id);
    if (res.ok && res.data?.already_exists) {
      toast.info(`"${localSong.title}" ya está en "${playlistName}"`);
    } else if (res.ok) {
      toast.success(`"${localSong.title}" añadida a "${playlistName}"`);
      if (playlistName === "Favoritos") setFavorite(true);
    } else {
      toast.error("Error al añadir a playlist", { description: res.error });
    }
  };

  const handleDeleteSong = async () => {
    await bridge.deleteSong(song.id);
    onSongDeleted?.(song.id);
  };

  const filteredPlaylists = playlists.filter((p) => p.id !== "all");

  return (
    <><ContextMenu>
      <ContextMenuTrigger>
        <li
          onClick={() => onPlay(song.id)}
          className={`grid grid-cols-[40px_3fr_2fr_2fr_100px_80px_130px_80px] gap-4 px-5 py-3 items-center hover:bg-muted/30 transition group cursor-pointer ${
            isActive ? "bg-primary/10" : ""
          }`}
        >
          <span className="text-sm font-mono text-muted-foreground group-hover:hidden">{index + 1}</span>
          <Play className="w-4 h-4 hidden group-hover:block fill-current text-primary" />
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 rounded bg-muted/40 flex items-center justify-center shrink-0">
              <CoverArt
                src={localSong.cover_url}
                alt=""
                className="w-full h-full rounded object-cover"
                icon="♪"
              />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{localSong.title}</p>
            </div>
          </div>
          <span className="text-sm text-muted-foreground truncate">{localSong.artist}</span>
          <span className="text-sm text-muted-foreground truncate">{localSong.album}</span>
          <span>
            <SourceBadge source={localSong.source} />
          </span>
          <span className="text-sm text-muted-foreground font-mono text-right tabular-nums">{fmtDuration(localSong.duration)}</span>
          <span className="text-xs text-muted-foreground font-mono">
            {localSong.download_date ? formatDownloadDate(localSong.download_date) : "-"}
          </span>
          <div className="flex items-center gap-0 justify-end">
            <button
              onClick={toggleFav}
              className="text-muted-foreground hover:text-primary transition p-1"
              aria-label={favorite ? "Quitar de favoritos" : "Añadir a favoritos"}
            >
              <Heart className={`w-4 h-4 ${favorite ? "fill-primary text-primary" : ""}`} />
            </button>
            <Dialog>
              <AlertDialog>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button
                      onClick={(e) => e.stopPropagation()}
                      className="text-muted-foreground hover:text-foreground transition p-1 opacity-0 group-hover:opacity-100"
                      aria-label="Más opciones"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()} className="min-w-44">
                    <DialogTrigger asChild>
                      <DropdownMenuItem onSelect={(e) => e.preventDefault()} className="focus:bg-muted focus:text-foreground">
                        <Plus className="w-4 h-4 mr-2" />
                        Añadir a playlist
                      </DropdownMenuItem>
                    </DialogTrigger>
                    <DropdownMenuItem onSelect={(e) => { e.preventDefault(); setEditDialogOpen(true); }} className="focus:bg-muted focus:text-foreground">
                      <Pencil className="w-4 h-4 mr-2" />
                      Editar información
                    </DropdownMenuItem>
                    {playlistId && playlistId !== "all" && onRemoveFromPlaylist && (
                      <DropdownMenuItem
                        onSelect={(e) => {
                          e.preventDefault();
                          const favPlaylist = playlists.find((p) => p.name === "Favoritos");
                          if (favPlaylist && playlistId === favPlaylist.id) setFavorite(false);
                          onRemoveFromPlaylist(song.id);
                        }}
                        className="focus:bg-muted focus:text-foreground"
                      >
                        <ListMinus className="w-4 h-4 mr-2" />
                        Quitar de playlist
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuSeparator />
                    <AlertDialogTrigger asChild>
                      <DropdownMenuItem
                        onSelect={(e) => e.preventDefault()}
                        className="text-destructive focus:bg-muted focus:text-destructive"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Borrar canción
                      </DropdownMenuItem>
                    </AlertDialogTrigger>
                  </DropdownMenuContent>
                </DropdownMenu>
                <AlertDialogContent onClick={(e) => e.stopPropagation()}>
                  <AlertDialogHeader>
                    <AlertDialogTitle>¿Borrar canción?</AlertDialogTitle>
                    <AlertDialogDescription>
                      Se eliminará "{localSong.title}" de tu biblioteca y del disco.
                      Esta acción no se puede deshacer.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancelar</AlertDialogCancel>
                    <AlertDialogAction onClick={handleDeleteSong} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                      Borrar
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              <DialogContent onClick={(e) => e.stopPropagation()} className="sm:max-w-sm">
                <DialogHeader>
                  <DialogTitle>Añadir a playlist</DialogTitle>
                </DialogHeader>
                <div className="flex flex-col gap-1 max-h-60 overflow-y-auto">
                  {filteredPlaylists.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      No hay playlists disponibles
                    </p>
                  ) : (
                    filteredPlaylists.map((pl) => (
                      <button
                        key={pl.id}
                        onClick={(e) => handleAddToPlaylist(e, pl.id, pl.name)}
                        className="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-muted text-left transition"
                      >
                        <ListMusic className="w-4 h-4 shrink-0 text-muted-foreground" />
                        <span className="truncate">{pl.name}</span>
                      </button>
                    ))
                  )}
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </li>
      </ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem onClick={() => onPlay(song.id)} className="focus:bg-accent focus:text-accent-foreground">
          <Play className="w-4 h-4 mr-2" /> Reproducir
        </ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuItem onClick={toggleFav} className="focus:bg-accent focus:text-accent-foreground">
          <Heart className={`w-4 h-4 mr-2 ${favorite ? "fill-primary text-primary" : ""}`} />
          {favorite ? "Quitar de favoritos" : "Añadir a favoritos"}
        </ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuItem onClick={() => setEditDialogOpen(true)} className="focus:bg-accent focus:text-accent-foreground">
          <Pencil className="w-4 h-4 mr-2" /> Editar información
        </ContextMenuItem>
        {playlistId && playlistId !== "all" && onRemoveFromPlaylist && (
          <>
            <ContextMenuSeparator />
            <ContextMenuItem
              onClick={(e) => { e.stopPropagation(); onRemoveFromPlaylist(song.id); }}
              className="text-destructive focus:bg-muted focus:text-destructive"
            >
              Eliminar de playlist
            </ContextMenuItem>
          </>
        )}
      </ContextMenuContent>
    </ContextMenu>
      <SongEditDialog
        song={localSong}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onSongUpdated={handleSongUpdated}
      />
    </>
  );
}
