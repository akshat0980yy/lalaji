import time
import re
import json
import os
import subprocess
import webbrowser
from urllib.parse import quote
from datetime import datetime


class Helpers:
    """General utility functions for JARVIS AI"""

    @staticmethod
    def format_duration(seconds):
        """
        Format duration in seconds to human readable format

        Args:
            seconds (int or float): Duration in seconds

        Returns:
            str: Formatted duration string
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    @staticmethod
    def format_timestamp(timestamp=None):
        """
        Format timestamp to readable string

        Args:
            timestamp (float, optional): Unix timestamp. Defaults to now.

        Returns:
            str: Formatted timestamp
        """
        if timestamp is None:
            timestamp = time.time()
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitize filename for safe file system usage

        Args:
            filename (str): Original filename

        Returns:
            str: Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        # Ensure filename is not empty
        if not filename:
            filename = "untitled"

        return filename

    @staticmethod
    def extract_json_from_text(text):
        """
        Extract JSON object from text

        Args:
            text (str): Text containing JSON

        Returns:
            dict or None: Parsed JSON object or None if not found
        """
        try:
            # Look for JSON pattern
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            return None
        except (json.JSONDecodeError, AttributeError):
            return None

    @staticmethod
    def truncate_text(text, max_length=100, suffix="..."):
        """
        Truncate text to maximum length

        Args:
            text (str): Text to truncate
            max_length (int): Maximum length
            suffix (str): Suffix to add if truncated

        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def is_valid_url(url):
        """
        Check if string is a valid URL

        Args:
            url (str): URL string to check

        Returns:
            bool: True if valid URL
        """
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

    @staticmethod
    def normalize_text(text):
        """
        Normalize text by removing extra whitespace and special characters

        Args:
            text (str): Text to normalize

        Returns:
            str: Normalized text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove special quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        return text

    @staticmethod
    def get_file_extension_icon(extension):
        """
        Get icon representation for file extension

        Args:
            extension (str): File extension (with or without dot)

        Returns:
            str: Icon emoji
        """
        extension = extension.lower().lstrip('.')

        icon_map = {
            'pdf': '📄',
            'doc': '📝', 'docx': '📝',
            'xls': '📊', 'xlsx': '📊',
            'ppt': '📈', 'pptx': '📈',
            'txt': '📄', 'md': '📄',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵',
            'mp4': '🎬', 'avi': '🎬', 'mkv': '🎬',
            'zip': '🗜️', 'rar': '🗜️', '7z': '🗜️',
            'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨',
            'exe': '⚙️', 'msi': '⚙️',
            'folder': '📁'
        }

        return icon_map.get(extension, '📄')

    @staticmethod
    def safe_dict_get(dictionary, key, default=None):
        """
        Safely get value from dictionary with default

        Args:
            dictionary (dict): Dictionary to get value from
            key: Key to look for
            default: Default value if key not found

        Returns:
            Value or default
        """
        try:
            return dictionary.get(key, default) if dictionary else default
        except (AttributeError, TypeError):
            return default

    @staticmethod
    def execute_command_with_timeout(command, timeout=30):
        """
        Execute command with timeout

        Args:
            command (str or list): Command to execute
            timeout (int): Timeout in seconds

        Returns:
            dict: Result with success, stdout, stderr, timeout flag
        """
        try:
            result = subprocess.run(
                command,
                shell=isinstance(command, str),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'timeout': False
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'returncode': -1,
                'timeout': True
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'timeout': False
            }

    @staticmethod
    def retry_on_failure(func, max_retries=3, delay=1, exceptions=Exception):
        """
        Retry function execution on failure

        Args:
            func: Function to execute
            max_retries (int): Maximum number of retries
            delay (float): Delay between retries in seconds
            exceptions: Exception types to catch

        Returns:
            Function result or None if all retries failed
        """
        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                if attempt == max_retries:
                    print(f"❌ All {max_retries + 1} attempts failed. Last error: {e}")
                    return None
                print(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)

    @staticmethod
    def generate_unique_filename(base_path, extension=""):
        """
        Generate unique filename by adding number if file exists

        Args:
            base_path (str): Base file path (without extension)
            extension (str): File extension

        Returns:
            str: Unique file path
        """
        if extension and not extension.startswith('.'):
            extension = '.' + extension

        original_path = base_path + extension
        if not os.path.exists(original_path):
            return original_path

        counter = 1
        while True:
            new_path = f"{base_path}_{counter}{extension}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    @staticmethod
    def format_file_size(size_bytes):
        """
        Format file size in bytes to human readable format

        Args:
            size_bytes (int): Size in bytes

        Returns:
            str: Formatted file size
        """
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)

        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1

        return f"{size:.1f} {size_names[i]}"