import { bridge, type Song, type Playlist } from "./bridge";

export type { Song, Playlist };

export const songs: Song[] = [];
export const playlists: Playlist[] = [];
export const recentlyPlayed: number[] = [];

export async function fetchPlaylists(): Promise<Playlist[]> {
  return bridge.getPlaylists();
}

export async function fetchPlaylistSongs(playlistId: string): Promise<Song[]> {
  return bridge.getPlaylistSongs(playlistId);
}

export async function fetchSongs(): Promise<Song[]> {
  return bridge.getSongs();
}
