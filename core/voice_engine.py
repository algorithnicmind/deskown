import numpy as np
import sounddevice as sd
import threading

import config


class VoiceEngine:
    def __init__(self):
        self.stt_model = None
        self.tts_model = None
        self.recording = False
        self.audio_frames = []
        self.stream = None

    def _init_stt(self):
        if self.stt_model is not None:
            return
        try:
            from faster_whisper import WhisperModel
            self.stt_model = WhisperModel(
                config.STT_MODEL,
                device=config.STT_DEVICE,
                compute_type="int8",
            )
        except ImportError:
            raise RuntimeError("faster-whisper not installed. Run: pip install faster-whisper")

    def _init_tts(self):
        if self.tts_model is not None:
            return
        try:
            import piper
            self.tts_model = piper.PiperVoice.load(config.TTS_VOICE)
        except ImportError:
            raise RuntimeError("piper-tts not installed. Run: pip install piper-tts")
        except Exception:
            pass

    def transcribe(self, audio_data: np.ndarray) -> str:
        self._init_stt()
        try:
            audio_int16 = (audio_data * 32767).astype(np.int16)
            segments, _ = self.stt_model.transcribe(
                audio_int16,
                language=config.STT_LANGUAGE,
                beam_size=5,
            )
            return " ".join(segment.text for segment in segments)
        except Exception as e:
            return f"Transcription error: {e}"

    def speak(self, text: str):
        self._init_tts()
        try:
            if self.tts_model is not None:
                import io
                import wave

                audio_buffer = io.BytesIO()
                with wave.open(audio_buffer, "wb") as wav_file:
                    self.tts_model.synthesize(text, wav_file)

                audio_buffer.seek(0)
                with wave.open(audio_buffer, "rb") as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    sample_rate = wav_file.getframerate()
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                    audio_float = audio_data.astype(np.float32) / 32767.0
                    sd.play(audio_float, samplerate=sample_rate)
                    sd.wait()
            else:
                self._speak_fallback(text)
        except Exception as e:
            print(f"TTS error: {e}")

    def _speak_fallback(self, text: str):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except ImportError:
            print("No TTS engine available. Install piper-tts or pyttsx3.")

    def start_recording(self):
        self.recording = True
        self.audio_frames = []

        def callback(indata, frames, time_info, status):
            if self.recording:
                self.audio_frames.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            channels=config.CHANNELS,
            dtype=config.AUDIO_DTYPE,
            callback=callback,
        )
        self.stream.start()

    def stop_recording(self) -> np.ndarray:
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if self.audio_frames:
            return np.concatenate(self.audio_frames, axis=0).flatten()
        return np.array([], dtype=np.float32)

    def is_recording(self) -> bool:
        return self.recording

    def list_devices(self) -> list:
        return sd.query_devices()
