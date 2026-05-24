import { useState, useRef, useEffect } from "react";
import { Upload } from "lucide-react";
import { toast } from "sonner";
import { CoverArt } from "../shared/CoverArt";
import { bridge, type Song } from "../../lib/bridge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Button } from "../ui/button";

interface Props {
  song: Song;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSongUpdated: (updatedSong: Song) => void;
}

export function SongEditDialog({ song, open, onOpenChange, onSongUpdated }: Props) {
  const [title, setTitle] = useState(song.title);
  const [artist, setArtist] = useState(song.artist || "");
  const [album, setAlbum] = useState(song.album || "");
  const [genre, setGenre] = useState(song.genre || "");
  const [coverBase64, setCoverBase64] = useState<string | null>(null);
  const [coverPreview, setCoverPreview] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setTitle(song.title);
      setArtist(song.artist || "");
      setAlbum(song.album || "");
      setGenre(song.genre || "");
      setCoverBase64(null);
      setCoverPreview(null);
    }
  }, [open, song]);

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

  const handleSave = async () => {
    if (!title.trim()) {
      toast.error("El título no puede estar vacío");
      return;
    }
    setSaving(true);
    const data: Record<string, string> = {};
    if (title !== song.title) data.title = title.trim();
    if (artist !== (song.artist || "")) data.artist = artist.trim();
    if (album !== (song.album || "")) data.album = album.trim();
    if (genre !== (song.genre || "")) data.genre = genre.trim();
    if (coverBase64) data.cover_base64 = coverBase64;

    if (Object.keys(data).length === 0) {
      onOpenChange(false);
      setSaving(false);
      return;
    }

    const res = await bridge.updateSong(song.id, data);
    if (res.ok) {
      toast.success("Canción actualizada");
      onSongUpdated({
        ...song,
        ...(data.title ? { title: data.title } : {}),
        ...(data.artist ? { artist: data.artist } : {}),
        ...(data.album ? { album: data.album } : {}),
        ...(data.genre ? { genre: data.genre } : {}),
        ...(coverBase64 ? { cover_url: coverPreview || song.cover_url } : {}),
      });
      onOpenChange(false);
    } else {
      toast.error("Error al actualizar", { description: res.error });
    }
    setSaving(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent onClick={(e) => e.stopPropagation()} className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Editar información</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-4">
          <div className="flex flex-col items-center gap-2">
            <div className="w-32 h-32 rounded-lg overflow-hidden bg-muted/40">
              <CoverArt
                src={coverPreview || song.cover_url}
                alt=""
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
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-4 h-4 mr-2" />
              Cambiar portada
            </Button>
          </div>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label htmlFor="edit-title">Título</Label>
              <Input id="edit-title" value={title} onChange={(e) => setTitle(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="edit-artist">Artista</Label>
              <Input id="edit-artist" value={artist} onChange={(e) => setArtist(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="edit-album">Álbum</Label>
              <Input id="edit-album" value={album} onChange={(e) => setAlbum(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="edit-genre">Género</Label>
              <Input id="edit-genre" value={genre} onChange={(e) => setGenre(e.target.value)} />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" type="button" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="button" onClick={handleSave} disabled={saving}>
              {saving ? "Guardando..." : "Guardar"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
