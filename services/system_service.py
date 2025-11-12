import os
import sys
import platform
import subprocess
import time

# Windows-specific imports
if platform.system() == "Windows":
    import win32com.client
    import winreg
    import win32api
    import win32con

from utils.windows_utils import WindowsUtils


class SystemService:
    """Handles system control and Windows integration for JARVIS AI"""

    def __init__(self, config):
        """
        Initialize system service

        Args:
            config: Configuration object
        """
        self.config = config
        self.os_type = config.OS_TYPE
        self.installed_apps_cache = {}
        self.windows_utils = WindowsUtils() if self.os_type == "Windows" else None

        # Initialize installed apps cache for Windows
        if self.os_type == "Windows":
            print("🔍 Indexing installed applications...")
            self.installed_apps_cache = self.get_windows_installed_apps()
            print(f"✅ Indexed {len(self.installed_apps_cache)} applications")

    def get_windows_installed_apps(self):
        """
        Get all installed Windows applications using registry and shell

        Returns:
            dict: Dictionary of installed applications
        """
        apps = {}

        if self.os_type != "Windows":
            return apps

        if not self.windows_utils:
            return apps

        try:
            # Method 1: Windows Registry - Uninstall keys
            registry_apps = self.windows_utils.scan_registry_for_apps()
            apps.update(registry_apps)

            # Method 2: Start Menu shortcuts
            start_menu_apps = self.windows_utils.scan_start_menu_for_apps()
            apps.update(start_menu_apps)

        except Exception as e:
            print(f"Error indexing apps: {e}")

        return apps

    def find_app_path(self, app_name):
        """
        Find application path using cached data

        Args:
            app_name (str): Name of application to find

        Returns:
            str: Path to application executable or directory
        """
        if self.os_type != "Windows":
            return None

        app_lower = app_name.lower()

        # Direct match
        if app_lower in self.installed_apps_cache:
            return self.installed_apps_cache[app_lower]['path']

        # Partial match in key
        for key, value in self.installed_apps_cache.items():
            if app_lower in key or key in app_lower:
                return value['path']

        # Partial match in display name
        for key, value in self.installed_apps_cache.items():
            if app_lower in value['name'].lower() or value['name'].lower() in app_lower:
                return value['path']

        return None

    def smart_find_and_open_app(self, app_name, executable_hints=None):
        """
        Enhanced app opening with multiple strategies

        Args:
            app_name (str): Name of application to open
            executable_hints (list, optional): List of possible executable names

        Returns:
            bool: True if successful, False otherwise
        """
        if executable_hints is None:
            executable_hints = []

        print(f"🔍 Searching for: {app_name}")

        if self.os_type == "Windows":
            # Strategy 1: Use cached path
            app_path = self.find_app_path(app_name)
            if app_path and os.path.exists(app_path):
                try:
                    if os.path.isfile(app_path):
                        os.startfile(app_path)
                    else:
                        # Look for executable in directory
                        for file in os.listdir(app_path):
                            if file.endswith('.exe'):
                                os.startfile(os.path.join(app_path, file))
                                break
                    print(f"✅ Opened from cache: {app_path}")
                    return True
                except Exception as e:
                    print(f"Cache open error: {e}")

            # Strategy 2: Try executable hints
            for hint in executable_hints:
                try:
                    subprocess.Popen(hint, shell=True)
                    time.sleep(1)
                    print(f"✅ Opened via hint: {hint}")
                    return True
                except:
                    pass

            # Strategy 3: Use WScript shell
            if self.windows_utils:
                shell = win32com.client.Dispatch("WScript.Shell")
                for hint in [app_name] + executable_hints:
                    try:
                        shell.Run(hint)
                        print(f"✅ Opened via shell: {hint}")
                        return True
                    except:
                        pass

        elif self.os_type == "Darwin":
            # macOS
            for hint in [app_name] + executable_hints:
                try:
                    subprocess.run(['open', '-a', hint], check=True)
                    return True
                except:
                    continue

        elif self.os_type == "Linux":
            # Linux
            for hint in [app_name] + executable_hints:
                try:
                    subprocess.Popen([hint])
                    return True
                except:
                    continue

        print(f"❌ Could not find or open: {app_name}")
        return False

    def open_folder(self, folder_name, folder_paths=None):
        """
        Open folder with enhanced path detection

        Args:
            folder_name (str): Name of folder to open
            folder_paths (list, optional): List of possible folder paths

        Returns:
            bool: True if successful, False otherwise
        """
        if folder_paths is None:
            folder_paths = []

        print(f"📂 Opening folder: {folder_name}")

        if self.os_type == "Windows":
            # Try common Windows folders
            user_profile = os.environ.get('USERPROFILE', '')
            common_folders = {
                'downloads': os.path.join(user_profile, 'Downloads'),
                'documents': os.path.join(user_profile, 'Documents'),
                'desktop': os.path.join(user_profile, 'Desktop'),
                'pictures': os.path.join(user_profile, 'Pictures'),
                'music': os.path.join(user_profile, 'Music'),
                'videos': os.path.join(user_profile, 'Videos'),
                'one_drive': os.path.join(user_profile, 'OneDrive'),
            }

            folder_lower = folder_name.lower()

            # Try exact match in common folders
            if folder_lower in common_folders:
                path = common_folders[folder_lower]
                if os.path.exists(path):
                    os.startfile(path)
                    return True

            # Try provided folder paths
            for path_template in folder_paths:
                path = os.path.expandvars(path_template)
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    os.startfile(path)
                    return True

            # Fallback: use file search to find folder
            from services.file_service import FileService
            file_service = FileService(self.config)
            results = file_service.search_files(folder_name)
            folders = [r for r in results if r['type'] == 'folder']

            if folders:
                os.startfile(folders[0]['path'])
                print(f"✅ Found and opened: {folders[0]['path']}")
                return True

            # Final fallback: try direct path
            if os.path.exists(folder_name):
                os.startfile(folder_name)
                return True

        elif self.os_type == "Darwin":
            # macOS
            for path in folder_paths:
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    subprocess.run(['open', path])
                    return True

        elif self.os_type == "Linux":
            # Linux
            for path in folder_paths:
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    subprocess.run(['xdg-open', path])
                    return True

        return False

    def execute_system_command(self, command):
        """
        Execute a system command

        Args:
            command (str): Command to execute

        Returns:
            dict: Result of command execution
        """
        try:
            if self.os_type == "Windows":
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True
                )

            return {
                'success': True,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_system_info(self):
        """
        Get system information

        Returns:
            dict: System information
        """
        info = {
            'os': self.os_type,
            'platform': platform.platform(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'installed_apps_count': len(self.installed_apps_cache)
        }

        if self.os_type == "Windows":
            info.update({
                'windows_version': platform.win32_ver(),
                'computer_name': os.environ.get('COMPUTERNAME', 'Unknown'),
                'user_name': os.environ.get('USERNAME', 'Unknown')
            })

        return info

    def update_installed_apps_cache(self):
        """Refresh the installed applications cache"""
        if self.os_type == "Windows":
            print("🔄 Refreshing installed applications cache...")
            self.installed_apps_cache = self.get_windows_installed_apps()
            print(f"✅ Updated cache with {len(self.installed_apps_cache)} applications")
            return True
        return False

    def get_installed_apps_list(self, limit=None):
        """
        Get list of installed applications

        Args:
            limit (int, optional): Maximum number of apps to return

        Returns:
            list: List of application information
        """
        apps = []
        for key, value in self.installed_apps_cache.items():
            apps.append({
                'name': value['name'],
                'path': value['path'],
                'source': value.get('source', 'unknown')
            })
            if limit and len(apps) >= limit:
                break
        return apps

    def is_admin(self):
        """
        Check if the current process has administrator privileges

        Returns:
            bool: True if running as administrator
        """
        try:
            if self.os_type == "Windows":
                return win32api.ShellExecuteW(
                    None, "runas", 'cmd', '/c net session > nul 2>&1', None, 1
                ) > 32
            else:
                return os.geteuid() == 0
        except:
            return False