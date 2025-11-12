from flask import Blueprint, request, jsonify

vision_bp = Blueprint('vision', __name__)


def get_jarvis():
    """Get JARVIS instance from Flask app"""
    from flask import current_app
    return current_app.config.get('JARVIS_INSTANCE')


@vision_bp.route('/api/screen', methods=['GET'])
def get_screen():
    """
    Get current screen capture

    Returns:
    {
        "success": true/false,
        "image": "base64_encoded_image",
        "width": screen_width,
        "height": screen_height
    }
    """
    try:
        # Get jarvis instance
        jarvis = get_jarvis()
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Capture screen
        screenshot = jarvis.vision_module.capture_screen()
        if not screenshot:
            return jsonify({
                'success': False,
                'error': 'Screen capture failed'
            }), 500

        # Convert to base64
        img_base64 = jarvis.vision_module.image_to_base64(screenshot)
        if not img_base64:
            return jsonify({
                'success': False,
                'error': 'Image conversion failed'
            }), 500

        # Get screen dimensions
        width, height = jarvis.vision_module.get_screen_size()

        return jsonify({
            'success': True,
            'image': img_base64,
            'width': width,
            'height': height
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Screen capture error: {str(e)}'
        }), 500


@vision_bp.route('/api/screen/analyze', methods=['POST'])
def analyze_screen():
    """
    Analyze screen with vision AI

    Expected payload:
    {
        "query": "what to analyze on screen"
    }

    Returns:
    {
        "success": true/false,
        "analysis": {...},
        "response": "analysis result"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        query = data.get('query', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400

        # Get jarvis instance
        jarvis = get_jarvis()
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Capture screen
        screenshot = jarvis.vision_module.capture_screen()
        if not screenshot:
            return jsonify({
                'success': False,
                'error': 'Screen capture failed'
            }), 500

        # Convert to base64
        img_base64 = jarvis.vision_module.image_to_base64(screenshot)
        if not img_base64:
            return jsonify({
                'success': False,
                'error': 'Image conversion failed'
            }), 500

        # Analyze with vision
        analysis = jarvis.llm_service.analyze_screen_with_vision(query, img_base64)
        if not analysis:
            return jsonify({
                'success': False,
                'error': 'Vision analysis failed'
            }), 500

        return jsonify({
            'success': True,
            'analysis': analysis,
            'response': analysis.get('response', 'Analysis completed')
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Screen analysis error: {str(e)}'
        }), 500


@vision_bp.route('/api/screen/click', methods=['POST'])
def click_screen():
    """
    Click on screen at specified position

    Expected payload:
    {
        "x": x_percent,
        "y": y_percent
    }

    Returns:
    {
        "success": true/false,
        "position": {"x": actual_x, "y": actual_y}
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        x_percent = data.get('x')
        y_percent = data.get('y')

        if x_percent is None or y_percent is None:
            return jsonify({
                'success': False,
                'error': 'x and y coordinates are required'
            }), 400

        # Get jarvis instance
        jarvis = get_jarvis()
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Get screen size to calculate actual coordinates
        screen_width, screen_height = jarvis.vision_module.get_screen_size()
        actual_x = int(screen_width * x_percent / 100)
        actual_y = int(screen_height * y_percent / 100)

        # Perform click
        success = jarvis.vision_module.click_screen_position(x_percent, y_percent)

        return jsonify({
            'success': success,
            'position': {'x': actual_x, 'y': actual_y}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Click error: {str(e)}'
        }), 500


@vision_bp.route('/api/search-files', methods=['POST'])
def search_files():
    """
    Search for files and folders

    Expected payload:
    {
        "query": "search terms",
        "file_type": "optional_file_extension",
        "max_results": 50
    }

    Returns:
    {
        "success": true,
        "results": [...]
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        query = data.get('query', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'No search query provided'
            }), 400

        file_type = data.get('file_type')
        max_results = data.get('max_results', 50)

        # Get jarvis instance
        jarvis = get_jarvis()
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Perform search
        results = jarvis.file_service.search_files(query, file_type, max_results)

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'File search error: {str(e)}'
        }), 500


@vision_bp.route('/api/youtube-search', methods=['POST'])
def youtube_search():
    """
    Search YouTube and return video links

    Expected payload:
    {
        "query": "search terms",
        "limit": 5
    }

    Returns:
    {
        "success": true,
        "videos": [...]
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        query = data.get('query', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'No search query provided'
            }), 400

        limit = data.get('limit', 5)

        # Get jarvis instance
        jarvis = get_jarvis()
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Perform YouTube search
        videos = jarvis.youtube_service.search_youtube_api(query, limit)

        return jsonify({
            'success': True,
            'videos': videos
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'YouTube search error: {str(e)}'
        }), 500


@vision_bp.route('/api/file-info', methods=['POST'])
def get_file_info():
    """
    Get detailed information about a file

    Expected payload:
    {
        "path": "file_path"
    }

    Returns:
    {
        "success": true/false,
        "info": {...}
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        file_path = data.get('path', '')
        if not file_path:
            return jsonify({
                'success': False,
                'error': 'No file path provided'
            }), 400

        # Get jarvis instance
        jarvis = get_jarvis()
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Get file information
        file_info = jarvis.file_service.get_file_info(file_path)

        if not file_info:
            return jsonify({
                'success': False,
                'error': 'File not found or cannot access'
            }), 404

        return jsonify({
            'success': True,
            'info': file_info
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'File info error: {str(e)}'
        }), 500