import os
import platform


class Config:
    """Central configuration management for JARVIS AI Backend"""

    # LLM Configuration
    LLM_PROVIDER = 'openrouter'
    LLM_API_KEY = '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'
    LLM_API_BASE = 'https://openrouter.ai/api/v1'
    LLM_MODEL = 'openai/gpt-oss-20b:free'
    LLM_VISION_MODEL = 'gpt-4o'
    LLM_ENABLE_REASONING = True

    # Voice Configuration
    VOICE_RATE = 230
    VOICE_VOLUME = 1.0
    VOICE_PITCH = 1.5
    VOICE_PREFERRED_VOICE = 'david'

    # System Configuration
    OS_TYPE = platform.system()
    FAILSAFE_ENABLED = True
    PYAUTOGUI_PAUSE = 0.5
    PYAUTOGUI_FAILSAFE = True

    # API Configuration
    FLASK_DEBUG = True
    FLASK_PORT = 5000

    # Search Locations Configuration
    @property
    def search_locations(self):
        """Get common file search locations based on OS"""
        locations = []
        if self.OS_TYPE == "Windows":
            user_profile = os.environ.get('USERPROFILE', '')
            locations = [
                user_profile,
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Downloads'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'Music'),
                os.path.join(user_profile, 'OneDrive'),
            ]
        elif self.OS_TYPE == "Darwin":
            home = os.path.expanduser('~')
            locations = [
                home,
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                '/Applications',
            ]
        else:
            home = os.path.expanduser('~')
            locations = [
                home,
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
            ]

        return [loc for loc in locations if os.path.exists(loc)]

    # Environment Variable Overrides
    @classmethod
    def from_env(cls):
        """Load configuration with environment variable overrides"""
        config = cls()

        # LLM Configuration from Environment
        if os.getenv('LLM_PROVIDER'):
            config.LLM_PROVIDER = os.getenv('LLM_PROVIDER')
        if os.getenv('LLM_API_KEY'):
            config.LLM_API_KEY = os.getenv('LLM_API_KEY')
        if os.getenv('LLM_API_BASE'):
            config.LLM_API_BASE = os.getenv('LLM_API_BASE')
        if os.getenv('LLM_MODEL'):
            config.LLM_MODEL = os.getenv('LLM_MODEL')
        if os.getenv('LLM_VISION_MODEL'):
            config.LLM_VISION_MODEL = os.getenv('LLM_VISION_MODEL')
        if os.getenv('LLM_ENABLE_REASONING'):
            config.LLM_ENABLE_REASONING = os.getenv('LLM_ENABLE_REASONING').lower() == 'true'

        # Voice Configuration from Environment
        if os.getenv('VOICE_RATE'):
            config.VOICE_RATE = int(os.getenv('VOICE_RATE'))
        if os.getenv('VOICE_VOLUME'):
            config.VOICE_VOLUME = float(os.getenv('VOICE_VOLUME'))
        if os.getenv('VOICE_PITCH'):
            config.VOICE_PITCH = float(os.getenv('VOICE_PITCH'))
        if os.getenv('VOICE_PREFERRED_VOICE'):
            config.VOICE_PREFERRED_VOICE = os.getenv('VOICE_PREFERRED_VOICE')

        # Flask Configuration from Environment
        if os.getenv('FLASK_DEBUG'):
            config.FLASK_DEBUG = os.getenv('FLASK_DEBUG').lower() == 'true'
        if os.getenv('FLASK_PORT'):
            config.FLASK_PORT = int(os.getenv('FLASK_PORT'))

        return config

    def get_llm_config(self):
        """Get LLM configuration as dictionary"""
        return {
            'provider': self.LLM_PROVIDER,
            'api_key': self.LLM_API_KEY,
            'api_base': self.LLM_API_BASE,
            'model': self.LLM_MODEL,
            'vision_model': self.LLM_VISION_MODEL,
            'enable_reasoning': self.LLM_ENABLE_REASONING
        }

    def get_voice_config(self):
        """Get voice configuration as dictionary"""
        return {
            'rate': self.VOICE_RATE,
            'volume': self.VOICE_VOLUME,
            'pitch': self.VOICE_PITCH,
            'preferred_voice': self.VOICE_PREFERRED_VOICE
        }


# Global configuration instance
config = Config.from_env()