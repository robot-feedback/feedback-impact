
import os
import io
from gtts import gTTS
from playsound import playsound
from google.cloud import texttospeech
from config.config import (
    GOOGLE_CREDENTIALS_PATH, TTS_LANGUAGE, TTS_VOICE_NAME,
    TEMP_AUDIO_FILE, OUTPUT_AUDIO_FILE
)

class TTSHandler:
    """Handles text-to-speech functionality"""

    def __init__(self):
        """Initialize TTS handler"""
        pass

    def speak_with_gtts(self, text):
        """
        Convert text to speech using gTTS (Google Text-to-Speech)

        Args:
            text (str): Text to convert to speech

        Raises:
            Exception: If TTS conversion or playback fails
        """
        try:
            print("Debug log: Using gTTS for TTS...")

            tts = gTTS(text=text, lang='en')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # Save to temporary file
            with open(TEMP_AUDIO_FILE, "wb") as f:
                f.write(audio_buffer.read())

            # Play the audio
            playsound(TEMP_AUDIO_FILE)

            # Clean up temporary file
            if os.path.exists(TEMP_AUDIO_FILE):
                os.remove(TEMP_AUDIO_FILE)

        except Exception as e:
            print(f"gTTS Error: {e}")
            raise e

    def speak_with_google_cloud(self, text):
        """
        Convert text to speech using Google Cloud Text-to-Speech

        Args:
            text (str): Text to convert to speech

        Raises:
            Exception: If TTS conversion or playback fails
        """
        try:
            # Set Google Cloud credentials
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH

            # Initialize client
            client = texttospeech.TextToSpeechClient()

            # Set input text
            input_text = texttospeech.SynthesisInput(text=text)

            # Build voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=TTS_LANGUAGE,
                name=TTS_VOICE_NAME
            )

            # Select audio file format
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # Perform text-to-speech request
            response = client.synthesize_speech(
                input=input_text,
                voice=voice,
                audio_config=audio_config
            )

            # Save audio to file
            with open(OUTPUT_AUDIO_FILE, "wb") as out:
                out.write(response.audio_content)
                print("Playing audio")

            # Play the audio
            playsound(OUTPUT_AUDIO_FILE)

            # Clean up audio file
            if os.path.exists(OUTPUT_AUDIO_FILE):
                os.remove(OUTPUT_AUDIO_FILE)

        except Exception as e:
            print(f"Google Cloud TTS Error: {e}")
            raise e

    def speak(self, text, use_google_cloud=False):
        """
        Convert text to speech using preferred TTS engine

        Args:
            text (str): Text to convert to speech
            use_google_cloud (bool): If True, use Google Cloud TTS; otherwise use gTTS

        Raises:
            Exception: If TTS conversion or playback fails
        """
        try:
            if use_google_cloud:
                self.speak_with_google_cloud(text)
            else:
                self.speak_with_gtts(text)
        except Exception as e:
            print(f"TTS Error: {e}")
            # Fallback to the other TTS method
            try:
                if use_google_cloud:
                    print("Falling back to gTTS...")
                    self.speak_with_gtts(text)
                else:
                    print("Falling back to Google Cloud TTS...")
                    self.speak_with_google_cloud(text)
            except Exception as fallback_error:
                print(f"Fallback TTS also failed: {fallback_error}")
                raise fallback_error