#!/usr/bin/env python
# metadata_controller.py
import os
from model.metadata_reader import MetadataReader
from view.metadata_view import MetadataView
import argparse
import sys

class MetadataController:
    """
    Controller component for metadata operations
    Handles business logic and coordinates between model and view
    """
    
    def __init__(self):
        self.model = MetadataReader()
        self.view = MetadataView(self)
    
    def read_metadata(self, path):
        """
        Read metadata from file or directory
        
        Args:
            path (str): Path to file or directory
            
        Returns:
            list: List of metadata dictionaries
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        if os.path.isfile(path):
            metadata = self.model.read_metadata(path)
            return [metadata]
        elif os.path.isdir(path):
            return self.model.read_directory_metadata(path)
        else:
            raise ValueError(f"Invalid path: {path}")
    
    def export_metadata(self, metadata_list, output_path):
        """
        Export metadata to JSON file
        
        Args:
            metadata_list (list): List of metadata dictionaries
            output_path (str): Path to save the JSON file
        """
        self.model.export_metadata_to_json(metadata_list, output_path)
    
    def format_duration(self, seconds):
        """
        Format duration from seconds to MM:SS format
        
        Args:
            seconds (float): Duration in seconds
            
        Returns:
            str: Formatted duration (MM:SS)
        """
        return self.model.format_duration(seconds)
    
    def get_supported_formats(self):
        """
        Get list of supported audio formats
        
        Returns:
            list: List of supported file extensions
        """
        return self.model.supported_formats
    
    def run_gui(self):
        """
        Start the GUI application
        """
        try:
            root = self.view.create_gui()
            self.view.run()
        except ImportError as e:
            if "tkinter" in str(e).lower():
                print("Error: tkinter not available. GUI mode not supported.")
                print("Try using CLI mode instead.")
            else:
                raise e
    
    def run_cli(self, args=None):
        """
        Run the command-line interface
        
        Args:
            args: Command line arguments (optional)
        """
        if args is None:
            args = self._parse_cli_arguments()
        
        try:
            metadata_list = self.read_metadata(args.path)
            
            if args.format == 'detailed':
                for metadata in metadata_list:
                    self.view.print_metadata(metadata)
            else:
                self.view.print_table_header()
                for metadata in metadata_list:
                    self.view.print_table_row(metadata)
            
            if args.export:
                self.export_metadata(metadata_list, args.export)
                print(f"\nMetadata exported to: {args.export}")
            
            if len(metadata_list) > 1:
                print(f"\nTotal files processed: {len(metadata_list)}")
        
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def _parse_cli_arguments(self):
        """
        Parse command line arguments
        
        Returns:
            argparse.Namespace: Parsed arguments
        """
        parser = argparse.ArgumentParser(description='Read metadata from audio files')
        parser.add_argument('path', help='Path to audio file or directory')
        parser.add_argument('--export', '-e', help='Export metadata to JSON file')
        parser.add_argument('--format', '-f', choices=['table', 'detailed'], 
                           default='detailed', help='Output format')
        parser.add_argument('--gui', '-g', action='store_true', help='Launch GUI mode')
        
        return parser.parse_args()
    
    def read_single_file(self, file_path):
        """
        Read metadata from a single file
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            dict: Metadata dictionary
        """
        return self.model.read_metadata(file_path)
    
    def validate_file(self, file_path):
        """
        Validate if file is supported audio format
        
        Args:
            file_path (str): Path to file
            
        Returns:
            bool: True if file is supported, False otherwise
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.model.supported_formats

def main():
    """
    Main entry point for the metadata application
    Supports both CLI and GUI modes
    """
    controller = MetadataController()
    
    # Check if running from command line with arguments
    if len(sys.argv) > 1:
        args = controller._parse_cli_arguments()
        if args.gui:
            controller.run_gui()
        else:
            controller.run_cli(args)
    else:
        # No arguments provided - show help and ask for mode
        print("Ekho Metadata Reader")
        print("=" * 30)
        print("Usage:")
        print("  GUI Mode: python metadata_controller.py --gui")
        print("  CLI Mode: python metadata_controller.py <path> [options]")
        print("\nExamples:")
        print("  python metadata_controller.py --gui")
        print("  python metadata_controller.py 'song.mp3'")
        print("  python metadata_controller.py 'music_folder' --format table")
        print("  python metadata_controller.py 'downloads' --export metadata.json")
        print("\nChoose mode:")
        print("1. GUI Mode")
        print("2. CLI Mode (you'll need to provide a file/folder path)")
        
        try:
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == '1':
                controller.run_gui()
            elif choice == '2':
                path = input("Enter file or folder path: ").strip().strip('"\'')
                if path:
                    sys.argv = ['metadata_controller.py', path]
                    controller.run_cli()
                else:
                    print("No path provided. Exiting.")
            else:
                print("Invalid choice. Exiting.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")

if __name__ == "__main__":
    main()