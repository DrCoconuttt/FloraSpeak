from google.cloud import texttospeech
from dotenv import load_dotenv
import os

class GoogleTTSManager:
    def __init__(self):
        load_dotenv()

        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_CLOUD_SERVICE_PATH')
        except TypeError:
            exit("Ooops! You forgot to set GOOGLE_APPLICATION_CREDENTIALS in your environment!")
        
        self.client = texttospeech.TextToSpeechClient()
    
    def text_to_audio(self, input_text, voice_name='en-US-Wavenet-D', save_as_wave=False, subdirectory=""):
        synthesis_input = texttospeech.SynthesisInput(text=input_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_name[:5], name=voice_name)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3 if not save_as_wave else texttospeech.AudioEncoding.LINEAR16)
        
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config)
        
        file_extension = "wav" if save_as_wave else "mp3"
        file_name = f"___Msg{str(hash(input_text))}.{file_extension}"
        tts_file = os.path.join(subdirectory, file_name)
        
        with open(tts_file, "wb") as out:
            out.write(response.audio_content)
        
        return tts_file