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
  cover_url: string;
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

interface UrlTypeResult {
  platform: string | null;
  is_playlist: boolean;
}

interface ImportPlaylistResult {
  ok: boolean;
  data?: { task_id: string; platform: string };
  error?: string;
}

interface ImportProgress {
  status: "starting" | "running" | "done" | "error";
  platform: string;
  current: number;
  total: number;
  playlist_name: string;
  playlist_id: number | null;
  error: string | null;
  log: string;
}

export interface TrackPreview {
  title: string;
  artist: string;
  duration: number;
}

export interface AlbumPreviewData {
  platform: string;
  name: string;
  artist: string;
  year: number | null;
  cover_url: string;
  is_album: boolean;
  total_tracks: number;
  tracks: TrackPreview[];
}

interface AlbumPreviewResult {
  ok: boolean;
  data?: AlbumPreviewData;
  error?: string;
}

function getApi() {
  try {
    return (window as any)?.pywebview?.api ?? null;
  } catch {
    return null;
  }
}

function fmtDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export const bridge = {
  async getPlaylists(): Promise<Playlist[]> {
    const api = getApi();
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
    const api = getApi();
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
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.convert_youtube(url);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error en conversión" };
    }
  },

  async convertSpotify(url: string): Promise<ConvertResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.convert_spotify(url);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error en conversión" };
    }
  },

  async playSong(songId: string): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.play_song(songId);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al reproducir" };
    }
  },

  async pauseSong(): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: true, data: { message: "Simulado" } };
    try {
      return await api.pause_song();
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async resumeSong(): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: true, data: { message: "Simulado" } };
    try {
      return await api.resume_song();
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async stopSong(): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: true, data: { message: "Simulado" } };
    try {
      return await api.stop_song();
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async seekSong(position: number): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.seek_song(position);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al buscar" };
    }
  },

  async nextSong(): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: true, data: { message: "Simulado" } };
    try {
      return await api.next_song();
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async prevSong(): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: true, data: { message: "Simulado" } };
    try {
      return await api.prev_song();
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async getSettings(): Promise<Record<string, any>> {
    const api = getApi();
    if (!api) return { volume: 80, theme: "dark", download_quality: "192" };
    return await api.get_settings();
  },

  async updateSettings(data: Record<string, any>): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: true, data: { message: "Simulado" } };
    try {
      return await api.update_settings(data);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async getSystemStatus(): Promise<SystemStatus> {
    const api = getApi();
    if (!api) return { dependencies: {}, ffmpeg: false, music_count: 0 };
    return await api.get_system_status();
  },

  async addSongToPlaylist(playlistId: string, songId: string): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.add_song_to_playlist(playlistId, songId);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async removeSongFromPlaylist(playlistId: string, songId: string): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.remove_song_from_playlist(playlistId, songId);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error" };
    }
  },

  async convertSoundcloud(url: string): Promise<ConvertResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.convert_soundcloud(url);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error en conversión" };
    }
  },

  async detectUrlType(url: string): Promise<UrlTypeResult> {
    const api = getApi();
    if (!api) return { platform: null, is_playlist: false };
    try {
      return await api.detect_url_type(url);
    } catch {
      return { platform: null, is_playlist: false };
    }
  },

  async importPlaylist(url: string): Promise<ImportPlaylistResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.import_playlist(url);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al importar playlist" };
    }
  },

  async getAlbumPreview(url: string): Promise<AlbumPreviewResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.get_album_preview(url);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al obtener vista previa" };
    }
  },

  async importAlbum(url: string): Promise<ImportPlaylistResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.import_album(url);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al importar álbum" };
    }
  },

  async getImportProgress(taskId: string): Promise<{ ok: boolean; data?: ImportProgress; error?: string }> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.get_import_progress(taskId);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al obtener progreso" };
    }
  },

  async createPlaylist(name: string, description: string = ""): Promise<CreatePlaylistResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.create_playlist(name, description);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al crear playlist" };
    }
  },

  async deletePlaylist(playlistId: string): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.delete_playlist(playlistId);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al eliminar" };
    }
  },

  async renamePlaylist(playlistId: string, name: string): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      return await api.rename_playlist(playlistId, name);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al renombrar" };
    }
  },

  async searchSongs(query: string): Promise<Song[]> {
    const api = getApi();
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
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible", favorite: false };
    try {
      return await api.toggle_favorite(songId);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error", favorite: false };
    }
  },

  async getNowPlaying(): Promise<NowPlayingResult> {
    const api = getApi();
    if (!api) return { ok: true, data: null };
    try {
      return await api.get_now_playing();
    } catch {
      return { ok: true, data: null };
    }
  },

  async getPlaybackPosition(): Promise<PlaybackPosition> {
    const api = getApi();
    if (!api) return { position: 0, is_playing: false };
    try {
      const result = await api.get_playback_position();
      return result.data || { position: 0, is_playing: false };
    } catch {
      return { position: 0, is_playing: false };
    }
  },

  async setVolume(volume: number): Promise<{ ok: boolean; data?: VolumeData; error?: string }> {
    const api = getApi();
    if (!api) return { ok: true, data: { volume } };
    try {
      return await api.set_volume(volume);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al ajustar volumen" };
    }
  },

  async getVolume(): Promise<{ ok: boolean; data?: VolumeData; error?: string }> {
    const api = getApi();
        if (!api) return { ok: true, data: { volume: 100 } };
    try {
      return await api.get_volume();
    } catch {
      return { ok: true, data: { volume: 100 } };
    }
  },

  async getRecentlyPlayed(limit: number = 10): Promise<Song[]> {
    const api = getApi();
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
