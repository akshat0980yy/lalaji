# JARVIS AI Backend - Modular Structure

A comprehensive AI assistant backend with complete system control capabilities, reorganized into a modular, maintainable structure.

## Features

🤖 **AI Capabilities**
- OpenAI/OpenRouter API compatible
- Natural language command interpretation
- Vision analysis with screen understanding
- Intelligent URL construction

🖥️ **System Control**
- Screen capture and vision analysis
- Mouse control (click, scroll)
- Keyboard automation (type, press keys)
- File and folder search operations
- Application launching
- Windows-specific integration

🎵 **Media Integration**
- YouTube direct playback (yt-dlp)
- YouTube search and browse
- Web search capabilities

🔊 **Voice Support**
- Text-to-speech synthesis
- Voice recognition (optional)
- Configurable voice settings

## Architecture

```
backend/
│
├── app.py                 # Main entry point for Flask
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── config/               # Settings & environment variables
│   ├── __init__.py
│   └── settings.py       # Centralized configuration
│
├── core/                 # Core AI logic — JARVIS's "brain"
│   ├── __init__.py
│   ├── jarvis_ai.py      # Main JARVIS coordinator class
│   ├── voice_module.py   # Voice synthesis & recognition
│   ├── vision_module.py  # Screen capture & vision analysis
│   └── command_engine.py # Command interpretation
│
├── routes/               # Flask Blueprints — API endpoints
│   ├── __init__.py
│   ├── command_routes.py # /api/command processing
│   ├── system_routes.py  # /api/status, /api/config, etc.
│   └── vision_routes.py  # /api/screen, /api/search-files, etc.
│
├── services/             # External integrations
│   ├── __init__.py
│   ├── llm_service.py    # LLM API communication
│   ├── youtube_service.py # YouTube integration
│   ├── file_service.py   # File operations
│   └── system_service.py # System control & Windows integration
│
└── utils/                # Helper functions
    ├── __init__.py
    ├── logger.py         # Logging utilities
    ├── windows_utils.py  # Windows-specific helpers
    └── helpers.py        # General utilities
```

## Installation

### Prerequisites

- Python 3.7 or higher
- Operating System: Windows (recommended), macOS, Linux

### Setup

1. **Clone or download the backend files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys** (Optional - default keys included):
   Edit `config/settings.py` or use environment variables:
   ```bash
   export LLM_API_KEY="your-openai-or-openrouter-key"
   export LLM_PROVIDER="openrouter"  # or "openai"
   ```

4. **Start the server:**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## Configuration

### Environment Variables

```bash
# LLM Configuration
LLM_PROVIDER=openrouter
LLM_API_KEY=your-api-key
LLM_API_BASE=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-oss-20b:free
LLM_VISION_MODEL=gpt-4o
LLM_ENABLE_REASONING=true

# Voice Configuration
VOICE_RATE=230
VOICE_VOLUME=1.0
VOICE_PITCH=1.5
VOICE_PREFERRED_VOICE=david

# Flask Configuration
FLASK_DEBUG=true
FLASK_PORT=5000
```

### Configuration File

Edit `config/settings.py` to modify default values. The configuration supports:

- LLM provider settings (OpenAI, OpenRouter, etc.)
- Voice synthesis parameters
- System integration settings
- API endpoint configuration

## API Endpoints

### Command Processing
- `POST /api/command` - Process natural language commands
- `POST /api/voice-command` - Process voice commands (if enabled)

### Vision & Screen
- `GET /api/screen` - Capture current screen
- `POST /api/screen/analyze` - Analyze screen with AI
- `POST /api/screen/click` - Click on screen coordinates
- `POST /api/search-files` - Search files and folders
- `POST /api/youtube-search` - Search YouTube

### System & Configuration
- `GET /api/status` - Get system status and capabilities
- `GET/POST /api/config` - View/update configuration
- `GET /api/apps` - List installed applications (Windows)
- `POST /api/verify-url` - Get proper URL for website

## Usage Examples

### Command Processing

```javascript
// Simple command
POST /api/command
{
  "command": "play despacito"
}

// System control
POST /api/command
{
  "command": "open chrome"
}

// File search
POST /api/command
{
  "command": "find my resume"
}

// Screen interaction
POST /api/command
{
  "command": "scroll down"
}
```

### Vision Analysis

```javascript
POST /api/screen/analyze
{
  "query": "What can I click on this screen?"
}
```

### File Search

```javascript
POST /api/search-files
{
  "query": "resume",
  "file_type": "pdf",
  "max_results": 20
}
```

## Development

### Project Structure

The modular structure separates concerns:

- **Core**: Main AI logic and coordination
- **Services**: External integrations (LLM, YouTube, File System)
- **Routes**: API endpoints organized by functionality
- **Utils**: Helper functions and utilities
- **Config**: Centralized configuration management

### Adding New Features

1. **New Service**: Create in `services/` directory
2. **New API Endpoint**: Add to appropriate route file in `routes/`
3. **New Core Logic**: Add to appropriate core module in `core/`
4. **Configuration**: Add to `config/settings.py`

### Testing

Run the structure test to verify the implementation:
```bash
python test_structure.py
```

## Requirements

### Core Dependencies
- `flask==3.0.0` - Web framework
- `flask-cors==4.0.0` - CORS support
- `requests==2.31.0` - HTTP client
- `openai==1.3.0` - LLM API client

### Voice Dependencies (Optional)
- `pyttsx3==2.90` - Text-to-speech
- `speechrecognition==3.10.0` - Voice recognition

### System Control Dependencies
- `pyautogui==0.9.54` - Screen capture and control
- `Pillow==10.0.1` - Image processing

### Media Dependencies
- `yt-dlp==2023.10.13` - YouTube integration
- `youtubesearchpython==1.7.0` - YouTube search

### Windows Dependencies (Windows only)
- `pywin32==306` - Windows API integration

## Troubleshooting

### Common Issues

1. **Import Errors**: Install missing dependencies with `pip install -r requirements.txt`

2. **Voice Not Working**: Ensure microphone permissions are granted (Linux/macOS)

3. **Screen Capture Issues**: Grant screen recording permissions (macOS) or run as admin (Windows)

4. **Windows Features Not Working**: Install `pywin32` and run as administrator

### Logging

Logs are written to the `logs/` directory and to console. Check logs for detailed error information.

### Performance

- First startup may be slow while indexing installed applications (Windows)
- Vision analysis depends on LLM API response times
- File search performance depends on the size of user directories

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the `logs/` directory
3. Verify all dependencies are installed correctly