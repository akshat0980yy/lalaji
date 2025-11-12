"""
JARVIS AI Backend - Main Entry Point
Run: python app.py
"""

from flask import Flask, render_template
from flask_cors import CORS

# Import configuration
from config.settings import config

# Import core modules
from core.jarvis_ai import JarvisAI

# Import route blueprints
from routes.command_routes import command_bp
from routes.system_routes import system_bp
from routes.vision_routes import vision_bp

# Import utilities
from utils.logger import logger

# Global jarvis instance
global_jarvis = None


def get_jarvis():
    """Get the global JARVIS instance"""
    return global_jarvis


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    CORS(app)

    # Configure Flask
    app.config['DEBUG'] = config.FLASK_DEBUG
    app.config['SECRET_KEY'] = 'jarvis-ai-secret-key-change-in-production'

    # Initialize JARVIS
    logger.info("🚀 Initializing JARVIS AI...")
    jarvis = JarvisAI(use_voice=False)  # Disable voice for web server mode
    app.config['JARVIS_INSTANCE'] = jarvis

    # Set global instance for routes
    global global_jarvis
    global_jarvis = jarvis

    # Make jarvis available through app context
    app.javis = jarvis

    print(f"✅ Global jarvis set: {global_jarvis is not None}")  # Debug line

    # Register blueprints
    app.register_blueprint(command_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(vision_bp)

    # Main route
    @app.route('/')
    def index():
        """Serve main application page"""
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f"Template error: {e}")
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>JARVIS AI Backend</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #333; text-align: center; margin-bottom: 30px; }
                    .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .api-info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .endpoint { font-family: monospace; background: #f1f1f1; padding: 5px; border-radius: 3px; margin: 5px 0; display: inline-block; }
                    .error { background: #ffe6e6; padding: 15px; border-radius: 5px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 JARVIS AI Backend</h1>

                    <div class="status">
                        <h3>✅ Backend Server is Running</h3>
                        <p>JARVIS AI has been successfully initialized and is ready to accept commands.</p>
                    </div>

                    <div class="api-info">
                        <h3>🔌 Available API Endpoints</h3>
                        <p><strong>Command Processing:</strong></p>
                        <div class="endpoint">POST /api/command</div>

                        <p><strong>Vision & Screen:</strong></p>
                        <div class="endpoint">GET /api/screen</div>
                        <div class="endpoint">POST /api/search-files</div>
                        <div class="endpoint">POST /api/youtube-search</div>

                        <p><strong>System & Configuration:</strong></p>
                        <div class="endpoint">GET /api/status</div>
                        <div class="endpoint">GET/POST /api/config</div>
                        <div class="endpoint">GET /api/apps</div>
                    </div>

                    <div class="error">
                        <h3>⚠️ Frontend Template Missing</h3>
                        <p>The frontend template file <code>templates/index.html</code> was not found.
                        You can still use the API endpoints directly or create the template file.</p>
                    </div>
                </div>
            </body>
            </html>
            """

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Endpoint not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'success': False, 'error': 'Internal server error'}, 500

    return app, jarvis


def display_startup_info(jarvis):
    """Display startup information"""
    print("\n" + "="*70)
    print("🤖 JARVIS AI Backend - Modular Structure")
    print("="*70)
    print("\n⚙️ Configuration:")
    llm_config = jarvis.llm_service.get_config(safe=False)
    print(f"   • Provider: {llm_config.get('provider')}")
    print(f"   • API Base: {llm_config.get('api_base')}")
    print(f"   • Model: {llm_config.get('model')}")
    print(f"   • Vision Model: {llm_config.get('vision_model')}")
    print(f"   • Reasoning: {llm_config.get('enable_reasoning')}")
    print(f"   • API Key: {'✅ Set' if jarvis.llm_service.is_configured() else '❌ Not Set'}")
    print(f"   • Voice: {'✅ Enabled' if jarvis.voice_module and jarvis.voice_module.is_available() else '❌ Disabled'}")

    print("\n✅ Features Active:")
    print("   • OpenAI API Compatible")
    print("   • Screen Vision & Click")
    print("   • Direct YouTube Video Playback (yt-dlp)")
    print("   • Scroll (up/down)")
    print("   • Type Text")
    print("   • Press Keys")
    print("   • File & Folder Search (User Directory)")
    print("   • App/Folder Opening (Enhanced)")
    print("   • Intelligent URL Construction")
    print("   • Modular Backend Structure")

    if jarvis.config.OS_TYPE == "Windows":
        print(f"   • Indexed {len(jarvis.system_service.installed_apps_cache)} Windows Apps")
        print(f"   • Windows-specific Integration")

    print(f"   • Search Locations: {len(jarvis.file_service.search_locations)} directories")

    print("\n💡 API Examples:")
    print("   POST /api/command → Process natural language commands")
    print("   GET /api/status → Get system status")
    print("   GET /api/screen → Capture screen")
    print("   POST /api/search-files → Search files")
    print("   POST /api/youtube-search → Search YouTube")

    print("\n🌐 Server Information:")
    print(f"   • Port: {config.FLASK_PORT}")
    print(f"   • Debug Mode: {config.FLASK_DEBUG}")
    print(f"   • Base URL: http://localhost:{config.FLASK_PORT}")
    print("\n💻 Commands to try:")
    print("   • 'play despacito' → Plays YouTube video")
    print("   • 'open chrome' → Opens Chrome browser")
    print("   • 'find my resume' → Searches files")
    print("   • 'scroll down' → Scrolls screen down")
    print("   • 'type hello world' → Types text")

    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    # Create app and initialize JARVIS
    app, jarvis = create_app()

    # Display startup information
    display_startup_info(jarvis)

    # Start Flask server
    try:
        app.run(
            debug=config.FLASK_DEBUG,
            port=config.FLASK_PORT,
            host='0.0.0.0',
            use_reloader=False  # Prevent multiple initializations
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down JARVIS AI Backend...")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        print(f"❌ Failed to start server: {e}")