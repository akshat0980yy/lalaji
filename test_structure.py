#!/usr/bin/env python3
"""
Test script to verify the modular structure works correctly
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported without errors"""
    print("🧪 Testing module imports...")

    try:
        # Test config
        from config.settings import Config, config
        print("✅ Config module imported successfully")

        # Test core modules
        from core.voice_module import VoiceModule
        print("✅ VoiceModule imported successfully")

        from core.vision_module import VisionModule
        print("✅ VisionModule imported successfully")

        from core.command_engine import CommandEngine
        print("✅ CommandEngine imported successfully")

        # Test service modules
        from services.llm_service import LLMService
        print("✅ LLMService imported successfully")

        from services.youtube_service import YouTubeService
        print("✅ YouTubeService imported successfully")

        from services.file_service import FileService
        print("✅ FileService imported successfully")

        # Test utilities
        from utils.logger import Logger
        print("✅ Logger imported successfully")

        from utils.helpers import Helpers
        print("✅ Helpers imported successfully")

        # Test Windows utils if on Windows
        import platform
        if platform.system() == "Windows":
            try:
                from utils.windows_utils import WindowsUtils
                print("✅ WindowsUtils imported successfully")
            except ImportError as e:
                print(f"⚠️ WindowsUtils import failed (expected on non-Windows): {e}")
        else:
            print("ℹ️ Skipping WindowsUtils on non-Windows system")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")

    try:
        from config.settings import config

        # Test basic config access
        print(f"   • LLM Provider: {config.LLM_PROVIDER}")
        print(f"   • OS Type: {config.OS_TYPE}")
        print(f"   • Search locations: {len(config.search_locations)}")
        print(f"   • Flask Port: {config.FLASK_PORT}")

        # Test LLM config
        llm_config = config.get_llm_config()
        print(f"   • LLM Model: {llm_config.get('model')}")

        # Test voice config
        voice_config = config.get_voice_config()
        print(f"   • Voice Rate: {voice_config.get('rate')}")

        print("✅ Configuration working correctly")
        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without Flask"""
    print("\n🔧 Testing basic functionality...")

    try:
        from config.settings import config
        from services.file_service import FileService
        from services.youtube_service import YouTubeService
        from utils.logger import Logger

        # Test file service
        file_service = FileService(config)
        print(f"   • File service initialized with {len(file_service.search_locations)} search locations")

        # Test YouTube service
        youtube_service = YouTubeService(config)
        print("   • YouTube service initialized")

        # Test logger
        logger = Logger.get_logger("test")
        logger.info("Test log message")
        print("   • Logger working")

        # Test helpers
        from utils.helpers import Helpers
        test_text = Helpers.truncate_text("This is a very long text that should be truncated", 20)
        print(f"   • Text truncation: '{test_text}'")

        print("✅ Basic functionality working")
        return True

    except Exception as e:
        print(f"❌ Basic functionality error: {e}")
        return False

def test_directory_structure():
    """Verify the expected directory structure exists"""
    print("\n📁 Verifying directory structure...")

    expected_dirs = [
        'config',
        'core',
        'services',
        'routes',
        'utils'
    ]

    expected_files = [
        'config/settings.py',
        'config/__init__.py',
        'core/jarvis_ai.py',
        'core/voice_module.py',
        'core/vision_module.py',
        'core/command_engine.py',
        'core/__init__.py',
        'services/llm_service.py',
        'services/youtube_service.py',
        'services/file_service.py',
        'services/system_service.py',
        'services/__init__.py',
        'routes/command_routes.py',
        'routes/system_routes.py',
        'routes/vision_routes.py',
        'routes/__init__.py',
        'utils/logger.py',
        'utils/windows_utils.py',
        'utils/helpers.py',
        'utils/__init__.py',
        'app.py',
        'requirements.txt'
    ]

    all_good = True

    for dir_name in expected_dirs:
        if os.path.isdir(dir_name):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ - Missing")
            all_good = False

    for file_path in expected_files:
        if os.path.isfile(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing")
            all_good = False

    return all_good

def main():
    """Run all tests"""
    print("🚀 JARVIS AI Backend Structure Test")
    print("=" * 50)

    tests = [
        test_directory_structure,
        test_imports,
        test_configuration,
        test_basic_functionality
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! The modular structure is working correctly.")
        print("\n🔥 To start the server:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run the application: python app.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)