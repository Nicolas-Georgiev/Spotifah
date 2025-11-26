# run_metadata.py
"""
Ekho - Metadata Application Runner
Simple console interface to browse and analyze music metadata
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controller.metadata_controller import MetadataController

def show_music_library():
    """
    Show all songs in data/music folder and let user select one to view metadata
    """
    print("🎵 EKHO - Music Library Metadata Viewer")
    print("=" * 50)
    
    # Path to music folder
    music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "music")
    
    if not os.path.exists(music_folder):
        print(f"❌ Music folder not found: {music_folder}")
        print("Please make sure you have music files in the data/music directory.")
        return
    
    controller = MetadataController()
    
    try:
        # Get all audio files in music folder
        audio_files = []
        supported_formats = controller.get_supported_formats()
        
        for file in os.listdir(music_folder):
            file_path = os.path.join(music_folder, file)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in supported_formats:
                    audio_files.append(file)
        
        if not audio_files:
            print("❌ No audio files found in the music folder.")
            print(f"Supported formats: {', '.join(supported_formats)}")
            return
        
        while True:
            # Display list of songs
            print(f"\n📁 Found {len(audio_files)} songs in your library:")
            print("-" * 50)
            
            for i, song in enumerate(audio_files, 1):
                # Show just the filename without extension for cleaner display
                display_name = os.path.splitext(song)[0]
                print(f"{i:2d}. {display_name}")
            
            print("\n0. Exit")
            print("-" * 50)
            
            try:
                choice = input("\nSelect a song to view metadata (0 to exit): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                
                song_index = int(choice) - 1
                
                if 0 <= song_index < len(audio_files):
                    selected_song = audio_files[song_index]
                    song_path = os.path.join(music_folder, selected_song)
                    
                    print(f"\n🎵 Analyzing: {selected_song}")
                    print("=" * 60)
                    
                    # Read and display metadata
                    metadata_list = controller.read_metadata(song_path)
                    if metadata_list:
                        metadata = metadata_list[0]
                        display_song_metadata(metadata, controller)
                    else:
                        print("❌ Could not read metadata from this file.")
                    
                    input("\nPress Enter to continue...")
                
                else:
                    print("❌ Invalid selection. Please try again.")
            
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    except Exception as e:
        print(f"❌ Error reading music library: {str(e)}")

def display_song_metadata(metadata, controller):
    """
    Display song metadata in a clean, organized format
    """
    print("📋 METADATA INFORMATION")
    print("-" * 40)
    
    # Basic info
    print(f"🎵 Title:     {metadata.get('title', 'Unknown')}")
    print(f"👤 Artist:    {metadata.get('artist', 'Unknown')}")
    print(f"💿 Album:     {metadata.get('album', 'Unknown')}")
    print(f"🎭 Genre:     {metadata.get('genre', 'Unknown')}")
    
    # Source information (from source field)
    source = metadata.get('source', 'Unknown')
    
    # Capitalize first letter for display
    if source and source != 'Unknown':
        source = source.capitalize()
    
    print(f"📍 Source:    {source}")
    
    print("-" * 40)
    
    # Technical info
    duration = controller.format_duration(metadata.get('duration'))
    file_size_mb = round(metadata.get('file_size', 0) / 1024 / 1024, 2)
    
    print(f"⏱️ Duration:   {duration}")
    print(f"💾 Size:      {file_size_mb} MB")
    print(f"📁 Format:    {metadata.get('format', 'Unknown')}")
    
    print("-" * 40)
    print(f"📂 File:      {metadata.get('file_name', 'Unknown')}")

def quick_library_overview():
    """
    Show a quick overview of the music library
    """
    music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "music")
    
    if not os.path.exists(music_folder):
        print("❌ Music folder not found.")
        return
    
    controller = MetadataController()
    
    try:
        metadata_list = controller.read_metadata(music_folder)
        
        if not metadata_list:
            print("❌ No audio files found.")
            return
        
        print(f"\n📊 LIBRARY OVERVIEW")
        print("=" * 50)
        print(f"Total songs: {len(metadata_list)}")
        
        # Count by source
        sources = {}
        total_duration = 0
        
        for metadata in metadata_list:
            # Check source field for source
            comment = metadata.get('source', '')
            source = 'Unknown/Local'
            
            if comment:
                comment_lower = comment.lower()
                if 'youtube' in comment_lower:
                    source = 'YouTube'
                elif 'spotify' in comment_lower:
                    source = 'Spotify'
                elif 'soundcloud' in comment_lower:
                    source = 'SoundCloud'
                elif 'bandcamp' in comment_lower:
                    source = 'Bandcamp'
                elif 'apple music' in comment_lower or 'itunes' in comment_lower:
                    source = 'Apple Music'
                else:
                    source = 'Other'
            
            sources[source] = sources.get(source, 0) + 1
            
            duration = metadata.get('duration', 0) or 0
            total_duration += duration
        
        print(f"Total duration: {controller.format_duration(total_duration)}")
        print("\nSources:")
        for source, count in sources.items():
            print(f"  {source}: {count} songs")
        
        print("=" * 50)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """
    Main menu for metadata viewer
    """
    while True:
        try:
            print("\n🎵 EKHO - Metadata Viewer")
            print("=" * 30)
            print("1. Browse music library")
            print("2. Library overview")
            print("3. Exit")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == "1":
                show_music_library()
            elif choice == "2":
                quick_library_overview()
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()