import os
import logging
from typing import Dict, Any, Optional
from faster_whisper import WhisperModel

logger = logging.getLogger("oncovault_whisper")

class WhisperService:
    _instance: Optional["WhisperService"] = None

    def __init__(self, model_size: Optional[str] = None, device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size or os.getenv("WHISPER_MODEL", "small.en")
        self.device = device
        self.compute_type = compute_type
        self.model: Optional[WhisperModel] = None
        self._load_model()

    @classmethod
    def get_instance(cls) -> "WhisperService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self) -> None:
        try:
            logger.info(f"Loading Whisper model '{self.model_size}' on {self.device} ({self.compute_type})...")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=2,
            )
            logger.info(f"Whisper model '{self.model_size}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
            raise RuntimeError(f"Could not initialize Whisper speech-to-text engine: {e}")

    def transcribe(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found at path: {audio_path}")

        file_size = os.path.getsize(audio_path)
        if file_size < 100:
            raise ValueError("Audio file is empty or corrupted (file size too small).")

        if self.model is None:
            self._load_model()

        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                temperature=0.0,
                condition_on_previous_text=False,
                repetition_penalty=1.15,
                no_speech_threshold=0.6,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=400, speech_pad_ms=300),
            )

            text_segments = [seg.text.strip() for seg in segments if seg.text.strip()]
            full_transcript = " ".join(text_segments).strip()

            return {
                "success": True,
                "transcript": full_transcript,
                "language": info.language if info else language,
                "language_probability": getattr(info, "language_probability", 1.0),
                "duration": getattr(info, "duration", 0.0),
                "model": self.model_size,
            }
        except Exception as e:
            logger.error(f"Transcription error on file {audio_path}: {e}")
            raise RuntimeError(f"Whisper transcription failed: {str(e)}")
