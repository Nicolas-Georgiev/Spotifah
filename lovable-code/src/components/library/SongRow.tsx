import { useState } from "react";
import { Play, Heart } from "lucide-react";
import { CoverArt } from "../shared/CoverArt";
import { SourceBadge } from "./SourceBadge";
import { bridge, type Song } from "../../lib/bridge";
import {
  ContextMenu,
  ContextMenuTrigger,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
} from "../ui/context-menu";

interface Props {
  song: Song;
  index: number;
  isActive: boolean;
  onPlay: (id: string) => void;
  fmtDuration: (seconds: number) => string;
  playlistId?: string;
  onRemoveFromPlaylist?: (songId: string) => void;
}

export function SongRow({ song, index, isActive, onPlay, fmtDuration, playlistId, onRemoveFromPlaylist }: Props) {
  const [favorite, setFavorite] = useState(false);

  const toggleFav = async (e?: React.MouseEvent) => {
    e?.stopPropagation();
    const res = await bridge.toggleFavorite(song.id);
    if (res.ok) setFavorite(res.favorite);
  };

  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <li
          onClick={() => onPlay(song.id)}
          className={`grid grid-cols-[40px_3fr_2fr_2fr_120px_80px_40px] gap-4 px-5 py-3 items-center hover:bg-muted/30 transition group cursor-pointer ${
            isActive ? "bg-primary/10" : ""
          }`}
        >
          <span className="text-sm font-mono text-muted-foreground group-hover:hidden">{index + 1}</span>
          <Play className="w-4 h-4 hidden group-hover:block fill-current text-primary" />
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 rounded bg-muted/40 flex items-center justify-center shrink-0">
              <CoverArt
                src={song.cover_url}
                alt=""
                className="w-full h-full rounded object-cover"
                icon="♪"
              />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{song.title}</p>
            </div>
          </div>
          <span className="text-sm text-muted-foreground truncate">{song.artist}</span>
          <span className="text-sm text-muted-foreground truncate">{song.album}</span>
          <span>
            <SourceBadge source={song.source} />
          </span>
          <span className="text-sm text-muted-foreground font-mono text-right">{fmtDuration(song.duration)}</span>
          <button
            onClick={toggleFav}
            className="text-muted-foreground hover:text-red-400 transition p-1"
            aria-label={favorite ? "Quitar de favoritos" : "Añadir a favoritos"}
          >
            <Heart className={`w-4 h-4 ${favorite ? "fill-red-400 text-red-400" : ""}`} />
          </button>
        </li>
      </ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem onClick={() => onPlay(song.id)}>
          <Play className="w-4 h-4 mr-2" /> Reproducir
        </ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuItem onClick={toggleFav}>
          <Heart className={`w-4 h-4 mr-2 ${favorite ? "fill-red-400 text-red-400" : ""}`} />
          {favorite ? "Quitar de favoritos" : "Añadir a favoritos"}
        </ContextMenuItem>
        {playlistId && playlistId !== "all" && onRemoveFromPlaylist && (
          <>
            <ContextMenuSeparator />
            <ContextMenuItem
              onClick={(e) => { e.stopPropagation(); onRemoveFromPlaylist(song.id); }}
              className="text-destructive focus:text-destructive"
            >
              Eliminar de playlist
            </ContextMenuItem>
          </>
        )}
      </ContextMenuContent>
    </ContextMenu>
  );
}
