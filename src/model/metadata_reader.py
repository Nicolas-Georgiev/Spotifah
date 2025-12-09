# metadata_reader.py
import os
from mutagen import File
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TRCK
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
import json

class MetadataReader:
    """
    Class to read and extract metadata from various audio file formats
    Supports: MP3, MP4/M4A, FLAC, OGG, WAV
    """
    
    def __init__(self):
        self.supported_formats = ['.mp3', '.mp4', '.m4a', '.flac', '.ogg', '.wav']
    
    def read_metadata(self, file_path):
        """
        Read metadata from an audio file
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            dict: Dictionary containing metadata information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        try:
            audio_file = File(file_path)
            if audio_file is None:
                raise ValueError(f"Could not read audio file: {file_path}")
            
            metadata = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'format': file_ext[1:].upper(),
                'title': self._get_tag(audio_file, 'TIT2', 'TITLE', '\xa9nam'),
                'artist': self._get_tag(audio_file, 'TPE1', 'ARTIST', '\xa9ART'),
                'album': self._get_tag(audio_file, 'TALB', 'ALBUM', '\xa9alb'),
                'genre': self._get_tag(audio_file, 'TCON', 'GENRE', '\xa9gen'),
                'source': self._get_comments(audio_file),
                'duration': self._get_duration(audio_file)
            }
            
            return metadata
            
        except Exception as e:
            raise Exception(f"Error reading metadata from {file_path}: {str(e)}")
    
    def _get_tag(self, audio_file, id3_tag, vorbis_tag, mp4_tag):
        """
        Get a specific tag from the audio file, handling different formats
        
        Args:
            audio_file: The loaded audio file object
            id3_tag: ID3 tag name (for MP3)
            vorbis_tag: Vorbis comment tag name (for FLAC/OGG)
            mp4_tag: MP4 tag name (for MP4/M4A)
            
        Returns:
            str: Tag value or None if not found
        """
        try:
            # MP3 files (ID3 tags)
            if isinstance(audio_file, MP3):
                if id3_tag in audio_file:
                    return str(audio_file[id3_tag])
            
            # MP4/M4A files
            elif isinstance(audio_file, MP4):
                if mp4_tag in audio_file:
                    value = audio_file[mp4_tag]
                    if isinstance(value, list) and len(value) > 0:
                        return str(value[0])
                    return str(value)
            
            # FLAC/OGG files (Vorbis comments)
            elif isinstance(audio_file, (FLAC, OggVorbis)):
                if vorbis_tag in audio_file:
                    value = audio_file[vorbis_tag]
                    if isinstance(value, list) and len(value) > 0:
                        return value[0]
                    return str(value)
            
            # Generic approach for other formats
            else:
                for tag in [vorbis_tag, id3_tag, mp4_tag]:
                    if tag in audio_file:
                        value = audio_file[tag]
                        if isinstance(value, list) and len(value) > 0:
                            return str(value[0])
                        return str(value)
            
        except Exception:
            pass
        
        return None
    
    def _get_duration(self, audio_file):
        """
        Get duration of the audio file in seconds
        
        Args:
            audio_file: The loaded audio file object
            
        Returns:
            float: Duration in seconds or None if not available
        """
        try:
            if hasattr(audio_file, 'info') and hasattr(audio_file.info, 'length'):
                return round(audio_file.info.length, 2)
        except Exception:
            pass
        
        return None
    
    def _get_comments(self, audio_file):
        """Extract comment tags from MP3 file"""
        try:
            if hasattr(audio_file, 'tags') and audio_file.tags:
                # Try to get COMM tags (comments)
                comm_tags = audio_file.tags.getall('COMM')
                if comm_tags:
                    # Return the text of the first comment
                    for comm in comm_tags:
                        if comm.text and len(comm.text) > 0:
                            comment_text = str(comm.text[0])
                            # If it starts with "Origen:", extract just the source
                            if comment_text.startswith('Origen: '):
                                return comment_text.replace('Origen: ', '').lower()
                            return comment_text
            
            # MP4/M4A files
            if isinstance(audio_file, MP4):
                if '\xa9cmt' in audio_file:
                    value = audio_file['\xa9cmt']
                    if isinstance(value, list) and len(value) > 0:
                        return str(value[0])
                    return str(value)
            
            # FLAC/OGG files (Vorbis comments)
            elif isinstance(audio_file, (FLAC, OggVorbis)):
                if 'COMMENT' in audio_file:
                    value = audio_file['COMMENT']
                    if isinstance(value, list) and len(value) > 0:
                        return value[0]
                    return str(value)
            
            return None
        except Exception as e:
            print(f"Error extracting comments: {e}")
            return None
            
        except Exception:
            pass
        
        return None
    
    def format_duration(self, seconds):
        """
        Format duration from seconds to MM:SS format
        
        Args:
            seconds (float): Duration in seconds
            
        Returns:
            str: Formatted duration (MM:SS)
        """
        if seconds is None:
            return "Unknown"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def read_directory_metadata(self, directory_path):
        """
        Read metadata from all audio files in a directory
        
        Args:
            directory_path (str): Path to the directory
            
        Returns:
            list: List of metadata dictionaries for each audio file
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        metadata_list = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext in self.supported_formats:
                    try:
                        metadata = self.read_metadata(file_path)
                        metadata_list.append(metadata)
                    except Exception as e:
                        print(f"Error reading {filename}: {str(e)}")
        
        return metadata_list
    
    def export_metadata_to_json(self, metadata_list, output_path):
        """
        Export metadata list to a JSON file
        
        Args:
            metadata_list (list): List of metadata dictionaries
            output_path (str): Path to save the JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_list, f, indent=2, ensure_ascii=False)
            print(f"Metadata exported to: {output_path}")
        except Exception as e:
            print(f"Error exporting metadata: {str(e)}")
    
    def print_metadata(self, metadata):
        """
        Print metadata in a formatted way
        
        Args:
            metadata (dict): Metadata dictionary
        """
        print("=" * 50)
        print(f"File: {metadata.get('file_name', 'Unknown')}")
        print(f"Format: {metadata.get('format', 'Unknown')}")
        print(f"Title: {metadata.get('title', 'Unknown')}")
        print(f"Artist: {metadata.get('artist', 'Unknown')}")
        print(f"Album: {metadata.get('album', 'Unknown')}")
        print(f"Genre: {metadata.get('genre', 'Unknown')}")
        print(f"Duration: {self.format_duration(metadata.get('duration'))}")
        print(f"File Size: {round(metadata.get('file_size', 0) / 1024 / 1024, 2)} MB")
        print("=" * 50)

# Example usage
if __name__ == "__main__":
    reader = MetadataReader()
    
    # Example: Read metadata from a single file
    try:
        file_path = "path/to/your/audio/file.mp3"
        metadata = reader.read_metadata(file_path)
        reader.print_metadata(metadata)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example: Read metadata from all files in a directory
    try:
        directory_path = "path/to/your/music/directory"
        metadata_list = reader.read_directory_metadata(directory_path)
        
        for metadata in metadata_list:
            reader.print_metadata(metadata)
        
        # Export to JSON
        reader.export_metadata_to_json(metadata_list, "metadata_export.json")
        
    except Exception as e:
        print(f"Error: {e}")