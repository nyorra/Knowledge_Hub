"""
Audio transcription service using OpenAI Whisper API.
"""

import asyncio
import tempfile
from pathlib import Path

from fastapi import UploadFile
from openai import OpenAI

from app.core.logger import logger
from app.core.settings import settings


class TranscriptionService:
    """Handles audio-to-text transcription via Whisper API."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=30.0,
            max_retries=2,
        )

    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_file: Uploaded audio file (mp3, wav, webm, m4a, etc.)

        Returns:
            Transcribed text

        Raises:
            ValueError: If transcription fails
        """
        logger.info(f"Starting transcription for: {audio_file.filename}")

        try:
            content = await audio_file.read()

            if len(content) == 0:
                raise ValueError("Audio file is empty")

            suffix = Path(audio_file.filename).suffix or ".webm"

            def _transcribe_sync():
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name

                try:
                    with open(tmp_path, "rb") as audio:
                        response = self.client.audio.transcriptions.create(
                            model="whisper-large-v3-turbo",  # Updated model name
                            file=audio,
                            response_format="text",
                        )

                    return response if isinstance(response, str) else response.text
                finally:
                    Path(tmp_path).unlink(missing_ok=True)

            text = await asyncio.to_thread(_transcribe_sync)

            if not text or not text.strip():
                raise ValueError("Transcription returned empty text")

            logger.info(f"✓ Transcription complete: {len(text)} chars")
            return text.strip()

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise ValueError(f"Failed to transcribe audio: {str(e)}")


transcription_service = TranscriptionService()
