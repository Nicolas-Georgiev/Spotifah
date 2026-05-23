import { Link } from "@tanstack/react-router";
import { CoverArt } from "./CoverArt";
import type { Song } from "../../lib/bridge";

interface Props {
  song: Song;
}

export function SongCard({ song }: Props) {
  return (
    <Link
      to="/library/$playlistId"
      params={{ playlistId: "all" }}
      className="group"
    >
      <div className="relative rounded-xl overflow-hidden aspect-square bg-muted/40 flex items-center justify-center">
        <CoverArt
          src={song.cover_url}
          alt={song.title}
          className="w-full h-full object-cover transition group-hover:scale-105"
        />
      </div>
      <p className="mt-3 font-semibold truncate">{song.title}</p>
      <p className="text-sm text-muted-foreground truncate">{song.artist}</p>
    </Link>
  );
}
