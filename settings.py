# settings.py
import os
import json
from pathlib import Path

class Settings:
    def __init__(self):
        # Define default settings
        self.default_settings = {
            'recent_files': [],
            'default_output_dir': str(Path.home() / "Documents"),
            'default_image_output_dir': str(Path.home() / "Pictures"),
            'max_recent_files': 10,
            'theme': 'default',
            'confirm_overwrite': True,
            'remember_last_directory': True,
            'last_directories': {
                'pdf_input': '',
                'pdf_output': '',
                'image_input': '',
                'image_output': '',
            }
        }
        
        # Set up paths
        self.app_dir = Path.home() / ".p2i"
        self.settings_file = self.app_dir / "settings.json"
        
        # Load or create settings
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file or create default"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            else:
                # Create app directory if it doesn't exist
                os.makedirs(self.app_dir, exist_ok=True)
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        except Exception:
            # If there's any error, return defaults
            return self.default_settings.copy()
    
    def save_settings(self, settings=None):
        """Save settings to file"""
        if settings is None:
            settings = self.settings
        
        try:
            os.makedirs(self.app_dir, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def add_recent_file(self, file_path):
        """Add a file to recent files list"""
        if not file_path:
            return
            
        # Convert to string if it's a Path
        file_path = str(file_path)
        
        # Get recent files list
        recent_files = self.settings.get('recent_files', [])
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
            
        # Add to beginning of list
        recent_files.insert(0, file_path)
        
        # Trim list if needed
        max_recent = self.settings.get('max_recent_files', 10)
        if len(recent_files) > max_recent:
            recent_files = recent_files[:max_recent]
            
        # Update settings
        self.settings['recent_files'] = recent_files
        self.save_settings()
    
    def get_recent_files(self):
        """Get list of recent files (that still exist)"""
        recent_files = self.settings.get('recent_files', [])
        
        # Filter out files that no longer exist
        return [f for f in recent_files if os.path.exists(f)]
    
    def update_last_directory(self, category, directory):
        """Update last used directory for a category"""
        if not directory:
            return
            
        # Convert to string if it's a Path
        directory = str(directory)
        
        # Ensure the last_directories dict exists
        if 'last_directories' not in self.settings:
            self.settings['last_directories'] = {}
            
        # Update the directory
        self.settings['last_directories'][category] = directory
        self.save_settings()
    
    def get_last_directory(self, category):
        """Get last used directory for a category"""
        if ('last_directories' in self.settings and
            category in self.settings['last_directories'] and
            os.path.exists(self.settings['last_directories'][category])):
            
            return self.settings['last_directories'][category]
        
        # Return default if no valid last directory
        if 'pdf' in category:
            return self.settings.get('default_output_dir', str(Path.home() / "Documents"))
        else:
            return self.settings.get('default_image_output_dir', str(Path.home() / "Pictures"))