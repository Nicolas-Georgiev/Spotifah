export interface Song {
  id: string;
  title: string;
  artist: string;
  album: string;
  duration: number;
  genre: string;
  source: string;
  path: string;
  cover_url: string;
}

export interface Playlist {
  id: string;
  name: string;
  description: string;
  is_public: boolean;
}

interface ConvertResult {
  ok: boolean;
  data?: { path: string; filename: string; log: string };
  error?: string;
}

interface ActionResult {
  ok: boolean;
  data?: { message: string };
  error?: string;
}

interface SystemStatus {
  dependencies: Record<string, boolean>;
  ffmpeg: boolean;
  music_count: number;
}

const FALLBACK_PLAYLISTS: Playlist[] = [
  { id: "all", name: "Todas mis canciones", description: "Todas las canciones en tu biblioteca", is_public: false },
  { id: "favorites", name: "Favoritos", description: "Tus canciones favoritas", is_public: false },
];

const FALLBACK_SONGS: Song[] = [
  { id: "1", title: "Blinding Lights", artist: "The Weeknd", album: "After Hours", duration: 200, genre: "Pop", source: "spotify", path: "", cover_url: "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=400&h=400&fit=crop" },
  { id: "2", title: "Levitating", artist: "Dua Lipa", album: "Future Nostalgia", duration: 203, genre: "Pop", source: "youtube", path: "", cover_url: "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=400&h=400&fit=crop" },
  { id: "3", title: "Save Your Tears", artist: "The Weeknd", album: "After Hours", duration: 215, genre: "Pop", source: "spotify", path: "", cover_url: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400&h=400&fit=crop" },
  { id: "4", title: "Good 4 U", artist: "Olivia Rodrigo", album: "SOUR", duration: 178, genre: "Pop", source: "youtube", path: "", cover_url: "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=400&h=400&fit=crop" },
  { id: "5", title: "Heat Waves", artist: "Glass Animals", album: "Dreamland", duration: 238, genre: "Pop", source: "spotify", path: "", cover_url: "https://images.unsplash.com/photo-1487180144351-b8472da7d491?w=400&h=400&fit=crop" },
  { id: "6", title: "As It Was", artist: "Harry Styles", album: "Harry's House", duration: 167, genre: "Pop", source: "youtube", path: "", cover_url: "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400&h=400&fit=crop" },
];

const isBrowser = typeof window !== "undefined";
const api = isBrowser ? (window as any).pywebview?.api : null;

function fmtDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export const bridge = {
  async getPlaylists(): Promise<Playlist[]> {
    try {
      if (api) {
        const result = await api.get_playlists();
        if (Array.isArray(result)) return result;
        return FALLBACK_PLAYLISTS;
      }
      return FALLBACK_PLAYLISTS;
    } catch {
      return FALLBACK_PLAYLISTS;
    }
  },

  async getPlaylistSongs(playlistId: string): Promise<Song[]> {
    try {
      if (api) {
        const result = await api.get_playlist_songs(playlistId);
        if (Array.isArray(result)) return result;
        return FALLBACK_SONGS;
      }
      return FALLBACK_SONGS;
    } catch {
      return FALLBACK_SONGS;
    }
  },

  async getSongs(): Promise<Song[]> {
    return bridge.getPlaylistSongs("all");
  },

  async convertYoutube(url: string): Promise<ConvertResult> {
    try {
      if (api) return await api.convert_youtube(url);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error en conversión" };
    }
  },

  async convertSpotify(url: string): Promise<ConvertResult> {
    try {
      if (api) return await api.convert_spotify(url);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error en conversión" };
    }
  },

  async playSong(songId: string): Promise<ActionResult> {
    try {
      if (api) return await api.play_song(songId);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al reproducir" };
    }
  },

  async pauseSong(): Promise<ActionResult> {
    try {
      if (api) return await api.pause_song();
      return { ok: true, data: { message: "Simulado" } };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async resumeSong(): Promise<ActionResult> {
    try {
      if (api) return await api.resume_song();
      return { ok: true, data: { message: "Simulado" } };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async stopSong(): Promise<ActionResult> {
    try {
      if (api) return await api.stop_song();
      return { ok: true, data: { message: "Simulado" } };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async nextSong(): Promise<ActionResult> {
    try {
      if (api) return await api.next_song();
      return { ok: true, data: { message: "Simulado" } };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async prevSong(): Promise<ActionResult> {
    try {
      if (api) return await api.prev_song();
      return { ok: true, data: { message: "Simulado" } };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async getSettings(): Promise<Record<string, any>> {
    try {
      if (api) return await api.get_settings();
      return { volume: 80, theme: "dark", download_quality: "192" };
    } catch {
      return { volume: 80, theme: "dark", download_quality: "192" };
    }
  },

  async updateSettings(data: Record<string, any>): Promise<ActionResult> {
    try {
      if (api) return await api.update_settings(data);
      return { ok: true, data: { message: "Simulado" } };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async getSystemStatus(): Promise<SystemStatus> {
    try {
      if (api) return await api.get_system_status();
      return { dependencies: {}, ffmpeg: false, music_count: FALLBACK_SONGS.length };
    } catch {
      return { dependencies: {}, ffmpeg: false, music_count: 0 };
    }
  },

  async addSongToPlaylist(playlistId: string, songId: string): Promise<ActionResult> {
    try {
      if (api) return await api.add_song_to_playlist(playlistId, songId);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async removeSongFromPlaylist(playlistId: string, songId: string): Promise<ActionResult> {
    try {
      if (api) return await api.remove_song_from_playlist(playlistId, songId);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },
};

export { fmtDuration };
