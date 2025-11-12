import re


class CommandEngine:
    """Handles natural language command interpretation for JARVIS AI"""

    def __init__(self, config, llm_service, installed_apps_cache=None):
        """
        Initialize command engine

        Args:
            config: Configuration object
            llm_service: LLM service instance for interpretation
            installed_apps_cache: Cache of installed applications
        """
        self.config = config
        self.llm_service = llm_service
        self.installed_apps_cache = installed_apps_cache or {}

    def get_proper_url(self, website_input):
        """
        Use LLM to intelligently construct proper URL

        Args:
            website_input (str): Website name or partial URL

        Returns:
            str: Complete, properly formatted URL
        """
        try:
            prompt = f"""Given the website input: "{website_input}"

Return ONLY a valid, complete URL with proper format.

Rules:
1. Return ONLY the URL, nothing else
2. Must start with https://
3. Use correct domain extension (.com, .org, .net, .io, etc.)
4. For popular sites, use the exact correct URL
5. No www duplication
6. Clean, single URL only

Examples:
Input: "youtube" → Output: https://www.youtube.com
Input: "gmail" → Output: https://mail.google.com
Input: "github" → Output: https://github.com
Input: "reddit" → Output: https://www.reddit.com

Now process: "{website_input}"

Return ONLY the URL:""""

            messages = [{"role": "user", "content": prompt}]
            response = self.llm_service.call_api(messages)

            if response:
                url = response.strip()
                url = re.sub(r'```.*?```', '', url, flags=re.DOTALL)
                url = url.strip()

                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                match = re.search(url_pattern, url)
                if match:
                    url = match.group(0)

                if not url.startswith('http://') and not url.startswith('https://'):
                    url = 'https://' + url

                url = re.sub(r'https?://(https?://)+', 'https://', url)

                print(f"🌐 Constructed URL: {url}")
                return url

            # Fallback to basic URL construction
            if not website_input.startswith('http'):
                return f"https://www.{website_input}.com"
            return website_input

        except Exception as e:
            print(f"URL construction error: {e}")
            # Fallback to basic URL construction
            if not website_input.startswith('http'):
                return f"https://www.{website_input}.com"
            return website_input

    def llm_interpret_command(self, user_command):
        """
        Enhanced LLM interpretation with all system controls

        Args:
            user_command (str): User's natural language command

        Returns:
            dict: Parsed command interpretation with action, target, etc.
        """
        app_names = list(self.installed_apps_cache.keys())[:50] if self.installed_apps_cache else []
        apps_context = ", ".join(app_names) if app_names else "Scanning..."

        system_prompt = f"""You are Jarvis with COMPLETE system control capabilities.

CRITICAL: Respond with VALID JSON only. No markdown, no extra text.

Available Actions:
1. OPEN_APP - Open application
2. OPEN_FOLDER - Open folder
3. SEARCH_WEB - Google search
4. SEARCH_YOUTUBE - YouTube search (search only)
5. PLAY_YOUTUBE - Play YouTube video directly
6. OPEN_WEBSITE - Open website (for specific sites)
7. SCREEN_CLICK - Click on screen
8. SCREEN_ANALYZE - Analyze screen
9. TYPE_TEXT - Type text
10. PRESS_KEY - Press key/combination
11. SCROLL - Scroll up/down
12. SEARCH_FILES - Search files/folders
13. OPEN_FILE - Open specific file/folder
14. CONVERSATION - General chat
15. SYSTEM_COMMAND - Execute command

System: {self.config.OS_TYPE}
Detected Apps: {apps_context}

JSON Format:
{{
    "action": "ACTION_TYPE",
    "target": "target/query",
    "reasoning": "why this action",
    "executable_hints": ["possible", "executables"],
    "folder_paths": ["possible/paths"],
    "params": {{"direction": "up/down", "amount": 3, "key": "enter"}},
    "response": "user message"
}}

CRITICAL YOUTUBE RULES:
1. PLAY_YOUTUBE = When user wants to PLAY/WATCH/LISTEN
   - Keywords: "play", "watch", "listen", "put on"
   - Examples: "play despacito", "watch tutorial", "listen to music"
2. SEARCH_YOUTUBE = ONLY when user explicitly says "search"
3. OPEN_WEBSITE = When opening YouTube homepage: target should be "youtube"

Examples:
"open chrome" → {{"action": "OPEN_APP", "target": "chrome", "response": "Opening Chrome"}}
"play despacito" → {{"action": "PLAY_YOUTUBE", "target": "despacito", "response": "Playing despacito"}}
"open youtube" → {{"action": "OPEN_WEBSITE", "target": "youtube", "response": "Opening YouTube"}}
"scroll down" → {{"action": "SCROLL", "target": "down", "params": {{"direction": "down", "amount": 3}}, "response": "Scrolling"}}

Now interpret: {user_command}"""

        try:
            messages = [{"role": "user", "content": system_prompt}]
            response = self.llm_service.call_api(messages)

            if response:
                response_text = response.strip()
                response_text = re.sub(r'```json\s*|\s*```', '', response_text)

                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))

                # Fallback if JSON parsing fails
                return {
                    "action": "CONVERSATION",
                    "target": "",
                    "reasoning": "Parse error",
                    "executable_hints": [],
                    "folder_paths": [],
                    "params": {},
                    "response": response_text
                }

            return None

        except Exception as e:
            print(f"LLM Error: {e}")
            return None

    def update_installed_apps_cache(self, apps_cache):
        """Update the installed applications cache"""
        self.installed_apps_cache = apps_cache

    def get_available_apps(self):
        """Get list of available applications for context"""
        return list(self.installed_apps_cache.keys())[:20] if self.installed_apps_cache else []