from flask import Blueprint, request, jsonify

system_bp = Blueprint('system', __name__)


def get_jarvis():
    """Get JARVIS instance from Flask app"""
    from flask import current_app
    return current_app.config.get('JARVIS_INSTANCE')


@system_bp.route('/api/status', methods=['GET'])
def get_status():
    """
    Get system status and JARVIS information

    Returns:
    {
        "status": "online",
        "context": {...},
        "llm_provider": "...",
        "api_base": "...",
        "model": "...",
        "indexed_apps": number,
        "search_locations": [...],
        "features": {...}
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

        # Get system information
        system_info = jarvis.system_service.get_system_info()

        # Get LLM configuration (safe)
        llm_config = jarvis.llm_service.get_config(safe=True)

        status_response = {
            'success': True,
            'status': 'online',
            'context': jarvis.context,
            'llm_provider': llm_config.get('provider'),
            'api_base': llm_config.get('api_base'),
            'model': llm_config.get('model'),
            'indexed_apps': len(jarvis.system_service.installed_apps_cache),
            'search_locations': jarvis.file_service.search_locations,
            'features': {
                'vision': True,
                'typing': True,
                'file_search': True,
                'folder_search': True,
                'scroll': True,
                'keyboard': True,
                'url_intelligence': True,
                'youtube_direct_play': True,
                'youtube_search_python': True,
                'openai_compatible': True,
                'reasoning_support': llm_config.get('enable_reasoning', False),
                'voice_enabled': jarvis.voice_module.is_available() if jarvis.voice_module else False,
                'pywin32': jarvis.config.OS_TYPE == "Windows"
            },
            'system_info': system_info
        }

        return jsonify(status_response)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Status error: {str(e)}'
        }), 500


@system_bp.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """
    Get or update LLM configuration

    GET: Returns current configuration (with API key masked)
    POST: Updates configuration

    POST payload:
    {
        "api_key": "new_api_key",
        "api_base": "new_api_base",
        "model": "new_model",
        "vision_model": "new_vision_model",
        "provider": "new_provider",
        "enable_reasoning": true/false
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

        if request.method == 'POST':
            data = request.json
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400

            # Update LLM service configuration
            jarvis.llm_service.update_config(data)

            # Get updated configuration
            updated_config = jarvis.llm_service.get_config(safe=False)

            return jsonify({
                'success': True,
                'config': updated_config,
                'message': 'Configuration updated successfully'
            })

        else:  # GET
            # Return current configuration with safe defaults
            config = jarvis.llm_service.get_config(safe=True)

            return jsonify({
                'success': True,
                'config': config
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Config error: {str(e)}'
        }), 500


@system_bp.route('/api/apps', methods=['GET'])
def get_installed_apps():
    """
    Get list of installed applications

    Query parameters:
    - limit: Maximum number of apps to return (optional)
    - search: Filter apps by name (optional)

    Returns:
    {
        "success": true,
        "apps": [...],
        "count": number
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

        # Get query parameters
        limit = request.args.get('limit', type=int)
        search_term = request.args.get('search', '').lower()

        # Get installed apps
        apps = jarvis.system_service.get_installed_apps_list(limit)

        # Filter by search term if provided
        if search_term:
            apps = [
                app for app in apps
                if search_term in app['name'].lower()
            ]

        return jsonify({
            'success': True,
            'apps': apps,
            'count': len(apps)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Apps error: {str(e)}'
        }), 500


@system_bp.route('/api/verify-url', methods=['POST'])
def verify_url():
    """
    Verify and get proper URL for a website

    Expected payload:
    {
        "site": "website_name_or_url"
    }

    Returns:
    {
        "success": true,
        "url": "https://www.example.com",
        "input": "original_input"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        site_input = data.get('site', '')
        if not site_input:
            return jsonify({
                'success': False,
                'error': 'No site input provided'
            }), 400

        # Get jarvis instance
        jarvis = get_jarvis()
        if not jarvis:
            return jsonify({
                'success': False,
                'error': 'JARVIS not initialized'
            }), 500

        # Get proper URL
        url = jarvis.command_engine.get_proper_url(site_input)

        return jsonify({
            'success': True,
            'url': url,
            'input': site_input
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'URL verification error: {str(e)}'
        }), 500


@system_bp.route('/api/system-info', methods=['GET'])
def get_detailed_system_info():
    """
    Get detailed system information

    Returns:
    {
        "success": true,
        "system": {...},
        "drives": [...],
        "environment": {...}
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

        # Get system information
        system_info = jarvis.system_service.get_system_info()

        response_data = {
            'success': True,
            'system': system_info
        }

        # Add drive information for Windows
        if jarvis.config.OS_TYPE == "Windows" and jarvis.system_service.windows_utils:
            try:
                drives = jarvis.system_service.windows_utils.get_system_drives()
                drive_info = []
                for drive in drives:
                    info = jarvis.system_service.windows_utils.get_drive_info(drive)
                    drive_info.append(info)
                response_data['drives'] = drive_info
            except Exception as e:
                response_data['drives_error'] = str(e)

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'System info error: {str(e)}'
        }), 500