try:
    import speech_recognition as sr
except ImportError:
    sr = None
    print("⚠️ SpeechRecognition not available")

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    print("⚠️ pyttsx3 not available")


class VoiceModule:
    """Handles voice synthesis and recognition for JARVIS AI"""

    def __init__(self, config):
        """
        Initialize voice module

        Args:
            config: Configuration object with voice settings
        """
        self.config = config
        self.engine = None
        self.recognizer = None
        self.use_voice = True

        self._initialize_voice()

    def _initialize_voice(self):
        """Initialize speech synthesis and recognition engines"""
        try:
            self.engine = pyttsx3.init()
            voice_config = self.config.get_voice_config()

            self.engine.setProperty('rate', voice_config['rate'])
            self.engine.setProperty('volume', voice_config['volume'])
            self.engine.setProperty('pitch', voice_config['pitch'])

            # Set preferred voice
            voices = self.engine.getProperty('voices')
            male_voice_set = False

            # Try to find preferred voice (David by default)
            for voice in voices:
                if voice_config['preferred_voice'].lower() in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"✅ Selected voice: {voice.name}")
                    male_voice_set = True
                    break

            # Fallback: try any male voice
            if not male_voice_set:
                for voice in voices:
                    if 'male' in voice.name.lower() or (hasattr(voice, 'gender') and voice.gender == 'male'):
                        self.engine.setProperty('voice', voice.id)
                        print(f"✅ Selected voice: {voice.name}")
                        male_voice_set = True
                        break

            # Final fallback: use first voice
            if not male_voice_set and voices:
                self.engine.setProperty('voice', voices[0].id)
                print(f"✅ Selected default voice: {voices[0].name}")

            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True

        except Exception as e:
            print(f"⚠️ Voice module initialization failed: {e}")
            self.use_voice = False

    def speak(self, text):
        """
        Convert text to speech

        Args:
            text (str): Text to speak

        Returns:
            str: The text that was spoken
        """
        print(f"Jarvis: {text}")
        if self.use_voice and self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️ Voice synthesis error: {e}")
        return text

    def listen(self):
        """
        Listen for voice input and convert to text

        Returns:
            str: Recognized text or None if recognition failed
        """
        if not self.use_voice or not self.recognizer:
            return None

        try:
            with sr.Microphone() as source:
                print("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)

            print("🧠 Recognizing...")
            text = self.recognizer.recognize_google(audio)
            print(f"✅ You said: {text}")
            return text

        except sr.UnknownValueError:
            print("❌ Sorry, I didn't catch that.")
            return None
        except sr.RequestError:
            print("❌ Speech recognition service unavailable.")
            return None
        except Exception as e:
            print(f"❌ Voice recognition error: {e}")
            return None

    def is_available(self):
        """Check if voice functionality is available"""
        return self.use_voice and self.engine is not None

    def toggle_voice(self):
        """Toggle voice functionality on/off"""
        self.use_voice = not self.use_voice
        status = "enabled" if self.use_voice else "disabled"
        print(f"🔊 Voice {status}")
        return self.use_voice