# DeskOwn — UI Components

## 1. System Tray (`ui/tray.py`)

### Class: `SystemTray`

The system tray icon provides persistent access to DeskOwn.

#### Features

- Custom icon in Windows system tray (bottom-right corner)
- Tooltip showing app name and status
- Right-click context menu
- Double-click to toggle popup window
- Balloon notifications

#### Context Menu Items

| Item | Action |
|---|---|
| Open | Show/hide popup window |
| Voice On/Off | Toggle voice engine |
| Auto-start On/Off | Toggle Windows auto-start |
| About | Show version info |
| Quit | Exit application |

#### Signals

```python
tray.open_requested.connect(show_popup)
tray.quit_requested.connect(app.quit)
tray.voice_toggled.connect(toggle_voice)
tray.autostart_toggled.connect(toggle_autostart)
```

#### Icon Requirements

- Format: `.ico` (Windows icon)
- Sizes: 16x16 (standard tray), 32x32 (high-DPI)
- Should be visible on both light and dark Windows themes

---

## 2. Popup Window (`ui/popup_window.py`)

### Class: `PopupWindow`

The main popup window that appears when triggered.

#### Window Properties

```python
self.setWindowFlags(
    Qt.WindowType.FramelessWindowHint      # No title bar
    | Qt.WindowType.WindowStaysOnTopHint   # Always on top
    | Qt.WindowType.Tool                   # No taskbar entry
)
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
```

#### Appearance

- Rounded corners (12px radius)
- Semi-transparent background (rgba 30, 30, 30, 230)
- White text on dark background
- Modern flat design

#### Positioning

Positions itself near the system tray icon:

```python
def show_near_tray(self):
    tray_geo = self.tray_icon.geometry()
    screen = QApplication.screenAt(tray_geo.center())

    # Default: popup appears above tray
    x = tray_geo.x()
    y = tray_geo.y() - self.height() - 5

    # Keep within screen bounds
    screen_geo = screen.availableGeometry()
    x = max(screen_geo.left(), min(x, screen_geo.right() - self.width()))
    y = max(screen_geo.top(), y)

    self.move(x, y)
```

#### Focus Handling

Auto-hides when losing focus:

```python
QApplication.instance().focusChanged.connect(self._on_focus_changed)

def _on_focus_changed(self, old, new):
    if self.isVisible() and new is None:
        self.hide()
```

#### Layout

```
┌──────────────────────────────────┐
│  [Chat]  [Voice]  [Monitor]     │  ← Tab bar
├──────────────────────────────────┤
│                                  │
│     [Active Tab Content]        │  ← Chat/Voice/Monitor
│                                  │
├──────────────────────────────────┤
│  [Input Field]         [Send]   │  ← Chat input
└──────────────────────────────────┘
```

---

## 3. Chat Widget (`ui/chat_widget.py`)

### Class: `ChatWidget`

Displays conversation history and accepts user input.

#### Message Display

**User Messages:**
```
┌─────────────────────────────────┐
│                        │ Hello  │  ← Right-aligned, blue
│                        │        │
└─────────────────────────────────┘
```

**AI Messages:**
```
┌─────────────────────────────────┐
│ Hi! How can I help │            │  ← Left-aligned, dark gray
│ you today?          │            │
│                     │            │
└─────────────────────────────────┘
```

#### Streaming Display

During AI response generation, text appears token by token:

```python
def on_stream_token(self, token: str):
    self.current_message.append(token)
    self.update_display()
```

#### Markdown Rendering

Supports basic markdown in AI responses:

- `**bold**` → <b>bold</b>
- `*italic*` → <i>italic</i>
- `` `code` `` → <code>code</code>
- ``` ```code block``` ``` → <pre>code block</pre>

#### Input Field

- Single-line text input
- Enter to send
- Shift+Enter for newline
- Send button on the right

#### Scroll Behavior

- Auto-scrolls to bottom on new messages
- User can scroll up to view history
- Scroll bar appears only when needed

---

## 4. Voice Widget (`ui/voice_widget.py`)

### Class: `VoiceWidget`

Controls voice input and displays voice status.

#### Microphone Button

Large circular button in the center:

| State | Appearance |
|---|---|
| Idle | Gray microphone icon |
| Listening | Pulsing red border, "Listening..." text |
| Thinking | Spinning loader, "Thinking..." text |
| Speaking | Animated speaker icon, "Speaking..." text |

#### Usage

1. **Push-to-talk**: Hold button (or Ctrl+Space) to record
2. **Release**: Transcription starts
3. **AI responds**: Response is spoken aloud

#### Status Area

Below the button:
- Transcribed text (what you said)
- AI response text (what was said back)
- Volume level indicator (small bar)

#### Keyboard Shortcut

Default: **Ctrl+Space** (hold to record)

---

## 5. Monitor Widget (`ui/monitor_widget.py`)

### Class: `MonitorWidget`

Displays real-time system statistics.

#### Layout

```
┌──────────────────────────────────┐
│  System Monitor        [Refresh] │
├──────────────────────────────────┤
│  CPU    [████████░░] 45.2%      │
│  RAM    [██████░░░░] 62.5% 5/8G │
│  Disk C:[████████░░] 75.3%      │
│  Battery [████████░░] 85% 🔋    │
├──────────────────────────────────┤
│  Network                        │
│  ↑ 1.2 MB/s   ↓ 3.4 MB/s      │
├──────────────────────────────────┤
│  Top Processes                  │
│  ┌─────┬──────────┬──────┬────┐ │
│  │ PID │ Name     │ CPU% │ RAM│ │
│  ├─────┼──────────┼──────┼────┤ │
│  │ 1234│ python   │ 15.2 │ 256│ │
│  │ 5678│ chrome   │ 12.1 │ 512│ │
│  └─────┴──────────┴──────┴────┘ │
└──────────────────────────────────┘
```

#### Color Coding

- **CPU**: Green (< 50%), Yellow (50-80%), Red (> 80%)
- **RAM**: Green (< 60%), Yellow (60-85%), Red (> 85%)
- **Battery**: Green (> 50%), Yellow (20-50%), Red (< 20%)

#### Auto-Refresh

Updates every 2 seconds (configurable in `config.py`).

#### Kill Process

Right-click a process → "Kill" to terminate it.

---

## 6. Styling

### Color Palette

```python
COLORS = {
    "background": "rgba(30, 30, 30, 230)",
    "surface": "rgba(45, 45, 45, 200)",
    "text": "#ffffff",
    "text_secondary": "#aaaaaa",
    "accent": "#4a9eff",
    "user_bubble": "#4a9eff",
    "ai_bubble": "#3a3a3a",
    "success": "#4caf50",
    "warning": "#ff9800",
    "error": "#f44336",
}
```

### Font

```python
FONT_FAMILY = "Segoe UI"  # Windows default
FONT_SIZE = 14
```

### Stylesheet

Applied to the popup window:

```css
QWidget {
    background-color: rgba(30, 30, 30, 230);
    color: white;
    font-family: 'Segoe UI';
    font-size: 14px;
    border-radius: 12px;
}
QPushButton {
    background-color: #4a9eff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    color: white;
}
QPushButton:hover {
    background-color: #3a8ee6;
}
QLineEdit {
    background-color: rgba(45, 45, 45, 200);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    padding: 8px;
    color: white;
}
```
