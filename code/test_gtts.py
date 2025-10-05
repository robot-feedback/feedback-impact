
from gtts import gTTS
from playsound import playsound
import os

from google.cloud import texttospeech

json_credentials_path = "radiant-math-436013-g8-5a395a37023e.json"

def text_to_speech_gn(text):

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_credentials_path
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(language_code="en-US",name="en-US-Wavenet-C")
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            print("playing audio")

        playsound("output.mp3")


if __name__ == '__main__':
    feedback = "Feedback testing"
    text_to_speech_gn(feedback)