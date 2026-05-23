import { Plus } from "lucide-react";

export function CreatePlaylistButton() {
  return (
    <button
      type="button"
      className="glass rounded-2xl border-dashed border-2 border-border/60 flex flex-col items-center justify-center min-h-[280px] hover:bg-muted/20 transition group"
    >
      <div className="w-16 h-16 rounded-full bg-muted/40 grid place-items-center mb-3 group-hover:bg-primary/20 transition">
        <Plus className="w-7 h-7 text-muted-foreground group-hover:text-primary" />
      </div>
      <p className="font-semibold">Crear Nueva Playlist</p>
      <p className="text-xs text-muted-foreground mt-1">Agrupa tus canciones favoritas</p>
    </button>
  );
}
