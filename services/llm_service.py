import requests
import json


class LLMService:
    """Handles LLM API communication for JARVIS AI"""

    def __init__(self, config):
        """
        Initialize LLM service

        Args:
            config: Configuration object with LLM settings
        """
        self.config = config
        self.llm_config = config.get_llm_config()

    def call_api(self, messages, use_vision=False, preserve_reasoning=False):
        """
        Universal OpenAI-compatible API caller

        Args:
            messages (list): List of message dictionaries
            use_vision (bool): Whether to use vision model
            preserve_reasoning (bool): Whether to preserve reasoning details

        Returns:
            str or dict: API response content or reasoning details
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.llm_config['api_key']}",
                "Content-Type": "application/json",
            }

            # Choose appropriate model
            model = self.llm_config['vision_model'] if use_vision else self.llm_config['model']

            payload = {
                "model": model,
                "messages": messages,
            }

            # Add reasoning support for OpenRouter
            if self.llm_config['enable_reasoning'] and self.llm_config['provider'] == 'openrouter':
                payload["extra_body"] = {"reasoning": {"enabled": True}}

            # Make API call
            response = requests.post(
                url=f"{self.llm_config['api_base']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # Extract response
            message = result['choices'][0]['message']
            content = message.get('content', '')

            # Preserve reasoning details if enabled
            if preserve_reasoning and 'reasoning_details' in message:
                return {
                    'content': content,
                    'reasoning_details': message['reasoning_details']
                }

            return content

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def analyze_screen_with_vision(self, user_query, base64_image):
        """
        Use OpenAI Vision API to analyze screen

        Args:
            user_query (str): User's query about the screen
            base64_image (str): Base64 encoded screenshot

        Returns:
            dict: Vision analysis result with action and position
        """
        try:
            prompt = f"""Analyze this screenshot and help with: "{user_query}"

Respond with JSON ONLY:
{{
    "action": "CLICK" | "INFORMATION" | "NOT_FOUND",
    "target_description": "what to interact with",
    "approximate_position": {{"x": percent_x, "y": percent_y}},
    "confidence": "high" | "medium" | "low",
    "reasoning": "what you found",
    "response": "user message"
}}

For clicks: provide x,y as percentages (0-100) of screen size.
For information: describe what you see."""

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            response = self.call_api(messages, use_vision=True)

            if response:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))

                # Fallback if no JSON found
                return {"action": "INFORMATION", "response": response}

            return None

        except Exception as e:
            print(f"Vision analysis error: {e}")
            return None

    def update_config(self, new_config):
        """
        Update LLM configuration

        Args:
            new_config (dict): New configuration values
        """
        for key, value in new_config.items():
            if key in self.llm_config:
                self.llm_config[key] = value

        # Update config object as well
        if 'api_key' in new_config:
            self.config.LLM_API_KEY = new_config['api_key']
        if 'api_base' in new_config:
            self.config.LLM_API_BASE = new_config['api_base']
        if 'model' in new_config:
            self.config.LLM_MODEL = new_config['model']
        if 'vision_model' in new_config:
            self.config.LLM_VISION_MODEL = new_config['vision_model']
        if 'provider' in new_config:
            self.config.LLM_PROVIDER = new_config['provider']
        if 'enable_reasoning' in new_config:
            self.config.LLM_ENABLE_REASONING = new_config['enable_reasoning']

    def get_config(self, safe=True):
        """
        Get current LLM configuration

        Args:
            safe (bool): Whether to hide sensitive information like API keys

        Returns:
            dict: Current configuration
        """
        config = self.llm_config.copy()
        if safe and config.get('api_key'):
            # Show only first 8 characters of API key
            config['api_key'] = config['api_key'][:8] + '...'
        return config

    def is_configured(self):
        """
        Check if LLM service is properly configured

        Returns:
            bool: True if API key is set and not a placeholder
        """
        api_key = self.llm_config.get('api_key', '')
        return bool(api_key and api_key != 'YOUR_API_KEY_HERE' and len(api_key) > 10)