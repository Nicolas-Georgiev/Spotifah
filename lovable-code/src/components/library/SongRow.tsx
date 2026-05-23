import { Play } from "lucide-react";
import { CoverArt } from "../shared/CoverArt";
import { SourceBadge } from "./SourceBadge";
import type { Song } from "../../lib/bridge";

interface Props {
  song: Song;
  index: number;
  isActive: boolean;
  onPlay: (id: string) => void;
  fmtDuration: (seconds: number) => string;
}

export function SongRow({ song, index, isActive, onPlay, fmtDuration }: Props) {
  return (
    <li
      key={song.id}
      onClick={() => onPlay(song.id)}
      className={`grid grid-cols-[40px_3fr_2fr_2fr_120px_80px] gap-4 px-5 py-3 items-center hover:bg-muted/30 transition group cursor-pointer ${
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
    </li>
  );
}
