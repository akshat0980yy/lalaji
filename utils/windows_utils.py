import os
import platform

# Windows-specific imports
if platform.system() == "Windows":
    import win32com.client
    import winreg
    import win32api
    import win32con


class WindowsUtils:
    """Windows-specific helper functions for JARVIS AI"""

    def __init__(self):
        """Initialize Windows utilities"""
        if platform.system() != "Windows":
            raise RuntimeError("WindowsUtils can only be used on Windows systems")

    def scan_registry_for_apps(self):
        """
        Scan Windows registry for installed applications

        Returns:
            dict: Dictionary of installed applications from registry
        """
        apps = {}

        try:
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]

            for hkey, path in registry_paths:
                try:
                    key = winreg.OpenKey(hkey, path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)

                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                install_location = None

                                # Try to get install location
                                try:
                                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                except FileNotFoundError:
                                    pass

                                # Try to extract from display icon
                                try:
                                    display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                    if display_icon and '.exe' in display_icon.lower():
                                        icon_path = display_icon.split(',')[0].strip('"')
                                        if os.path.exists(icon_path):
                                            install_location = os.path.dirname(icon_path)
                                except (FileNotFoundError, IndexError):
                                    pass

                                # Add to apps dictionary if we have a display name
                                if display_name and display_name not in apps:
                                    apps[display_name.lower()] = {
                                        'name': display_name,
                                        'path': install_location,
                                        'source': 'registry'
                                    }

                            except FileNotFoundError:
                                pass

                            winreg.CloseKey(subkey)
                        except OSError:
                            continue

                    winreg.CloseKey(key)
                except OSError:
                    continue

        except Exception as e:
            print(f"Registry scan error: {e}")

        return apps

    def scan_start_menu_for_apps(self):
        """
        Scan Start Menu for application shortcuts

        Returns:
            dict: Dictionary of applications from Start Menu
        """
        apps = {}

        try:
            start_menu_paths = [
                os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
                os.path.join(os.environ.get('APPDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
            ]

            shell = win32com.client.Dispatch("WScript.Shell")

            for start_path in start_menu_paths:
                if os.path.exists(start_path):
                    for root, dirs, files in os.walk(start_path):
                        for file in files:
                            if file.endswith('.lnk'):
                                try:
                                    shortcut_path = os.path.join(root, file)
                                    shortcut = shell.CreateShortCut(shortcut_path)
                                    target = shortcut.Targetpath

                                    if target and os.path.exists(target):
                                        app_name = file.replace('.lnk', '')
                                        if app_name.lower() not in apps:
                                            apps[app_name.lower()] = {
                                                'name': app_name,
                                                'path': target,
                                                'source': 'start_menu'
                                            }
                                except Exception:
                                    continue

        except Exception as e:
            print(f"Start Menu scan error: {e}")

        return apps

    def get_installed_browsers(self):
        """
        Get list of installed web browsers

        Returns:
            list: List of browser information
        """
        browsers = []
        browser_keys = [
            r"SOFTWARE\Clients\StartMenuInternet",
            r"SOFTWARE\WOW6432Node\Clients\StartMenuInternet"
        ]

        for key_path in browser_keys:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        browser_name = winreg.EnumKey(key, i)
                        try:
                            browser_key = winreg.OpenKey(key, browser_name)
                            try:
                                install_path = winreg.QueryValueEx(browser_key, "InstallLocation")[0]
                                browsers.append({
                                    'name': browser_name,
                                    'path': install_path
                                })
                            except FileNotFoundError:
                                browsers.append({'name': browser_name, 'path': None})
                            finally:
                                winreg.CloseKey(browser_key)
                        except OSError:
                            continue
            except OSError:
                continue

        return browsers

    def get_environment_variables(self):
        """
        Get Windows environment variables

        Returns:
            dict: Environment variables
        """
        return {
            'USERPROFILE': os.environ.get('USERPROFILE', ''),
            'APPDATA': os.environ.get('APPDATA', ''),
            'LOCALAPPDATA': os.environ.get('LOCALAPPDATA', ''),
            'PROGRAMFILES': os.environ.get('PROGRAMFILES', ''),
            'PROGRAMFILES(X86)': os.environ.get('PROGRAMFILES(X86)', ''),
            'PROGRAMDATA': os.environ.get('PROGRAMDATA', ''),
            'TEMP': os.environ.get('TEMP', ''),
            'TMP': os.environ.get('TMP', ''),
            'COMPUTERNAME': os.environ.get('COMPUTERNAME', ''),
            'USERNAME': os.environ.get('USERNAME', ''),
            'USERDOMAIN': os.environ.get('USERDOMAIN', ''),
            'PATH': os.environ.get('PATH', '')
        }

    def is_process_running(self, process_name):
        """
        Check if a process is running

        Args:
            process_name (str): Process name (with or without .exe)

        Returns:
            bool: True if process is running
        """
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower() or \
                   proc.info['name'].lower() == f"{process_name.lower()}.exe":
                    return True
            return False
        except ImportError:
            # Fallback using tasklist
            try:
                result = os.popen(f'tasklist /FI "IMAGENAME eq {process_name}"').read()
                return process_name.lower() in result.lower()
            except:
                return False

    def kill_process(self, process_name):
        """
        Kill a running process

        Args:
            process_name (str): Process name (with or without .exe)

        Returns:
            bool: True if successful
        """
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'].lower() == process_name.lower() or \
                   proc.info['name'].lower() == f"{process_name.lower()}.exe":
                    proc.kill()
                    return True
            return False
        except ImportError:
            # Fallback using taskkill
            try:
                os.system(f'taskkill /F /IM {process_name}')
                return True
            except:
                return False

    def get_system_drives(self):
        """
        Get list of available system drives

        Returns:
            list: List of drive letters
        """
        drives = []
        for drive in win32api.GetLogicalDriveStrings().split('\000')[:-1]:
            if win32api.GetDriveType(drive) != win32con.DRIVE_NO_ROOT_DIR:
                drives.append(drive)
        return drives

    def get_drive_info(self, drive_letter):
        """
        Get information about a specific drive

        Args:
            drive_letter (str): Drive letter (e.g., 'C:')

        Returns:
            dict: Drive information
        """
        try:
            import shutil

            total, used, free = shutil.disk_usage(drive_letter)
            return {
                'drive': drive_letter,
                'total': total,
                'used': used,
                'free': free,
                'total_human': self._format_bytes(total),
                'used_human': self._format_bytes(used),
                'free_human': self._format_bytes(free)
            }
        except Exception as e:
            return {'drive': drive_letter, 'error': str(e)}

    def _format_bytes(self, bytes_value):
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"