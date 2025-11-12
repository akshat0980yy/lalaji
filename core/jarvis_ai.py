import webbrowser
from urllib.parse import quote

from core.voice_module import VoiceModule
from core.vision_module import VisionModule
from core.command_engine import CommandEngine
from services.llm_service import LLMService
from services.youtube_service import YouTubeService
from services.file_service import FileService
from services.system_service import SystemService
from utils.logger import logger


class JarvisAI:
    """Main JARVIS AI class - Central coordinator for all modules"""

    def __init__(self, use_voice=True):
        """
        Initialize JARVIS AI with all subsystems

        Args:
            use_voice (bool): Whether to enable voice functionality
        """
        # Import config here to avoid circular imports
        from config.settings import config
        self.config = config

        # Initialize logger
        self.logger = logger

        # Initialize context
        self.context = {
            'last_browser_tab': None,
            'last_app': None,
            'conversation_history': [],
            'screen_elements': [],
            'last_search_results': []
        }

        # Initialize core modules
        self.voice_module = VoiceModule(self.config) if use_voice else None
        self.vision_module = VisionModule(self.config)
        self.llm_service = LLMService(self.config)
        self.command_engine = CommandEngine(self.config, self.llm_service)

        # Initialize service modules
        self.youtube_service = YouTubeService(self.config)
        self.file_service = FileService(self.config)
        self.system_service = SystemService(self.config)

        # Update command engine with installed apps cache
        self.command_engine.update_installed_apps_cache(self.system_service.installed_apps_cache)

        # Log initialization
        self.logger.info("🤖 Jarvis AI initialized with COMPLETE SYSTEM CONTROL!")
        self.logger.info("👁️ Vision | ⌨️ Typing | 🔍 File Search | 🖱️ Mouse Control | 🎵 YouTube Direct Play")

        # Print startup info to console
        print("🤖 Jarvis AI initialized with COMPLETE SYSTEM CONTROL!")
        print("👁️ Vision | ⌨️ Typing | 🔍 File Search | 🖱️ Mouse Control | 🎵 YouTube Direct Play")

    def speak(self, text):
        """
        Speak text using voice module

        Args:
            text (str): Text to speak

        Returns:
            str: The text that was spoken
        """
        if self.voice_module:
            return self.voice_module.speak(text)
        else:
            print(f"Jarvis: {text}")
            return text

    def analyze_screen_with_vision(self, user_query):
        """
        Use OpenAI Vision API to analyze screen

        Args:
            user_query (str): Query about the screen

        Returns:
            dict: Vision analysis result
        """
        try:
            screenshot = self.vision_module.capture_screen()
            if not screenshot:
                return None

            img_base64 = self.vision_module.image_to_base64(screenshot)
            return self.llm_service.analyze_screen_with_vision(user_query, img_base64)

        except Exception as e:
            self.logger.error(f"Vision analysis error: {e}")
            return None

    def click_screen_position(self, x_percent, y_percent):
        """Click at screen position given as percentages"""
        return self.vision_module.click_screen_position(x_percent, y_percent)

    def search_files(self, query, file_type=None, max_results=50):
        """Search for files and folders in user directory"""
        return self.file_service.search_files(query, file_type, max_results)

    def open_file(self, file_path):
        """Open a file or folder with default application"""
        return self.file_service.open_file(file_path)

    def get_proper_url(self, website_input):
        """Use LLM to intelligently construct proper URL"""
        return self.command_engine.get_proper_url(website_input)

    def llm_interpret_command(self, user_command):
        """Enhanced LLM interpretation with all system controls"""
        return self.command_engine.llm_interpret_command(user_command)

    def open_folder(self, folder_name, folder_paths):
        """Open folder with enhanced path detection"""
        return self.system_service.open_folder(folder_name, folder_paths)

    def smart_find_and_open_app(self, app_name, executable_hints):
        """Enhanced app opening"""
        return self.system_service.smart_find_and_open_app(app_name, executable_hints)

    def search_web(self, query):
        """Search the web"""
        search_url = f"https://www.google.com/search?q={quote(query)}"
        webbrowser.open(search_url)
        self.context['last_browser_tab'] = 'search'

    def youtube_search(self, query):
        """Search YouTube"""
        self.youtube_service.search_youtube(query)
        self.context['last_browser_tab'] = 'youtube'

    def play_youtube_video(self, query):
        """Play YouTube video directly using yt-dlp"""
        success = self.youtube_service.play_youtube_video(query)
        if success:
            self.context['last_browser_tab'] = 'youtube_video'
        return success

    def open_website(self, site_input):
        """Open specific websites with intelligent URL construction"""
        url = self.get_proper_url(site_input)
        webbrowser.open(url)
        self.context['last_browser_tab'] = site_input
        return url

    def process_command(self, command):
        """
        Complete command processing with all features

        Args:
            command (str): User command to process

        Returns:
            dict: Command result
        """
        if not command:
            return {'success': False, 'response': 'No command received'}

        command_lower = command.lower()

        if any(word in command_lower for word in ['exit', 'quit', 'goodbye']):
            response = self.speak("Goodbye!")
            return {'success': True, 'response': response, 'action': 'exit'}

        self.logger.info(f"🧠 Analyzing command: {command}")
        interpretation = self.llm_interpret_command(command)

        if not interpretation:
            response = self.speak("I couldn't understand that.")
            return {'success': False, 'response': response}

        self.logger.info(f"💭 Reasoning: {interpretation.get('reasoning', 'N/A')}")

        action = interpretation.get('action', 'CONVERSATION')
        target = interpretation.get('target', '')
        ai_response = interpretation.get('response', '')
        executable_hints = interpretation.get('executable_hints', [])
        folder_paths = interpretation.get('folder_paths', [])
        params = interpretation.get('params', {})

        # Execute action
        if action == "SCROLL":
            direction = params.get('direction', target)
            amount = params.get('amount', 3)
            success = self.vision_module.scroll_action(direction, amount)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'scroll'}

        elif action == "TYPE_TEXT":
            success = self.vision_module.type_text(target)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'type'}

        elif action == "PRESS_KEY":
            key = params.get('key', target)
            success = self.vision_module.press_key(key)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'keypress'}

        elif action == "SEARCH_FILES":
            file_type = params.get('file_type', None)
            results = self.search_files(target, file_type)

            if results:
                folders = [r for r in results if r['type'] == 'folder']
                files = [r for r in results if r['type'] == 'file']

                result_text = f"Found {len(results)} results:\n"
                if folders:
                    result_text += f"\nFolders ({len(folders)}):\n"
                    for i, res in enumerate(folders[:3], 1):
                        result_text += f"{i}. 📁 {res['name']}\n"
                if files:
                    result_text += f"\nFiles ({len(files)}):\n"
                    for i, res in enumerate(files[:3], 1):
                        result_text += f"{i}. 📄 {res['name']}\n"

                response = self.speak(f"Found {len(folders)} folders and {len(files)} files.")
                return {
                    'success': True,
                    'response': response,
                    'action': 'search_files',
                    'results': results
                }
            else:
                response = self.speak("No files or folders found.")
                return {'success': False, 'response': response}

        elif action == "OPEN_FILE":
            if target.isdigit() and self.context['last_search_results']:
                idx = int(target) - 1
                if 0 <= idx < len(self.context['last_search_results']):
                    file_path = self.context['last_search_results'][idx]['path']
                    success = self.open_file(file_path)
                    response = self.speak(f"Opening {self.file_service.get_file_info(file_path).get('name', 'file')}")
                    return {'success': success, 'response': response, 'action': 'open_file'}
            else:
                results = self.search_files(target)
                if results:
                    success = self.open_file(results[0]['path'])
                    response = self.speak(f"Opening {results[0]['name']}")
                    return {'success': success, 'response': response, 'action': 'open_file'}

            response = self.speak("File not found.")
            return {'success': False, 'response': response}

        elif action == "OPEN_APP":
            success = self.smart_find_and_open_app(target, executable_hints)
            response = self.speak(ai_response if success else f"Couldn't find {target}")
            return {'success': success, 'response': response, 'action': 'open_app'}

        elif action == "OPEN_FOLDER":
            success = self.open_folder(target, folder_paths)
            response = self.speak(ai_response if success else f"Couldn't find {target} folder")
            return {'success': success, 'response': response, 'action': 'open_folder'}

        elif action == "SCREEN_CLICK":
            self.speak("Analyzing screen...")
            vision_result = self.analyze_screen_with_vision(command)

            if vision_result and vision_result.get('action') == 'CLICK':
                pos = vision_result.get('approximate_position', {})
                if pos:
                    success = self.click_screen_position(pos['x'], pos['y'])
                    response = self.speak(vision_result.get('response', 'Clicked'))
                    return {'success': success, 'response': response, 'action': 'click'}

            response = self.speak("Couldn't identify click target.")
            return {'success': False, 'response': response}

        elif action == "SCREEN_ANALYZE":
            self.speak("Analyzing screen...")
            vision_result = self.analyze_screen_with_vision(command)

            if vision_result:
                response = self.speak(vision_result.get('response', 'Screen analyzed'))
                return {'success': True, 'response': response, 'action': 'analyze'}

            response = self.speak("Couldn't analyze screen.")
            return {'success': False, 'response': response}

        elif action == "SEARCH_WEB":
            self.search_web(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'search'}

        elif action == "SEARCH_YOUTUBE":
            self.youtube_search(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'youtube'}

        elif action == "PLAY_YOUTUBE":
            success = self.play_youtube_video(target)
            response = self.speak(ai_response if success else f"Couldn't play {target}")
            return {'success': success, 'response': response, 'action': 'play_youtube'}

        elif action == "OPEN_WEBSITE":
            url = self.open_website(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'website', 'url': url}

        elif action == "CONVERSATION":
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'conversation'}

        elif action == "SYSTEM_COMMAND":
            result = self.system_service.execute_system_command(target)
            response = self.speak(ai_response if result['success'] else f"Error: {result.get('error', 'Unknown error')}")
            return {'success': result['success'], 'response': response, 'action': 'system'}

        else:
            response = self.speak("I'm not sure how to handle that.")
            return {'success': False, 'response': response}

    def get_status(self):
        """Get current JARVIS status"""
        return {
            'status': 'online',
            'context': self.context,
            'voice_enabled': self.voice_module.is_available() if self.voice_module else False,
            'llm_configured': self.llm_service.is_configured(),
            'indexed_apps': len(self.system_service.installed_apps_cache),
            'search_locations': self.file_service.search_locations
        }