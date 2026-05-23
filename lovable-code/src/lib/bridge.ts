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

interface NowPlayingData {
  id: string;
  title: string;
  artist: string;
  album: string;
  duration: number;
  cover_url: string;
  is_playing: boolean;
  position: number;
}

interface NowPlayingResult {
  ok: boolean;
  data?: NowPlayingData | null;
}

interface PlaybackPosition {
  position: number;
  is_playing: boolean;
}

interface VolumeData {
  volume: number;
}

interface FavoriteData {
  favorite: boolean;
}

interface CreatePlaylistResult {
  ok: boolean;
  data?: { id: string; name: string; description: string; is_public: boolean };
  error?: string;
}

const isBrowser = typeof window !== "undefined";
const api = isBrowser ? (window as any).pywebview?.api : null;

function fmtDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export const bridge = {
  async getPlaylists(): Promise<Playlist[]> {
    if (!api) return [];
    try {
      const result = await api.get_playlists();
      if (Array.isArray(result)) return result;
      return [];
    } catch {
      return [];
    }
  },

  async getPlaylistSongs(playlistId: string): Promise<Song[]> {
    if (!api) return [];
    try {
      const result = await api.get_playlist_songs(playlistId);
      if (Array.isArray(result)) return result;
      return [];
    } catch {
      return [];
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
    if (!api) return { volume: 80, theme: "dark", download_quality: "192" };
    return await api.get_settings();
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
    if (!api) return { dependencies: {}, ffmpeg: false, music_count: 0 };
    return await api.get_system_status();
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

  async convertSoundcloud(url: string): Promise<ConvertResult> {
    try {
      if (api) return await api.convert_soundcloud(url);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error en conversión" };
    }
  },

  async createPlaylist(name: string, description: string = ""): Promise<CreatePlaylistResult> {
    try {
      if (api) return await api.create_playlist(name, description);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al crear playlist" };
    }
  },

  async deletePlaylist(playlistId: string): Promise<ActionResult> {
    try {
      if (api) return await api.delete_playlist(playlistId);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al eliminar" };
    }
  },

  async renamePlaylist(playlistId: string, name: string): Promise<ActionResult> {
    try {
      if (api) return await api.rename_playlist(playlistId, name);
      return { ok: false, error: "PyWebView no disponible" };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al renombrar" };
    }
  },

  async searchSongs(query: string): Promise<Song[]> {
    if (!api) return [];
    try {
      const result = await api.search_songs(query);
      if (Array.isArray(result)) return result;
      return [];
    } catch {
      return [];
    }
  },

  async toggleFavorite(songId: string): Promise<FavoriteData & { ok: boolean; error?: string }> {
    try {
      if (api) return await api.toggle_favorite(songId);
      return { ok: false, error: "PyWebView no disponible", favorite: false };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error", favorite: false };
    }
  },

  async getNowPlaying(): Promise<NowPlayingResult> {
    try {
      if (api) return await api.get_now_playing();
      return { ok: true, data: null };
    } catch {
      return { ok: true, data: null };
    }
  },

  async getPlaybackPosition(): Promise<PlaybackPosition> {
    try {
      if (api) return await api.get_playback_position();
      return { position: 0, is_playing: false };
    } catch {
      return { position: 0, is_playing: false };
    }
  },

  async setVolume(volume: number): Promise<{ ok: boolean; data?: VolumeData; error?: string }> {
    try {
      if (api) return await api.set_volume(volume);
      return { ok: true, data: { volume } };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al ajustar volumen" };
    }
  },

  async getVolume(): Promise<{ ok: boolean; data?: VolumeData; error?: string }> {
    try {
      if (api) return await api.get_volume();
      return { ok: true, data: { volume: 80 } };
    } catch {
      return { ok: true, data: { volume: 80 } };
    }
  },

  async getRecentlyPlayed(limit: number = 10): Promise<Song[]> {
    if (!api) return [];
    try {
      const result = await api.get_recently_played(limit);
      if (Array.isArray(result)) return result;
      return [];
    } catch {
      return [];
    }
  },
};

export { fmtDuration };
