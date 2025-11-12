import os
import glob
import platform
import subprocess
from pathlib import Path


class FileService:
    """Handles file operations and search for JARVIS AI"""

    def __init__(self, config):
        """
        Initialize file service

        Args:
            config: Configuration object with search locations
        """
        self.config = config
        self.search_locations = config.search_locations
        self.last_search_results = []

    def search_files(self, query, file_type=None, max_results=50):
        """
        Search for files and folders in user directory

        Args:
            query (str): Search query
            file_type (str, optional): File extension to filter by
            max_results (int): Maximum number of results to return

        Returns:
            list: List of file/folder information dictionaries
        """
        results = []
        search_pattern = f"*{query}*"

        print(f"🔍 Searching for: {query} in user directory")

        try:
            for location in self.search_locations:
                if not os.path.exists(location):
                    continue

                print(f"  Scanning: {location}")

                if file_type:
                    pattern = os.path.join(location, '**', f"*{query}*.{file_type}")
                else:
                    pattern = os.path.join(location, '**', f"*{query}*")

                try:
                    matches = glob.glob(pattern, recursive=True)
                    for match in matches:
                        if len(results) >= max_results:
                            break

                        try:
                            if os.path.isfile(match):
                                results.append({
                                    'path': match,
                                    'name': os.path.basename(match),
                                    'size': os.path.getsize(match),
                                    'type': 'file',
                                    'parent': os.path.dirname(match),
                                    'extension': os.path.splitext(match)[1].lower()
                                })
                            elif os.path.isdir(match):
                                results.append({
                                    'path': match,
                                    'name': os.path.basename(match),
                                    'type': 'folder',
                                    'parent': os.path.dirname(match)
                                })
                        except Exception as e:
                            continue

                except Exception as e:
                    print(f"  Error scanning {location}: {e}")
                    continue

                if len(results) >= max_results:
                    break

            # Sort results: folders first, then alphabetically by name
            results.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))

            self.last_search_results = results
            print(f"✅ Found {len(results)} results")
            return results

        except Exception as e:
            print(f"File search error: {e}")
            return []

    def open_file(self, file_path):
        """
        Open a file or folder with default application

        Args:
            file_path (str): Path to file or folder to open

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ Path does not exist: {file_path}")
                return False

            if self.config.OS_TYPE == "Windows":
                os.startfile(file_path)
            elif self.config.OS_TYPE == "Darwin":
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])

            print(f"✅ Opened: {file_path}")
            return True
        except Exception as e:
            print(f"Open file error: {e}")
            return False

    def get_file_info(self, file_path):
        """
        Get detailed information about a file

        Args:
            file_path (str): Path to file

        Returns:
            dict: File information
        """
        try:
            if not os.path.exists(file_path):
                return None

            stat = os.stat(file_path)
            path_obj = Path(file_path)

            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'size_human': self._format_size(stat.st_size),
                'type': 'file' if os.path.isfile(file_path) else 'folder',
                'extension': path_obj.suffix.lower() if path_obj.suffix else None,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'parent': os.path.dirname(file_path),
                'absolute': os.path.abspath(file_path)
            }
        except Exception as e:
            print(f"File info error: {e}")
            return None

    def create_folder(self, folder_path):
        """
        Create a new folder

        Args:
            folder_path (str): Path for new folder

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"✅ Created folder: {folder_path}")
            return True
        except Exception as e:
            print(f"Create folder error: {e}")
            return False

    def delete_file(self, file_path):
        """
        Delete a file or folder

        Args:
            file_path (str): Path to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ Path does not exist: {file_path}")
                return False

            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)

            print(f"✅ Deleted: {file_path}")
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def copy_file(self, source, destination):
        """
        Copy a file or folder

        Args:
            source (str): Source path
            destination (str): Destination path

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import shutil

            if os.path.isfile(source):
                shutil.copy2(source, destination)
            elif os.path.isdir(source):
                shutil.copytree(source, destination)

            print(f"✅ Copied: {source} → {destination}")
            return True
        except Exception as e:
            print(f"Copy error: {e}")
            return False

    def move_file(self, source, destination):
        """
        Move a file or folder

        Args:
            source (str): Source path
            destination (str): Destination path

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import shutil
            shutil.move(source, destination)
            print(f"✅ Moved: {source} → {destination}")
            return True
        except Exception as e:
            print(f"Move error: {e}")
            return False

    def _format_size(self, size_bytes):
        """
        Format file size in human readable format

        Args:
            size_bytes (int): Size in bytes

        Returns:
            str: Formatted size string
        """
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f}{size_names[i]}"

    def get_last_search_results(self):
        """
        Get the results from the last search

        Returns:
            list: Last search results
        """
        return self.last_search_results

    def clear_search_results(self):
        """Clear the last search results"""
        self.last_search_results = []

    def search_by_extension(self, extension, location=None, max_results=50):
        """
        Search for files by extension

        Args:
            extension (str): File extension (with or without dot)
            location (str, optional): Specific location to search
            max_results (int): Maximum results

        Returns:
            list: Files with matching extension
        """
        if not extension.startswith('.'):
            extension = '.' + extension

        locations = [location] if location else self.search_locations
        results = []

        for loc in locations:
            if not os.path.exists(loc):
                continue

            pattern = os.path.join(loc, '**', f"*{extension}")
            matches = glob.glob(pattern, recursive=True)

            for match in matches:
                if len(results) >= max_results:
                    break
                if os.path.isfile(match):
                    results.append({
                        'path': match,
                        'name': os.path.basename(match),
                        'size': os.path.getsize(match),
                        'type': 'file',
                        'parent': os.path.dirname(match)
                    })

        return results