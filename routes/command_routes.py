from flask import Blueprint, request, jsonify

command_bp = Blueprint('command', __name__)


def get_jarvis():
    """Get JARVIS instance from app config or global"""
    try:
        # Try to get from app config first
        from flask import current_app
        jarvis = current_app.config.get('JARVIS_INSTANCE')
        if jarvis:
            return jarvis
    except:
        pass

    # Fallback to global instance
    try:
        from app import get_jarvis as get_global_jarvis
        return get_global_jarvis()
    except:
        return None


@command_bp.route('/api/command', methods=['POST'])
def handle_command():
    """
    Process user commands

    Expected payload:
    {
        "command": "user command text"
    }

    Returns:
    {
        "success": true/false,
        "response": "response text",
        "action": "action_type",
        ...additional action-specific data
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        command = data.get('command', '')
        if not command:
            return jsonify({
                'success': False,
                'error': 'No command provided'
            }), 400

        # Get jarvis instance from app context
        jarvis = request.app.config.get('JARVIS_INSTANCE')
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Process the command
        result = jarvis.process_command(command)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Command processing error: {str(e)}'
        }), 500


@command_bp.route('/api/voice-command', methods=['POST'])
def handle_voice_command():
    """
    Handle voice commands (optional endpoint)

    Expected payload:
    {
        "audio_data": "base64_encoded_audio",  # Optional
        "use_microphone": true/false
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        # Get jarvis instance
        jarvis = request.app.config.get('JARVIS_INSTANCE')
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Check if voice is available
        if not jarvis.voice_module or not jarvis.voice_module.is_available():
            return jsonify({
                'success': False,
                'error': 'Voice module not available'
            }), 400

        # Process voice command
        use_microphone = data.get('use_microphone', False)

        if use_microphone:
            # Listen from microphone
            command = jarvis.voice_module.listen()
            if not command:
                return jsonify({
                    'success': False,
                    'error': 'Could not understand voice input'
                })
        else:
            # Process provided text as voice command
            command = data.get('command', '')
            if not command:
                return jsonify({
                    'success': False,
                    'error': 'No command provided'
                }), 400

        # Process the recognized command
        result = jarvis.process_command(command)

        # Add voice response to result
        if result.get('success') and jarvis.voice_module:
            jarvis.voice_module.speak(result.get('response', ''))

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Voice command error: {str(e)}'
        }), 500


@command_bp.route('/api/web-search', methods=['POST'])
def web_search():
    """
    Perform web search

    Expected payload:
    {
        "query": "search terms"
    }
    """
    try:
        data = request.json
        query = data.get('query', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'No search query provided'
            }), 400

        # Get jarvis instance
        jarvis = request.app.config.get('JARVIS_INSTANCE')
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Perform web search
        jarvis.youtube_service.search_youtube(query) if 'youtube' in query.lower() else \
            jarvis.command_engine.get_proper_url(query) and \
            __import__('webbrowser').open(f"https://www.google.com/search?q={__import__('urllib.parse').quote(query)}")

        return jsonify({
            'success': True,
            'response': f'Searching for: {query}',
            'action': 'web_search'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Web search error: {str(e)}'
        }), 500