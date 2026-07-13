# DeskOwn — Core Modules API

## 1. AI Engine (`core/ai_engine.py`)

### Class: `AIEngine`

Manages all LLM interactions via Ollama.

#### Constructor

```python
AIEngine(model: str = None, host: str = None)
```

- `model`: Ollama model name (default from config)
- `host`: Ollama API host (default: `http://localhost:11434`)

#### Methods

##### `chat(message: str) -> str`

Send a message and get a complete response.

```python
response = ai.chat("What is Python?")
print(response)  # "Python is a programming language..."
```

##### `chat_stream(message: str) -> Generator[str, None, None]`

Send a message and yield response tokens as they arrive.

```python
for token in ai.chat_stream("Explain recursion"):
    print(token, end="", flush=True)
```

##### `clear_history()`

Reset conversation history.

```python
ai.clear_history()
```

##### `set_model(model: str)`

Switch to a different Ollama model.

```python
ai.set_model("qwen2.5:7b")
```

##### `get_history() -> list[dict]`

Return current conversation history.

```python
history = ai.get_history()
# [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
```

#### Internal Methods

##### `_build_messages(user_message: str) -> list[dict]`

Construct the message list with system prompt, history, and new message.

##### `_trim_history()`

Remove oldest messages when history exceeds `MAX_HISTORY`.

---

## 2. Voice Engine (`core/voice_engine.py`)

### Class: `VoiceEngine`

Handles speech-to-text and text-to-speech.

#### Constructor

```python
VoiceEngine(stt_model: str = None, tts_voice: str = None)
```

- `stt_model`: Whisper model size (default: "base")
- `tts_voice`: Piper voice (default: "en_US-amy-medium")

#### Methods

##### `transcribe(audio_data: np.ndarray) -> str`

Convert audio array to text.

```python
import numpy as np
audio = np.zeros(16000, dtype=np.float32)  # 1 second silence
text = voice.transcribe(audio)
```

##### `speak(text: str)`

Convert text to speech and play it.

```python
voice.speak("Hello, how can I help you?")
```

##### `record_audio(duration: float = None) -> np.ndarray`

Record audio from microphone. If `duration` is None, records until stopped.

```python
audio = voice.record_audio(duration=5.0)  # Record 5 seconds
```

##### `start_recording()`

Start continuous recording (for push-to-talk).

##### `stop_recording() -> np.ndarray`

Stop recording and return captured audio.

##### `is_recording() -> bool`

Check if currently recording.

#### Internal Methods

##### `_init_stt()`

Initialize faster-whisper model. Called on first use.

##### `_init_tts()`

Initialize piper-tts voice. Called on first use.

##### `_audio_callback(indata, frames, time, status)`

Callback for sounddevice input stream.

---

## 3. Task Runner (`core/task_runner.py`)

### Class: `TaskRunner`

Plugin-based command dispatcher.

#### Constructor

```python
TaskRunner(plugin_dir: str = "plugins")
```

#### Methods

##### `match(command: str) -> Plugin | None`

Find a plugin that matches the command.

```python
plugin = runner.match("open chrome")
if plugin:
    result = plugin.execute("open chrome", {})
```

##### `execute(command: str, context: dict = None) -> str`

Find matching plugin and execute. Returns result text.

```python
result = runner.execute("open notepad")
# "Notepad opened successfully"
```

##### `list_plugins() -> list[dict]`

Return list of available plugins with names and descriptions.

```python
plugins = runner.list_plugins()
# [{"name": "app_launcher", "description": "Open applications"}, ...]
```

##### `reload_plugins()`

Rescan plugin directory and reload all plugins.

#### Internal Methods

##### `_discover_plugins()`

Scan plugin directory, import modules, find Plugin classes.

##### `_match_pattern(command: str, patterns: list[str]) -> bool`

Check if command matches any regex pattern.

---

## 4. System Monitor (`core/system_monitor.py`)

### Class: `SystemMonitor`

Collects real-time system statistics.

#### Constructor

```python
SystemMonitor(interval: float = 2.0)
```

- `interval`: Update interval in seconds

#### Methods

##### `update()`

Refresh all statistics. Called automatically at interval.

##### `get_cpu() -> dict`

```python
monitor.get_cpu()
# {"percent": 45.2, "per_core": [30.1, 60.3, ...], "count": 8}
```

##### `get_memory() -> dict`

```python
monitor.get_memory()
# {"percent": 62.5, "used_gb": 5.0, "total_gb": 8.0, "available_gb": 3.0}
```

##### `get_disk(drive: str = "C:") -> dict`

```python
monitor.get_disk("C:")
# {"percent": 75.3, "used_gb": 120.5, "total_gb": 256.0, "free_gb": 135.5}
```

##### `get_battery() -> dict`

```python
monitor.get_battery()
# {"percent": 85, "power_plugged": True, "seconds_left": None}
```

##### `get_network() -> dict`

```python
monitor.get_network()
# {"bytes_sent": 1234567, "bytes_recv": 7654321, "speed_up": 1024, "speed_down": 2048}
```

##### `get_processes(top_n: int = 5) -> list[dict]`

```python
monitor.get_processes(5)
# [{"pid": 1234, "name": "python.exe", "cpu": 15.2, "memory": 256.0}, ...]
```

##### `get_all() -> dict`

Return all stats combined.

```python
stats = monitor.get_all()
# {"cpu": {...}, "memory": {...}, "disk": {...}, "battery": {...}, "network": {...}, "processes": [...]}
```

##### `start()`

Start automatic updates in background thread.

##### `stop()`

Stop automatic updates.

#### Signals (Qt)

Emitted when stats are updated:

```python
monitor.stats_updated.connect(on_stats_update)
# def on_stats_update(stats: dict): ...
```
