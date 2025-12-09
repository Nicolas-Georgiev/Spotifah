# metadata_view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

class MetadataView:
    """
    View component for metadata reading functionality
    Handles all user interface interactions for metadata operations
    """
    
    def __init__(self, controller):
        self.controller = controller
        self.root = None
        self.current_metadata = []
        
    def create_gui(self):
        """Create and setup the graphical user interface"""
        self.root = tk.Tk()
        self.root.title("Audio Metadata Reader")
        self.root.geometry("800x600")
        
        self.setup_ui()
        return self.root
    
    def setup_ui(self):
        """Setup the user interface components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select Audio File or Directory", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(file_frame, textvariable=self.path_var, width=60)
        path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text="Browse File", 
                  command=self.browse_file).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(file_frame, text="Browse Folder", 
                  command=self.browse_folder).grid(row=0, column=2, padx=(5, 0))
        
        file_frame.columnconfigure(0, weight=1)
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(button_frame, text="Read Metadata", 
                  command=self.read_metadata).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Export to JSON", 
                  command=self.export_metadata).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_results).grid(row=0, column=2, padx=(5, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Metadata Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview for displaying metadata
        columns = ('File', 'Title', 'Artist', 'Album', 'Duration', 'Format')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Define column headings and widths
        self.tree.heading('File', text='File Name')
        self.tree.heading('Title', text='Title')
        self.tree.heading('Artist', text='Artist')
        self.tree.heading('Album', text='Album')
        self.tree.heading('Duration', text='Duration')
        self.tree.heading('Format', text='Format')
        
        self.tree.column('File', width=150)
        self.tree.column('Title', width=150)
        self.tree.column('Artist', width=120)
        self.tree.column('Album', width=120)
        self.tree.column('Duration', width=80)
        self.tree.column('Format', width=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click to show detailed info
        self.tree.bind('<Double-1>', self.show_detailed_info)
        
        # Configure grid weights
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def browse_file(self):
        """Browse for a single audio file"""
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.mp4 *.m4a *.flac *.ogg *.wav"),
                ("MP3 Files", "*.mp3"),
                ("MP4/M4A Files", "*.mp4 *.m4a"),
                ("FLAC Files", "*.flac"),
                ("OGG Files", "*.ogg"),
                ("WAV Files", "*.wav"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.path_var.set(filename)
    
    def browse_folder(self):
        """Browse for a directory containing audio files"""
        dirname = filedialog.askdirectory(title="Select Directory with Audio Files")
        if dirname:
            self.path_var.set(dirname)
    
    def read_metadata(self):
        """Request metadata reading from controller"""
        path = self.path_var.get()
        if not path:
            self.show_error("Please select a file or directory first.")
            return
        
        self.clear_results()
        self.status_var.set("Reading metadata...")
        
        # Run in a separate thread to avoid blocking the UI
        thread = threading.Thread(target=self._read_metadata_thread, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _read_metadata_thread(self, path):
        """Thread function for reading metadata"""
        try:
            self.current_metadata = self.controller.read_metadata(path)
            self.root.after(0, self._update_results)
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))
            self.root.after(0, lambda: self.status_var.set("Error reading metadata"))
    
    def _update_results(self):
        """Update the results tree with metadata"""
        for metadata in self.current_metadata:
            file_name = metadata.get('file_name', 'Unknown')
            title = metadata.get('title', 'Unknown')
            artist = metadata.get('artist', 'Unknown')
            album = metadata.get('album', 'Unknown')
            duration = self.controller.format_duration(metadata.get('duration'))
            format_type = metadata.get('format', 'Unknown')
            
            self.tree.insert('', 'end', values=(
                file_name, title, artist, album, duration, format_type
            ))
        
        count = len(self.current_metadata)
        self.status_var.set(f"Loaded {count} audio file{'s' if count != 1 else ''}")
    
    def show_detailed_info(self, event):
        """Show detailed metadata information in a popup"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        file_name = item['values'][0]
        
        # Find the metadata for this file
        metadata = None
        for m in self.current_metadata:
            if m.get('file_name') == file_name:
                metadata = m
                break
        
        if metadata:
            self._show_metadata_popup(metadata)
    
    def _show_metadata_popup(self, metadata):
        """Show detailed metadata in a popup window"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Detailed Metadata - {metadata.get('file_name', 'Unknown')}")
        popup.geometry("500x400")
        
        # Create text widget with scrollbar
        frame = ttk.Frame(popup, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Format metadata for display
        details = (
            f"File Information:\n"
            f"File Name: {metadata.get('file_name', 'Unknown')}\n"
            f"File Path: {metadata.get('file_path', 'Unknown')}\n"
            f"File Size: {round(metadata.get('file_size', 0) / 1024 / 1024, 2)} MB\n"
            f"Format: {metadata.get('format', 'Unknown')}\n\n"
            f"Audio Metadata:\n"
            f"Title: {metadata.get('title', 'Unknown')}\n"
            f"Artist: {metadata.get('artist', 'Unknown')}\n"
            f"Album: {metadata.get('album', 'Unknown')}\n"
            f"Genre: {metadata.get('genre', 'Unknown')}\n\n"
            f"Technical Information:\n"
            f"Duration: {self.controller.format_duration(metadata.get('duration'))}"
        )
        
        text_widget.insert(tk.END, details)
        text_widget.configure(state='disabled')
        
        # Close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
    
    def export_metadata(self):
        """Export current metadata to JSON file"""
        if not self.current_metadata:
            self.show_error("No metadata to export. Please read metadata first.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Metadata",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.controller.export_metadata(self.current_metadata, filename)
                self.show_info(f"Metadata exported to: {filename}")
                self.status_var.set(f"Exported to {filename.split('/')[-1]}")
            except Exception as e:
                self.show_error(f"Failed to export metadata: {str(e)}")
    
    def clear_results(self):
        """Clear the results tree"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_metadata = []
        self.status_var.set("Ready")
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
    
    def show_info(self, message):
        """Show info message"""
        messagebox.showinfo("Success", message)
    
    def print_table_header(self):
        """Print table header for console output"""
        header = f"{'Title':<30} {'Artist':<20} {'Album':<20} {'Duration':<8} {'Format':<6}"
        print(header)
        print("-" * len(header))
    
    def print_table_row(self, metadata):
        """Print a single row in table format"""
        title = (metadata.get('title') or 'Unknown')[:29]
        artist = (metadata.get('artist') or 'Unknown')[:19]
        album = (metadata.get('album') or 'Unknown')[:19]
        duration = self.controller.format_duration(metadata.get('duration'))
        format_type = metadata.get('format', 'Unknown')
        
        row = f"{title:<30} {artist:<20} {album:<20} {duration:<8} {format_type:<6}"
        print(row)
    
    def print_metadata(self, metadata):
        """Print metadata in a formatted way for console"""
        print("=" * 50)
        print(f"File: {metadata.get('file_name', 'Unknown')}")
        print(f"Format: {metadata.get('format', 'Unknown')}")
        print(f"Title: {metadata.get('title', 'Unknown')}")
        print(f"Artist: {metadata.get('artist', 'Unknown')}")
        print(f"Album: {metadata.get('album', 'Unknown')}")
        print(f"Genre: {metadata.get('genre', 'Unknown')}")
        print(f"Duration: {self.controller.format_duration(metadata.get('duration'))}")
        print(f"File Size: {round(metadata.get('file_size', 0) / 1024 / 1024, 2)} MB")
        print("=" * 50)
    
    def run(self):
        """Run the GUI application"""
        if self.root:
            self.root.mainloop()