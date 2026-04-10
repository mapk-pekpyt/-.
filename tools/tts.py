import edge_tts
import asyncio
import pygame
from pydub import AudioSegment
from pydub.effects import low_pass_filter, reverb
import tempfile
import os

async def _speak_async(text, voice="en-GB-SamNeural"):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tmp_path = f.name
        await communicate.save(tmp_path)
    
    # Load and process audio
    audio = AudioSegment.from_mp3(tmp_path)
    # Low-pass filter at 1000Hz for Jarvis effect
    audio = low_pass_filter(audio, 1000)
    # Add reverb
    audio = audio + reverb(audio, decay=0.5)
    
    # Play
    pygame.mixer.init()
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
    
    os.unlink(tmp_path)

def speak(text, voice="en-GB-SamNeural"):
    asyncio.run(_speak_async(text, voice))