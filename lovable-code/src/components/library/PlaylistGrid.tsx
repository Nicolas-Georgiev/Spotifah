import type { Playlist } from "../../lib/bridge";
import { PlaylistCard } from "./PlaylistCard";
import { CreatePlaylistButton } from "./CreatePlaylistButton";

interface Props {
  playlists: Playlist[];
}

export function PlaylistGrid({ playlists }: Props) {
  return (
    <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {playlists.map(p => (
        <PlaylistCard key={p.id} playlist={p} />
      ))}
      <CreatePlaylistButton />
    </section>
  );
}
