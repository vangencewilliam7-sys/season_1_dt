import os
from faster_whisper import WhisperModel
from dotenv import load_dotenv

load_dotenv()

class STTService:
    def __init__(self):
        self.model_size = os.environ.get("WHISPER_MODEL_SIZE", "base")
        self.device = os.environ.get("WHISPER_DEVICE", "cpu")
        # Initialize the model locally
        # int8 is the standard for high-performance CPU inference
        self.model = WhisperModel(
            self.model_size, 
            device=self.device, 
            compute_type="int8" if self.device == "cpu" else "float16"
        )

    def transcribe_audio(self, audio_file_path: str) -> str:
        segments, info = self.model.transcribe(audio_file_path, beam_size=5)
        
        # Merge segments into a single transcript
        text = " ".join([segment.text for segment in segments])
        return text.strip()
